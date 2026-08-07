# A simple web framework for building APIs in Python.
from fastapi import FastAPI, HTTPException

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
import logging

# A library for loading environment variables from .env files.
from dotenv import load_dotenv

# A library for connecting to MySQL databases in Python.
import mysql.connector

# Google Generative AI SDK - used for the chatbot NLP fallback when no emotional words are detected.
import google.generativeai as genai

# Load environment variables from .env file.
load_dotenv()
load_dotenv("dbDetails.env")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "dbDetails.env"))
# Load API credentials for the chatbot fallback.
load_dotenv(os.path.join(os.path.dirname(__file__), "apiDetails.env"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

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

# These names must match the <emotion>_score columns in emotional_words and
# the emotion values in message_emotion_probabilities.
EMOTIONS = [
    "happy",
    "sad",
    "confused",
    "angry",
    "fear",
    "disgust",
    "anxiety",
    "suicidal",
    "depressed",
    "neutral",
]

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
    "anxiety": "neutral",
    "suicidal": "neutral",
    "depressed": "neutral",
}


# ─────────────────────────────────────────────────────────────────────────────
# Chatbot NLP Fallback
# ─────────────────────────────────────────────────────────────────────────────

def get_chatbot_response(user_text: str) -> str:
    """
    Called when no emotional words are detected in the user's input.
    Sends the original text to Google Gemini for a natural-language
    mental-health-aware reply, instead of simply returning 'Neutral'.

    Returns the chatbot reply string, or raises an exception if the API key
    is missing, invalid, or the call fails.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not configured or contains placeholder value in apiDetails.env."
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        system_prompt = (
            "You are a compassionate mental-health support assistant. "
            "The user's message does not contain clearly emotional language, "
            "but they may still need support or information. "
            "Respond in a warm, empathetic, and helpful way. "
            "Keep your response concise (2-4 sentences). "
            "Do NOT diagnose, prescribe, or replace professional help."
        )

        response = model.generate_content(f"{system_prompt}\n\nUser: {user_text}")
        if not response or not response.text:
            raise RuntimeError("Gemini API returned an empty response.")
        return response.text.strip()

    except Exception as e:
        logger.exception("Chatbot API call failed for text: %r", user_text[:80])
        raise e



# ─────────────────────────────────────────────────────────────────────────────

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
    port_value = os.getenv("DB_PORT")
    try:
        port = int(port_value) if port_value else None
    except ValueError as exc:
        raise ValueError(
            f"Invalid DB_PORT value: {port_value!r}. It must be a number."
        ) from exc

    cfg = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": port,
    }
    missing = [key for key in ("host", "user", "database") if not cfg[key]]
    if missing:
        env_names = ", ".join(f"DB_{key.upper()}" for key in missing)
        raise RuntimeError(
            f"Missing required database environment variables: {env_names}"
        )

    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=cfg["port"],
    )


# A function to load word scores from the database for a given set of words.
def load_word_scores(words):
    if not words:
        return {}

    columns = ", ".join(f"{emotion}_score" for emotion in EMOTIONS)
    placeholders = ", ".join(["%s"] * len(words))
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            f"SELECT word, {columns} FROM emotional_words WHERE word IN ({placeholders})",
            tuple(words),
        )
        rows = cur.fetchall()

        return {
            row[0]
            .lower()
            .strip(): {
                emotion: float(row[index + 1] or 0.0)
                for index, emotion in enumerate(EMOTIONS)
            }
            for row in rows
        }
    except mysql.connector.Error as e:
        logger.exception(
            "Failed to load word scores for %d words from the emotional_words table.",
            len(words),
        )
        raise RuntimeError(f"Database error while loading word scores: {e}") from e
    except Exception as e:
        logger.exception("Unexpected error while loading word scores.")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


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
    table_name = "emotional_words" if check else "stop_words"
    conn = None
    cur = None

    try:
        # Create database connection and fetch emotional words from the database, returning them as a set for efficient lookup.
        conn = get_connection()
        cur = conn.cursor()
        if check:
            cur.execute("SELECT word FROM emotional_words")
        else:
            cur.execute("SELECT word FROM stop_words")
        rows = cur.fetchall()
        # We recive the data from sql queiry as a list of tuples. Now we have to convert it to a set.
        # <if r> ensures tht the tuple is not empty and <r[0]> ensures tht the first element of the tuple (the word) is not empty.
        return set(r[0].lower().strip() for r in rows if r and r[0])
    except mysql.connector.Error:
        logger.exception(
            "Failed to load %s from the database. Returning an empty set.",
            table_name,
        )
        return set()
    except Exception:
        # If the DB isn't available return an empty set.
        logger.exception(
            "Unexpected error while loading %s. Returning an empty set.", table_name
        )
        return set()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# A variable of set data type to store words.
EMOTIONAL_WORDS = load_words(True)
STOP_WORDS = load_words(False)


def classifier_status():
    return {
        "ready": bool(EMOTIONAL_WORDS),
        "emotional_words_count": len(EMOTIONAL_WORDS),
        "stop_words_count": len(STOP_WORDS),
    }


def ensure_classifier_ready():
    if EMOTIONAL_WORDS:
        return

    logger.error(
        "Classifier is not ready because emotional_words loaded as empty. "
        "Check DB_NAME and confirm the emotional_words table exists."
    )
    raise HTTPException(
        status_code=503,
        detail={
            "message": "Classifier is not ready because emotional_words did not load from the database.",
            "likely_fix": "Check DB_NAME and confirm the emotional_words table exists in that database.",
            **classifier_status(),
        },
    )


def load_message_emotion_scores():
    conn = None
    cur = None

    try:
        # Load base emotion probabilities as P(emotion).
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT emotion, probability FROM message_emotion_probabilities")
        rows = cur.fetchall()

        result = {emotion: 1.0 for emotion in EMOTIONS}
        for emotion, probability in rows:
            emotion_key = emotion.lower().strip()
            if emotion_key in result:
                result[emotion_key] = float(probability or 0.0)

        return result
    except mysql.connector.Error:
        # If the DB isn't available, keep the endpoint responsive with neutral priors.
        logger.exception(
            "Failed to load message emotion probabilities. Using neutral priors."
        )
        return {emotion: 1.0 for emotion in EMOTIONS}
    except Exception:
        logger.exception(
            "Unexpected error while loading message emotion probabilities. Using neutral priors."
        )
        return {emotion: 1.0 for emotion in EMOTIONS}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.get("/")
def root():
    return {"message": "Mental Health Analysis API is running"}


@app.get("/health")
def health():
    status = classifier_status()
    return {
        "api": "running",
        "classifier": status,
    }


@app.get("/random-sentence")
def get_random_sentence(emotion: str):
    import random
    emotion_lower = emotion.lower().strip()
    if emotion_lower not in EMOTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid emotion: {emotion}. Must be one of {EMOTIONS}")
    
    file_path = os.path.join(os.path.dirname(__file__), "TrainingData", f"training_sentences_{emotion_lower}.txt")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Training file for emotion '{emotion_lower}' not found.")
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            sentences = [line.strip() for line in f if line.strip()]
        if not sentences:
            raise HTTPException(status_code=404, detail=f"No sentences found in training file for emotion '{emotion_lower}'.")
        return {"emotion": emotion_lower, "sentence": random.choice(sentences)}
    except Exception as e:
        logger.exception(f"Failed to read training sentences for emotion {emotion_lower}")
        raise HTTPException(status_code=500, detail=f"Error reading training sentences: {str(e)}")


# Define a POST endpoint at /process that accepts JSON data matching the InputText model,
# keeps emotional words from the input text, performs later actions on the cleaned text,
# and returns a prediction response.
# If no emotional words are found, the original text is sent to a Gemini chatbot
# for a natural-language NLP reply instead of returning a plain "Neutral".
@app.post("/process")
def process(payload: InputText):
    try:
        ensure_classifier_ready()
        text_without_stopwords = remove_stop_words(payload.text)
        cleaned_text = keep_emotional_words(text_without_stopwords)

        if not cleaned_text:
            # No emotional words were detected — delegate to the Gemini chatbot
            # for a more meaningful, context-aware natural language response.
            try:
                chatbot_reply = get_chatbot_response(payload.text)
                response = {
                    "prediction_message": "Neutral",
                    "confidence": 1.0,
                    "filtered_text": cleaned_text,
                    "chatbot_response": chatbot_reply,
                    "chatbot_used": True,
                }
                return response

            except Exception as api_error:
                # ── Print the full API problem to the backend console ──────────
                error_type = type(api_error).__name__
                error_msg  = str(api_error)
                logger.error(
                    "\n"
                    "╔══════════════════════════════════════════════════════╗\n"
                    "║          GEMINI API ERROR — SERVER SIDE              ║\n"
                    "╠══════════════════════════════════════════════════════╣\n"
                    "║  Error Type : %-38s║\n"
                    "║  Details    : %-38s║\n"
                    "╚══════════════════════════════════════════════════════╝",
                    error_type,
                    error_msg[:38],
                )
                logger.exception("Full traceback for Gemini API failure:")
                # Return a 503 so the frontend knows to display maintenance msg
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error":      "SERVER_UNDER_MAINTENANCE",
                        "error_type": error_type,
                        "api_error":  error_msg,
                    },
                ) from api_error

        # ── Emotional words found — use local Naive Bayes logic ────────────────
        result = perform_actions(cleaned_text)
        # Print the local prediction to the backend console
        print(
            f"\n[LOCAL PREDICTION] Emotion: {result['prediction_message'].upper()!r}  |  "
            f"Confidence: {round(result['confidence'] * 100, 2)}%  |  "
            f"Filtered text: {cleaned_text!r}"
        )
        return {
            "prediction_message": result["prediction_message"],
            "confidence": result["confidence"],
            "filtered_text": cleaned_text,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to process request text.")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to process the text. Check the backend logs for the full traceback.",
                "error_type": type(e).__name__,
                "error": str(e),
            },
        ) from e
