# A simple web framework for building APIs in Python.
from fastapi import FastAPI

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

# Create an instance of the FastAPI class, This instance will be used to handle requests.
app = FastAPI()


# Define a Pydantic model to specify the expected structure of the input data for the API endpoint.
# Pydantic is a python library for data validation and tht kinda stuffs.
class InputText(BaseModel):
    text: str


# A function to extract each word from InputText.
def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def keep_emotional_words(text):
    tokens = tokenize(text)
    filtered_tokens = [t for t in tokens if t in EMOTIONAL_WORDS]
    return " ".join(filtered_tokens)


def get_score_for_word(word, choice):
    valid_choices = {
        "happy",
        "sad",
        "confused",
        "angry",
        "fear",
        "disgust",
        "neutral",
    }
    choice_key = choice.lower().strip()
    if choice_key not in valid_choices:
        return 0.0

    score_column = f"{choice_key}_score"
    cfg = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
        )
        cur = conn.cursor()
        query = f"SELECT {score_column} FROM emotional_words WHERE word = %s LIMIT 1"
        cur.execute(query, (word.lower().strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row or row[0] is None:
            return 0.0

        return float(row[0])
    except Exception:
        return 0.0


########################################################################################################################
########################################################################################################################
########################################################################################################################
def perform_actions(cleaned_text):
    # Placeholder for future processing using the cleaned text.
    emotion_score = load_message_emotion_scores()
    for word in cleaned_text.split():
        if word in EMOTIONAL_WORDS:
            emotion_score["happy"] *= get_score_for_word(word, "happy")
            emotion_score["sad"] *= get_score_for_word(word, "sad")
            emotion_score["confused"] *= get_score_for_word(word, "confused")
            emotion_score["angry"] *= get_score_for_word(word, "angry")
            emotion_score["fear"] *= get_score_for_word(word, "fear")
            emotion_score["disgust"] *= get_score_for_word(word, "disgust")
            emotion_score["neutral"] *= get_score_for_word(word, "neutral")

    message_type = (
        max(emotion_score, key=emotion_score.get) if emotion_score else "neutral"
    )
    confidence = emotion_score.get(message_type, 0.0) if emotion_score else 0.0

    # Return the detected emotion and its score as confidence.
    return {
        "prediction_message": message_type,
        "confidence": confidence,
    }


########################################################################################################################
########################################################################################################################
########################################################################################################################


def load_emotional_words():
    # Setup configuration data for connecting to the database using environment variables
    cfg = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    try:
        # Create database connection and fetch emotional words from the database, returning them as a set for efficient lookup.
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
        )
        cur = conn.cursor()
        cur.execute("SELECT word FROM emotional_words")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # We recive the data from sql queiry as a list of tuples. Now we have to convert it to a set.
        # <if r> ensures tht the tuple is not empty and <r[0]> ensures tht the first element of the tuple (the word) is not empty.
        return set(r[0].lower().strip() for r in rows if r and r[0])
    except Exception:
        # If the DB isn't available return an empty set.
        return set()


# A variable of set data type to store emotional words.
EMOTIONAL_WORDS = load_emotional_words()


def load_message_emotion_scores():
    # Setup configuration data for connecting to the database using environment variables
    cfg = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    try:
        # Create database connection and fetch emotional words from the database, returning them as a set for efficient lookup.
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
        )
        cur = conn.cursor()
        # Load emotion scores from the message_emotion_probabilities table.
        # We read the first row and return a mapping of emotion -> score.
        cur.execute("SELECT * FROM message_emotion_probabilities LIMIT 1")
        rows = cur.fetchall()
        # get column names from the cursor
        colnames = []
        try:
            colnames = list(cur.column_names)
        except Exception:
            # fallback to cursor.description
            if cur.description:
                colnames = [c[0] for c in cur.description]
        cur.close()
        conn.close()

        if not rows:
            return {}

        row = rows[0]
        # Build {emotion: score} dict, skipping typical id/message columns
        skip_names = {"id", "message_id", "message", "rowid"}
        result = {}
        for name, val in zip(colnames, row):
            lname = name.lower()
            if lname in skip_names:
                continue
            # normalize column name: drop trailing _score if present
            key = lname
            if key.endswith("_score"):
                key = key[: -len("_score")]
            result[key] = float(val) if val is not None else 0.0

        return result
    except Exception:
        # If the DB isn't available return an empty set.
        return {}


# Define a POST endpoint at /process that accepts JSON data matching the InputText model,
# keeps emotional words from the input text, performs later actions on the cleaned text,
# and returns a prediction response.
@app.post("/process")
def process(payload: InputText):
    cleaned_text = keep_emotional_words(payload.text)
    result = perform_actions(cleaned_text)
    return {
        "prediction_message": result["prediction_message"],
        "confidence": result["confidence"],
        "filtered_text": cleaned_text,
    }
