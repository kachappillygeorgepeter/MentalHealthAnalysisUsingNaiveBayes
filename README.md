# Sentiment Analysis System

A FastAPI-based sentiment analysis API using a Naive Bayes classifier to detect emotional tone from text. The model predicts one of nine emotions and returns a confidence score.

## Key Features

- Naive Bayes emotion classification
- FastAPI backend
- MySQL storage for learned word statistics
- Stop word removal and emotional word extraction
- Custom training from text datasets
- Confidence scoring for predictions

## Supported Emotions

- Happy
- Sad
- Confused
- Angry
- Fear
- Disgust
- Neutral
- Anxiety
- Suicidal
- Depressed

## Technology

- Python 3.x
- FastAPI
- MySQL
- mysql-connector-python
- python-dotenv
- Pydantic

## What the Project Does

1. Receives user text
2. Removes stop words
3. Extracts emotional terms
4. Uses Naive Bayes probabilities to predict emotion
5. Returns emotion and confidence

## Data Structure

The backend stores:

- stop words for filtering input
- emotional words with learned probabilities
- prior emotion probabilities

## Training Data

Training sentences are stored in the `TrainingData/` folder, with one file per emotion. Each line is treated as a separate training example.

## Notes

This project trains its own classifier and does not use external pretrained machine learning models.

Example

Example

```text
I finally got my dream job.
```

```text
Everything feels hopeless.
```

---

# Training Process

Run

```bash
python train.py
```

The script will ask

```text
Do you want to add training data now? (y/n)
```

Choosing

```text
y
```

loads every training file.

The trainer then

- loads emotional words
- removes stop words
- counts word frequency
- computes Naive Bayes probabilities with Laplace smoothing
- updates the MySQL database

Finally

```text
Training completed successfully.
```

---

# Running the Backend

Install dependencies

```bash
pip install -r requirements.txt
```

Run FastAPI

```bash
py -m uvicorn main:app --reload
```

Server starts at

```
http://127.0.0.1:8000
```

Swagger documentation

```
http://127.0.0.1:8000/docs
```

---

# API Endpoint

## POST `/process`

### Request

```json
{
  "text": "I feel extremely anxious and scared."
}
```

---

### Response

```json
{
  "prediction_message": "fear",
  "confidence": 0.962,
  "filtered_text": "anxious scared"
}
```

---

# Environment Variables

Create a `.env` (or `dbDetails.env`) file.

Example

```env
DB_HOST=xxx
DB_USER=xxx
DB_PASSWORD=xxx
DB_NAME=xxx
```

---

# Setting Up the Database

Execute

```bash
setup_db.sql
```

This script automatically creates

- `mental_health_db`
- `stop_words`
- `emotional_words`
- `message_emotion_probabilities`

and inserts the default emotional vocabulary.

---

# Adding New Emotional Words

Simply add new words into

```sql
INSERT INTO emotional_words(word)
VALUES (...);
```

After adding new words, retrain the model.

```bash
python train.py
```

This updates all probabilities in the database.

---

# Naive Bayes Formula

Word likelihood

```
P(word | emotion)
=
(word_count + 1)
/
(total_words + vocabulary_size)
```

The project uses **Laplace Smoothing** to avoid zero probabilities.

Emotion prior

```
P(emotion)
=
messages_for_emotion
/
total_messages
```

Prediction score

```
P(emotion)
×
Π P(word | emotion)
```

The emotion with the highest score is returned.

---

# Future Improvements

- Lemmatization and stemming
- Negation handling (e.g., "not happy")
- Emoji sentiment detection
- Multi-label emotion prediction
- Confidence calibration
- Larger emotional vocabulary
- Improved preprocessing using NLP libraries

---
