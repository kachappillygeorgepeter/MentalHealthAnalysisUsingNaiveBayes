# A simple web framework for building APIs in Python.
from fastapi import FastAPI

# A middleware for handling Cross-Origin Resource Sharing (CORS), which allows the frontend to communicate with the backend.
from fastapi.middleware.cors import CORSMiddleware

# A library for data validation in Python, used here to define the structure of incoming data.
from pydantic import BaseModel

# A library for working with file paths in an easy to read and platform independent way.
from pathlib import Path

# Regular Expressions - String manipulation and pattern matching.
import re

# A library for working with environment variables, used here to read database credentials.
import os

# A library for loading environment variables from .env files.
from dotenv import load_dotenv

# A library for connecting to MySQL databases in Python.
import mysql.connector

# Load environment variables from .env file.
load_dotenv()
load_dotenv("dbDetails.env")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "dbDetails.env"))

# Create an instance of the FastAPI class, This instance will be used to handle requests.
app = FastAPI()

# Add CORS middleware to allow the frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

EMOTIONS = ["happy", "sad", "confused", "angry", "fear", "disgust", "neutral"]

# To handle negation in text, we define a set of negation words that can invert the meaning of emotional words in the text.
NEGATION_WORDS = {
    "not",
    "no",
    "never",
    "don't",
    "dont",
    "doesn't",
    "doesnt",
    "didn't",
    "didnt",
    "isn't",
    "isnt",
    "aren't",
    "arent",
    "wasn't",
    "wasnt",
    "weren't",
    "werent",
    "can't",
    "cant",
    "couldn't",
    "couldnt",
    "won't",
    "wont",
    "without",
}

# To map each emotion to its opposite for negation handling.
OPPOSITE_EMOTION = {
    "happy": "sad",
    "sad": "neutral",
    "angry": "neutral",
    "fear": "neutral",
    "confused": "neutral",
    "disgust": "neutral",
}


# Define a Pydantic model to specify the expected structure of the input data for the API endpoint.
# Pydantic is a python library for data validation and tht kinda stuffs.
class InputText(BaseModel):
    text: str


# A function to extract each word from InputText.
def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


# A function to filter words
def remove_stop_words(text):
    tokens = tokenize(text)
    filtered_tokens = [t for t in tokens if t not in STOP_WORDS or t in NEGATION_WORDS]
    return " ".join(filtered_tokens)


# A function to filter words
def keep_emotional_words(text):
    tokens = tokenize(text)
    filtered_tokens = [t for t in tokens if t in EMOTIONAL_WORDS or t in NEGATION_WORDS]
    return " ".join(filtered_tokens)


# A fucntion to establish db connection
def get_connection():
    cfg = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )


# A function to load word scores from the database for a given set of words.
def load_word_scores(words):
    if not words:
        return {}

    columns = ", ".join(f"{emotion}_score" for emotion in EMOTIONS)
    placeholders = ", ".join(["%s"] * len(words))

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            f"SELECT word, {columns} FROM emotional_words WHERE word IN ({placeholders})",
            tuple(words),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            row[0]
            .lower()
            .strip(): {
                emotion: float(row[index + 1] or 0.0)
                for index, emotion in enumerate(EMOTIONS)
            }
            for row in rows
        }
    except Exception:
        return {}


# A function to perform actions on the cleaned text, checking negation, calculating emotion scores based on the presence of emotional words and their associated scores.
def perform_actions(cleaned_text):
    emotion_score = load_message_emotion_scores()
    words = cleaned_text.split()
    word_score_map = load_word_scores(set(w for w in words if w in EMOTIONAL_WORDS))
    negate = False

    for word in words:
        if word in NEGATION_WORDS:
            negate = True
            continue

        scores = word_score_map.get(word)
        if not scores:
            continue

        if negate:
            dominant = max(scores, key=scores.get)
            opposite = OPPOSITE_EMOTION.get(dominant, dominant)
            for emotion in EMOTIONS:
                if emotion == opposite:
                    emotion_score[emotion] *= scores[
                        dominant
                    ]  # Make the necessary emotion dominant
                else:
                    emotion_score[emotion] *= 0.0001  # Reduce the others to negligible
            negate = False
        else:
            for emotion in EMOTIONS:
                emotion_score[emotion] *= scores[emotion]

    message_type = max(emotion_score, key=emotion_score.get)
    total_score = sum(emotion_score.values())
    confidence = emotion_score[message_type] / total_score if total_score > 0 else 0.0
    return {
        "prediction_message": message_type,
        "confidence": round(confidence, 4),
    }


def load_words(check: bool):
    try:
        # Create database connection and fetch emotional words from the database, returning them as a set for efficient lookup.
        conn = get_connection()
        cur = conn.cursor()
        if check:
            cur.execute("SELECT word FROM emotional_words")
        else:
            cur.execute("SELECT word FROM stop_words")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # We recive the data from sql queiry as a list of tuples. Now we have to convert it to a set.
        # <if r> ensures tht the tuple is not empty and <r[0]> ensures tht the first element of the tuple (the word) is not empty.
        return set(r[0].lower().strip() for r in rows if r and r[0])
    except Exception:
        # If the DB isn't available return an empty set.
        return set()


# A variable of set data type to store words.
EMOTIONAL_WORDS = load_words(True)
STOP_WORDS = load_words(False)


def load_message_emotion_scores():
    try:
        # Load base emotion probabilities as P(emotion).
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT emotion, probability FROM message_emotion_probabilities")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        result = {emotion: 1.0 for emotion in EMOTIONS}
        for emotion, probability in rows:
            emotion_key = emotion.lower().strip()
            if emotion_key in result:
                result[emotion_key] = float(probability or 0.0)

        return result
    except Exception:
        # If the DB isn't available, keep the endpoint responsive with neutral priors.
        return {emotion: 1.0 for emotion in EMOTIONS}


@app.get("/")
def root():
    return {"message": "Mental Health Analysis API is running"}


# Define a POST endpoint at /process that accepts JSON data matching the InputText model,
# keeps emotional words from the input text, performs later actions on the cleaned text,
# and returns a prediction response.
@app.post("/process")
def process(payload: InputText):
    text_without_stopwords = remove_stop_words(payload.text)
    cleaned_text = keep_emotional_words(text_without_stopwords)
    if not cleaned_text:
        return {
            "prediction_message": "Neutral",
            "confidence": 1.0,
            "filtered_text": cleaned_text,
        }
    result = perform_actions(cleaned_text)
    return {
        "prediction_message": result["prediction_message"],
        "confidence": result["confidence"],
        "filtered_text": cleaned_text,
    }
