# A simple web framework for building APIs in Python.
import logging
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

# Create an instance of the FastAPI class, This instance will be used to handle requests.
app = FastAPI()

# Add CORS middleware to allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Define a Pydantic model to specify the expected structure of the input data for the API endpoint.
# Pydantic is a python library for data validation and tht kinda stuffs.
class InputText(BaseModel):
    text: str


# A function to extract each word from InputText.
def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def remove_stop_words(text):
    tokens = tokenize(text)
    filtered_tokens = [t for t in tokens if t not in STOP_WORDS]
    return " ".join(filtered_tokens)


########################################################################################################################
########################################################################################################################
########################################################################################################################
def analyze_sentiment(cleaned_text):
    tokens = tokenize(cleaned_text)
    emotions = ["happy", "sad", "confused", "angry", "fear", "disgust", "neutral"]
    scores = {emotion: 1.0 for emotion in emotions}

    # Connect to database to fetch probabilities
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        with conn.cursor() as cur:
            # 1. Load base probabilities P(Emotion)
            cur.execute(
                "SELECT emotion, probability FROM message_emotion_probabilities"
            )
            for emotion, prob in cur.fetchall():
                if emotion in scores:
                    scores[emotion] = float(prob)

            # 2. Update scores based on words P(Word|Emotion)
            words_to_query = [w for w in tokens if w in EMOTIONAL_WORDS]
            if words_to_query:
                # Fetch all unique word scores in one query
                unique_words = list(set(words_to_query))
                format_strings = ",".join(["%s"] * len(unique_words))
                query = f"SELECT word, {', '.join([e + '_score' for e in emotions])} FROM emotional_words WHERE word IN ({format_strings})"
                cur.execute(query, tuple(unique_words))

                # Map words to their scores
                word_score_map = {row[0]: row[1:] for row in cur.fetchall()}

                # Multiply scores based on frequency in the original tokens
                for word in words_to_query:
                    if word in word_score_map:
                        for i, emotion in enumerate(emotions):
                            scores[emotion] *= float(word_score_map[word][i])
    except Exception as e:
        print(f"Database error during analysis: {e}")
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()

    prediction = max(scores, key=scores.get)
    total_score = sum(scores.values())
    confidence = (scores[prediction] / total_score) if total_score > 0 else 0.0

    return {
        "prediction_message": prediction,
        "confidence": round(confidence, 4),
    }


########################################################################################################################
########################################################################################################################
########################################################################################################################


def load_words(table_name: str):
    # Setup configuration data for connecting to the database using environment variables
    cfg = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    try:
        # Create database connection and fetch words from the database, returning them as a set for efficient lookup.
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
        )
        with conn.cursor() as cur:
            cur.execute(f"SELECT word FROM {table_name}")
            rows = cur.fetchall()
            # We recive the data from sql queiry as a list of tuples. Now we have to convert it to a set.
            # <if r> ensures tht the tuple is not empty and <r[0]> ensures tht the first element of the tuple (the word) is not empty.
            return set(r[0].lower().strip() for r in rows if r and r[0])
    except Exception as e:
        # If the DB isn't available return an empty set.
        print(f"Error loading words from {table_name}: {e}")
        return set()
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()


# A variable of set data type to store words.
# if we pass "stop_words" to load_words function, it will load stop words from the database, otherwise it will load emotional words.
STOP_WORDS = load_words("stop_words")
EMOTIONAL_WORDS = load_words("emotional_words")


# Define a POST endpoint at /process that accepts JSON data matching the InputText model,
# removes stop words from the input text, performs later actions on the cleaned text,
# and returns a prediction response.
@app.post("/analyze")
def analyze(payload: InputText):
    cleaned_text = remove_stop_words(payload.text)
    result = analyze_sentiment(cleaned_text)
    return {
        "prediction_message": result["prediction_message"],
        "confidence": result["confidence"],
        "filtered_text": cleaned_text,
    }
