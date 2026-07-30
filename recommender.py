def recommend(courses, events, interests, limit=3):
    completed = {event["course_id"] for event in events if event["action"] == "completed"}
    viewed = {event["course_id"] for event in events if event["action"] == "viewed"}
    scores = [event["score"] for event in events if event.get("score") is not None]
    average = sum(scores) / len(scores) if scores else 70

    def rank(course):
        score = 0
        reasons = []
        if course["topic"] in interests:
            score += 5
            reasons.append("matches your interests")
        if course["_id"] in viewed:
            score += 2
            reasons.append("continue where you left off")
        target = "Beginner" if average < 60 else "Intermediate" if average < 85 else "Advanced"
        if course["level"] == target:
            score += 3
            reasons.append("fits your current pace")
        return score, reasons or ["broadens your learning path"]

    ranked = [(course, *rank(course)) for course in courses if course["_id"] not in completed]
    ranked.sort(key=lambda item: (-item[1], item[0]["minutes"]))
    return [{"course": course, "reason": reason[0], "match": min(98, 72 + score * 3)} for course, score, reason in ranked[:limit]]

