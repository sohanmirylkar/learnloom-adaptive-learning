# LearnLoom

An adaptive learning platform built with Python, Flask, NLP heuristics, and MongoDB. LearnLoom turns learner interests, performance, activity, and natural-language feedback into explainable content recommendations.

## Features

- Secure learner registration and login
- Behavior- and score-aware course recommendations
- NLP feedback sentiment and keyword analysis
- Progress, engagement, and learning-history tracking
- MongoDB persistence with a zero-configuration in-memory demo mode
- Responsive, accessible interface

## Run locally

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. Copy `.env.example` to `.env` or export its values to use MongoDB. Without `MONGODB_URI`, the app runs with temporary demo data.

## Test

```bash
python -m unittest discover -s tests
```

## Deploy

The included `render.yaml` creates a Render web service. Set `MONGODB_URI` to a MongoDB Atlas connection string during deployment. `SECRET_KEY` is generated automatically.

## Recommendation logic

The ranking remains deliberately interpretable: interest alignment, recently viewed content, assessment-derived difficulty, and completed-course exclusion. This is easier to audit and improve than an opaque model without enough training data.

