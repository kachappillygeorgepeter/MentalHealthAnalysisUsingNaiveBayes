import os
import re

EMOTIONS = ["happy", "sad", "confused", "angry", "fear", "disgust", "neutral"]
TRAINING_DATA_DIR = os.path.join(os.path.dirname(__file__), "TrainingData")

# Training sentences are loaded from TrainingData/training_sentences_<emotion>.txt.
TRAINING_DATA = {emotion: [] for emotion in EMOTIONS}


# Function to load environment variables from a .env file.
def load_env_file(file_name):
    if not os.path.exists(file_name):  # Check if file exists
        return

    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if (
                not line or line.startswith("#") or "=" not in line
            ):  # Check if line is empty, a comment, or doesn't contain an '=' character, and skip it if so.
                continue

            key, value = line.split(
                "=", 1
            )  # Split the line into key and value at the first '=' character.
            os.environ.setdefault(
                key.strip(), value.strip().strip("'\"")
            )  # Set the environment variable if it's not already set, stripping whitespace and any surrounding quotes from the value.


# Function to establish a connection to the MySQL db.
def get_connection():
    import mysql.connector

    # Any method for laoding is fine, but we want to be sure to check both the current working directory and the directory containing this script, since the .env files could be in either place depending on how the script is run.
    # Search relative to the current working directory.
    load_env_file(".env")
    load_env_file("dbDetails.env")
    # Search relative to the directory containing the current Python file.
    load_env_file(os.path.join(os.path.dirname(__file__), ".env"))
    load_env_file(os.path.join(os.path.dirname(__file__), "dbDetails.env"))

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


# Function to load words from the database and returning them as a set.
def get_words_from_table(cursor, table_name):
    cursor.execute(f"SELECT word FROM {table_name}")
    return {row[0].lower() for row in cursor.fetchall()}


# Function to tokenize text and to convert it to lowercase.
def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


# Function to remove stop words from the text.
def clean_text(text, emotional_words, stop_words):
    words = tokenize(text)
    return [
        word for word in words if word in emotional_words and word not in stop_words
    ]


# Function to add training data.
def add_training_data():
    # Keep prompting until the user enters a valid response ('y' or 'n').
    while True:
        choice = input("Do you want to add training data now? (y/n): ").lower().strip()
        if choice in ("y", "n"):
            break
        print("Please enter 'y' or 'n'. Try again.")

    if choice == "n":
        return

    total_sentences_added = 0

    for emotion in EMOTIONS:
        file_path = os.path.join(
            TRAINING_DATA_DIR, f"training_sentences_{emotion}.txt"
        )

        if not os.path.exists(file_path):
            print(f"No training file found for {emotion}: {file_path}")
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            sentences = [line.strip() for line in file if line.strip()]

        TRAINING_DATA[emotion].extend(sentences)
        total_sentences_added += len(sentences)
        print(f"Loaded {len(sentences)} {emotion} training sentences.")

    print(f"Loaded {total_sentences_added} training sentences from TrainingData.")


# Function to collect data for training naive bayes model and for db updation.
def train_naive_bayes(emotional_words, stop_words):
    # Initialization
    # fmt: off
    word_counts = {} # Structure: {emotion: {word: count}} Store the count of each word for each emotion.
    total_words = {} # Structure: {emotion: total_count} Store the total number of words for each emotion.
    message_counts = {} # Structure: {emotion: message_count} Store the total number of messages for each emotion.
    #fmt: on
    # Loop through each emotion and count the occurrences of each word in the training sentences, while also keeping track of the total number of words and messages for each emotion.
    for emotion in EMOTIONS:
        word_counts[emotion] = {}
        total_words[emotion] = 0
        message_counts[emotion] = len(TRAINING_DATA[emotion])

        for sentence in TRAINING_DATA[emotion]:
            cleaned_words = clean_text(sentence, emotional_words, stop_words)

            for word in cleaned_words:
                if word not in word_counts[emotion]:
                    word_counts[emotion][word] = 0

                word_counts[emotion][word] += 1
                total_words[emotion] += 1

    vocabulary_size = len(emotional_words)
    # fmt: off
    word_scores = {} # Structure: {word: {emotion_count, emotion_score}} Store the count and score of each word for each emotion.
    # fmt: on

    for word in emotional_words:
        word_scores[word] = {}

        for emotion in EMOTIONS:
            # fmt: off
            count = word_counts[emotion].get(word, 0) # Get the count of the word for the emotion, defaulting to 0 if the word is not present in the training data for that emotion.
            # fmt: on

            # Naive Bayes with Laplace smoothing:
            # P(word | emotion) = (Word Count (of a word for a particular emotion) + 1) / (Total Word Count (for that emotion) + Vocabulary Size (number of unique words in the emotional_words table))
            probability = (count + 1) / (total_words[emotion] + vocabulary_size)

            word_scores[word][f"{emotion}_count"] = count + 1  # Updating count
            word_scores[word][f"{emotion}_score"] = probability  # Updating score

    total_messages = sum(
        message_counts.values()
    )  # Calculate the total number of messages across all emotions, which is needed to calculate the probability of each emotion based on the training data.
    # fmt: off
    emotion_scores = {} # Structure: {emotion: {count, probability}} Store the count and probability of each emotion based on the training data.
    # fmt: on

    for emotion in EMOTIONS:
        # P(emotion) = Messages For Emotion (each) / Total Messages (for all emotions)
        emotion_scores[emotion] = {
            "count": message_counts[emotion],
            "probability": (
                message_counts[emotion] / total_messages if total_messages else 0.0
            ),
        }
    # word_scores → contains probabilities for every word.
    # emotion_scores → contains overall probabilities for each emotion
    return word_scores, emotion_scores


# Fucntion to save the trained data to the database.
def save_training_to_database(cursor, word_scores, emotion_scores):
    for word, scores in word_scores.items():
        cursor.execute(
            """
            UPDATE emotional_words
            SET
                happy_count = %s, happy_score = %s,
                sad_count = %s, sad_score = %s,
                confused_count = %s, confused_score = %s,
                angry_count = %s, angry_score = %s,
                fear_count = %s, fear_score = %s,
                disgust_count = %s, disgust_score = %s,
                neutral_count = %s, neutral_score = %s
            WHERE word = %s
            """,
            (
                scores["happy_count"],
                scores["happy_score"],
                scores["sad_count"],
                scores["sad_score"],
                scores["confused_count"],
                scores["confused_score"],
                scores["angry_count"],
                scores["angry_score"],
                scores["fear_count"],
                scores["fear_score"],
                scores["disgust_count"],
                scores["disgust_score"],
                scores["neutral_count"],
                scores["neutral_score"],
                word,
            ),
        )

    for emotion, scores in emotion_scores.items():
        cursor.execute(
            """
            UPDATE message_emotion_probabilities
            SET probability = %s, count = %s
            WHERE emotion = %s
            """,
            (scores["probability"], scores["count"], emotion),
        )


# Main Fucntion
def main():
    add_training_data()

    connection = get_connection()
    cursor = connection.cursor()

    emotional_words = get_words_from_table(cursor, "emotional_words")
    stop_words = get_words_from_table(cursor, "stop_words")

    word_scores, emotion_scores = train_naive_bayes(emotional_words, stop_words)
    save_training_to_database(cursor, word_scores, emotion_scores)

    connection.commit()
    cursor.close()
    connection.close()

    print("Training completed successfully.")


if __name__ == "__main__":
    main()
