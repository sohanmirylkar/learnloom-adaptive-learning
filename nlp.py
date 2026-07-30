import re
from collections import Counter

POSITIVE = {"clear", "helpful", "great", "good", "easy", "love", "useful", "confident", "excellent"}
NEGATIVE = {"confusing", "hard", "difficult", "unclear", "lost", "stuck", "boring", "frustrating", "bad"}
STOPWORDS = {"the", "a", "an", "and", "or", "to", "of", "is", "it", "this", "that", "was", "i", "in", "for"}


def analyze_feedback(text):
    words = re.findall(r"[a-z']+", text.lower())
    score = sum(word in POSITIVE for word in words) - sum(word in NEGATIVE for word in words)
    sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    keywords = [word for word, _ in Counter(
        word for word in words if len(word) > 3 and word not in STOPWORDS
    ).most_common(3)]
    return {"sentiment": sentiment, "score": score, "keywords": keywords}

