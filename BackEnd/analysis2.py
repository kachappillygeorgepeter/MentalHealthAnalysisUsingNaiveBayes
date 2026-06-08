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


########################################################################################################################
########################################################################################################################
########################################################################################################################
def perform_actions(cleaned_text):
    # Placeholder for future processing using the cleaned text.
    # Replace this logic with the actual prediction or analysis pipeline later.
    return {
        "prediction_message": "pending",
        "confidence": 0.0,
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
