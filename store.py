from datetime import datetime, timezone
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, mongo_uri=None, database="learnloom"):
        self.mongo = None
        self.data = {"users": [], "courses": [], "events": [], "feedback": []}
        if mongo_uri:
            from pymongo import MongoClient
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=4000)
            client.admin.command("ping")
            self.mongo = client[database]
        self.seed()

    def collection(self, name):
        return self.mongo[name] if self.mongo is not None else None

    def insert(self, name, document):
        document = {"_id": uuid4().hex, **document}
        collection = self.collection(name)
        if collection is not None:
            collection.insert_one(document)
        else:
            self.data[name].append(document)
        return document

    def find(self, name, query=None):
        query = query or {}
        collection = self.collection(name)
        if collection is not None:
            return list(collection.find(query))
        return [item for item in self.data[name] if all(item.get(k) == v for k, v in query.items())]

    def find_one(self, name, query):
        matches = self.find(name, query)
        return matches[0] if matches else None

    def seed(self):
        if self.find_one("courses", {"slug": "python-foundations"}):
            return
        courses = [
            ("python-foundations", "Python Foundations", "python", "Beginner", 35, "Build confidence with variables, loops, functions, and clean Python."),
            ("data-storytelling", "Data Storytelling", "analytics", "Intermediate", 45, "Turn analysis into clear, persuasive narratives for real decisions."),
            ("practical-nlp", "Practical NLP", "nlp", "Intermediate", 55, "Learn text cleaning, sentiment analysis, and useful language features."),
            ("mongodb-flask", "MongoDB with Flask", "backend", "Advanced", 60, "Design persistent Flask applications around simple document models."),
            ("statistics-refresh", "Statistics Refresh", "analytics", "Beginner", 30, "Revisit distributions, sampling, confidence, and experiment basics."),
            ("recommendation-systems", "Recommendation Systems", "ml", "Advanced", 70, "Build interpretable ranking systems from behavior and performance."),
        ]
        for slug, title, topic, level, minutes, description in courses:
            self.insert("courses", dict(slug=slug, title=title, topic=topic, level=level, minutes=minutes, description=description))

    def record_event(self, user_id, course_id, action, score=None):
        return self.insert("events", {"user_id": user_id, "course_id": course_id, "action": action, "score": score, "created_at": now()})

