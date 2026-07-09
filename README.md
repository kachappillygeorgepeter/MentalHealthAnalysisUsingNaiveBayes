# Sentiment Analysis System

A **FastAPI-based Sentiment Analysis API** that uses a **Naive Bayes** classifier to detect the emotional tone of user's message. The model classifies text into one of seven emotions:

- 😊 Happy
- 😢 Sad
- 😕 Confused
- 😠 Angry
- 😨 Fear
- 🤢 Disgust
- 😐 Neutral

The system stores emotional words and learnt probabilities inside a **MySQL** database and updates them through a training script using custom training datasets.

---

# Features

- Emotion detection using **Naive Bayes Classification**
- API built with **FastAPI**
- MySQL database for storing emotional words and probabilities
- Automatic stop-word removal
- Emotional word extraction
- Custom training using text datasets
- Probability based confidence score
- Easy to expand by adding new emotional words and training sentences

---

# Technologies Used

- Python 3.x
- FastAPI
- MySQL
- mysql-connector-python
- python-dotenv
- Pydantic
- RegEx
- OS

---

# How It Works

## 1. User sends text

Example

```text
I feel lonely and exhausted today.
```

---

## 2. Stop words are removed

Example

```text
lonely exhausted today
```

---

## 3. Emotional words are extracted

Only words that exist inside the **emotional_words** table are kept.

Example

```text
lonely exhausted
```

---

## 4. Naive Bayes Prediction

For every emotional word, the trained probability

```
P(word | emotion)
```

is loaded from the database.

The backend multiplies the probabilities together with the prior probability

```
P(emotion)
```

and predicts the emotion with the highest score.

---

## 5. API Response

Example

```json
{
  "prediction_message": "sad",
  "confidence": 0.94,
  "filtered_text": "lonely exhausted"
}
```

---

# Database

The project uses three tables.

## 1. stop_words

Stores common English stop words.

Example

```text
the
is
am
have
will
because
```

These are removed before prediction.

---

## 2. emotional_words

Stores every emotional word together with its learned statistics.

Example

| Word   | Happy Score | Sad Score | Angry Score |
| ------ | ----------- | --------- | ----------- |
| happy  | 0.42        | 0.01      | 0.01        |
| lonely | 0.01        | 0.53      | 0.02        |

Each word stores

- Count for every emotion
- Probability for every emotion

---

## 3. message_emotion_probabilities

Stores

```
P(emotion)
```

Example

| Emotion | Probability |
| ------- | ----------- |
| Happy   | 0.21        |
| Sad     | 0.18        |
| Neutral | 0.25        |

---

# Training the Model

The project does **not** use pre-trained machine learning libraries.

Instead, it trains its own Naive Bayes model.

Training data is stored inside

```text
TrainingData/
```

Each emotion has its own text file.

Example

```
training_sentences_happy.txt
training_sentences_sad.txt
training_sentences_angry.txt
```

Each line represents one training sentence.

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
