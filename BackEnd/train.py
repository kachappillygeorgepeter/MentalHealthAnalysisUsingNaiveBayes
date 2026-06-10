import os
import re


EMOTIONS = ["happy", "sad", "confused", "angry", "fear", "disgust", "neutral"]

# Add training sentences here. The strings do not need to be cleaned.
TRAINING_DATA = {
    "happy": [
        "I feel happy joyful excited loved and hopeful today",
        "Life feels bright cheerful peaceful and positive",
    ],
    "sad": [
        "I feel sad lonely hopeless tired and empty",
        "I am heartbroken rejected abandoned and depressed",
    ],
    "confused": [
        "I feel confused unsure unclear and lost",
        "My thoughts are scattered foggy doubtful and mixed up",
    ],
    "angry": [
        "I feel angry furious irritated frustrated and bitter",
        "I am annoyed offended hostile and resentful",
    ],
    "fear": [
        "I feel afraid scared nervous anxious and worried",
        "I am terrified panicked insecure and vulnerable",
    ],
    "disgust": [
        "I feel disgusted repulsed revolted and sickened",
        "That was gross nasty offensive vile and unpleasant",
    ],
    "neutral": [
        "I went to the store and completed my work",
        "The meeting happened today and the report was shared",
    ],
}


def load_env_file(file_name):
    if not os.path.exists(file_name):
        return

    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def get_connection():
    import mysql.connector

    load_env_file(".env")
    load_env_file("dbDetails.env")
    load_env_file(os.path.join(os.path.dirname(__file__), ".env"))
    load_env_file(os.path.join(os.path.dirname(__file__), "dbDetails.env"))

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "mental_health_db"),
    )


def get_words_from_table(cursor, table_name):
    cursor.execute(f"SELECT word FROM {table_name}")
    return {row[0].lower() for row in cursor.fetchall()}


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def clean_text(text, emotional_words, stop_words):
    words = tokenize(text)

    # Set lookup is fast, so this keeps only emotional words quickly.
    return [word for word in words if word in emotional_words]


def add_training_data():
    choice = input("Do you want to add training data now? (y/n): ").lower().strip()
    if choice != "y":
        return

    for emotion in EMOTIONS:
        print(f"\nEnter training sentences for {emotion}. Press Enter to stop.")
        while True:
            sentence = input(f"{emotion}: ").strip()
            if not sentence:
                break
            TRAINING_DATA[emotion].append(sentence)


def train_naive_bayes(emotional_words, stop_words):
    word_counts = {}
    total_words = {}
    message_counts = {}

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
    word_scores = {}

    for word in emotional_words:
        word_scores[word] = {}

        for emotion in EMOTIONS:
            count = word_counts[emotion].get(word, 0)

            # Naive Bayes with Laplace smoothing:
            # P(word | emotion) = (word_count + 1) / (total_words + vocabulary_size)
            probability = (count + 1) / (total_words[emotion] + vocabulary_size)

            word_scores[word][f"{emotion}_count"] = count + 1
            word_scores[word][f"{emotion}_score"] = probability

    total_messages = sum(message_counts.values())
    emotion_scores = {}

    for emotion in EMOTIONS:
        # P(emotion) = messages_for_emotion / total_messages
        emotion_scores[emotion] = {
            "count": message_counts[emotion],
            "probability": message_counts[emotion] / total_messages,
        }

    return word_scores, emotion_scores


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
