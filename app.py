import os
from functools import wraps

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from nlp import analyze_feedback
from recommender import recommend
from store import Store, now


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "development-only-change-me"),
        MONGODB_URI=os.getenv("MONGODB_URI"),
        MONGODB_DB=os.getenv("MONGODB_DB", "learnloom"),
    )
    if config:
        app.config.update(config)
    try:
        app.store = Store(app.config["MONGODB_URI"], app.config["MONGODB_DB"])
    except Exception:
        app.logger.warning("MongoDB unavailable; using temporary in-memory storage")
        app.store = Store()

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            return view(*args, **kwargs) if session.get("user_id") else redirect(url_for("login"))
        return wrapped

    @app.get("/")
    def index():
        return redirect(url_for("dashboard")) if session.get("user_id") else render_template("landing.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            if app.store.find_one("users", {"email": email}):
                flash("An account already exists for that email.", "error")
            elif len(request.form["password"]) < 8:
                flash("Use at least 8 characters for your password.", "error")
            else:
                user = app.store.insert("users", {
                    "name": request.form["name"].strip(),
                    "email": email,
                    "password": generate_password_hash(request.form["password"]),
                    "interests": request.form.getlist("interests"),
                    "created_at": now(),
                })
                session["user_id"] = user["_id"]
                return redirect(url_for("dashboard"))
        return render_template("auth.html", mode="register")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = app.store.find_one("users", {"email": request.form["email"].strip().lower()})
            if user and check_password_hash(user["password"], request.form["password"]):
                session["user_id"] = user["_id"]
                return redirect(url_for("dashboard"))
            flash("Email or password is incorrect.", "error")
        return render_template("auth.html", mode="login")

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        user = app.store.find_one("users", {"_id": session["user_id"]})
        courses = app.store.find("courses")
        events = app.store.find("events", {"user_id": user["_id"]})
        feedback = app.store.find("feedback", {"user_id": user["_id"]})
        completed = [event for event in events if event["action"] == "completed"]
        minutes = sum(next((course["minutes"] for course in courses if course["_id"] == event["course_id"]), 0) for event in completed)
        return render_template(
            "dashboard.html", user=user, courses=courses, events=events,
            recommendations=recommend(courses, events, user["interests"]),
            completed=len(completed), minutes=minutes,
            engagement=min(100, 42 + len(events) * 7 + len(feedback) * 5),
            feedback=feedback[-3:],
        )

    @app.post("/courses/<course_id>/event")
    @login_required
    def course_event(course_id):
        action = request.form.get("action")
        if action not in {"viewed", "completed"} or not app.store.find_one("courses", {"_id": course_id}):
            return jsonify({"error": "Invalid learning event"}), 400
        score = request.form.get("score", type=int)
        app.store.record_event(session["user_id"], course_id, action, score)
        flash("Progress saved. Your learning path has been refreshed.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/feedback")
    @login_required
    def feedback():
        text = request.form["feedback"].strip()
        if len(text) < 5:
            flash("Please share a little more detail.", "error")
        else:
            result = analyze_feedback(text)
            app.store.insert("feedback", {"user_id": session["user_id"], "text": text, **result, "created_at": now()})
            flash("Thanks — your feedback now shapes future recommendations.", "success")
        return redirect(url_for("dashboard"))

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "database": "mongodb" if app.store.mongo is not None else "memory"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

