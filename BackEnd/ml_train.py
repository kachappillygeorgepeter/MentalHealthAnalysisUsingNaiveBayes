# ============================================================================
# Mental Health Sentiment Analysis System - Machine Learning Trainer
# ============================================================================
#
# This file trains a simple Naive Bayes model using Scikit-learn and stores
# the learned probability scores in the MySQL database.
#
# The backend application (app.py) uses the stored probability scores for
# sentiment analysis. This keeps app.py simple and focused on request handling.
#
# ============================================================================

# Database imports
import mysql.connector
from mysql.connector import Error

# Machine Learning imports
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


# ============================================================================
# Database Configuration
# ============================================================================

# Update these credentials to match your MySQL setup
DATABASE_CONFIG = {
    "host": "localhost",           # MySQL server address
    "user": "root",                # MySQL username
    "password": "your_password",   # MySQL password (change this!)
    "database": "mental_health_db" # Database name
}


# ============================================================================
# Step 1: Database Connection
# ============================================================================

def connect_database():
    """
    Connect to the MySQL database.

    Returns:
        mysql.connector.connection.MySQLConnection or None
    """
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        if connection.is_connected():
            print("✓ Connected to MySQL for machine learning")
            return connection
    except Error as error:
        print(f"✗ Database connection error: {error}")
    return None


# ============================================================================
# Step 2: Load Training Data
# ============================================================================

def load_training_data():
    """
    Load the words and labels from the database for model training.

    Returns:
        tuple: (sentences, labels)
    """
    connection = connect_database()
    if connection is None:
        return [], []

    cursor = connection.cursor()
    
    # Load depressed words as training examples labeled "depressed"
    cursor.execute("SELECT word FROM depressed_words")
    depressed_words = [word.lower() for (word,) in cursor.fetchall()]

    # Load normal words as training examples labeled "normal"
    cursor.execute("SELECT word FROM normal_words")
    normal_words = [word.lower() for (word,) in cursor.fetchall()]

    cursor.close()
    connection.close()

    sentences = depressed_words + normal_words
    labels = ["depressed"] * len(depressed_words) + ["normal"] * len(normal_words)

    print(f"✓ Loaded {len(sentences)} training examples")
    return sentences, labels


# ============================================================================
# Step 3: Train the Naive Bayes Model
# ============================================================================

def train_naive_bayes_model(sentences, labels):
    """
    Train a simple Naive Bayes text classifier.

    Returns:
        sklearn.pipeline.Pipeline: Trained model
    """
    if not sentences or not labels:
        print("✗ No training data available")
        return None

    model = Pipeline([
        ("vectorizer", CountVectorizer()),
        ("classifier", MultinomialNB())
    ])

    model.fit(sentences, labels)
    print("✓ Trained Naive Bayes model")
    return model


# ============================================================================
# Step 4: Calculate Probability Score for a Word
# ============================================================================

def calculate_probability(model, word, label):
    """
    Calculate the probability score for a word belonging to one class.

    Arguments:
        model: The trained Naive Bayes model
        word (str): The word to score
        label (str): Either "depressed" or "normal"

    Returns:
        float: Probability score between 0.0 and 1.0
    """
    if model is None:
        return 0.0

    word_lower = word.lower()
    probabilities = model.predict_proba([word_lower])[0]
    class_index = list(model.classes_).index(label)
    return float(round(probabilities[class_index], 2))


# ============================================================================
# Step 5: Update Scores in the Database
# ============================================================================

def update_probability_scores(model):
    """
    Update the probability_score values in the depressed_words and normal_words tables.

    The probability_score in depressed_words is the model's probability that the
    word belongs to the depressed class. The probability_score in normal_words is
    the model's probability that the word belongs to the normal class.
    """
    connection = connect_database()
    if connection is None:
        return

    cursor = connection.cursor()
    
    # Update depressed_words table
    cursor.execute("SELECT id, word FROM depressed_words")
    depressed_rows = cursor.fetchall()
    for row_id, word in depressed_rows:
        score = calculate_probability(model, word, "depressed")
        cursor.execute(
            "UPDATE depressed_words SET probability_score = %s WHERE id = %s",
            (score, row_id)
        )

    # Update normal_words table
    cursor.execute("SELECT id, word FROM normal_words")
    normal_rows = cursor.fetchall()
    for row_id, word in normal_rows:
        score = calculate_probability(model, word, "normal")
        cursor.execute(
            "UPDATE normal_words SET probability_score = %s WHERE id = %s",
            (score, row_id)
        )

    connection.commit()
    cursor.close()
    connection.close()
    print("✓ Updated probability scores in the database")


# ============================================================================
# Step 6: Main Execution
# ============================================================================

def main():
    """
    Main function to run the training and update process.

    Usage:
        python ml_train.py
    """
    sentences, labels = load_training_data()
    model = train_naive_bayes_model(sentences, labels)
    if model is not None:
        update_probability_scores(model)
        print("\nMachine learning training complete. The backend can now use stored scores.")
    else:
        print("✗ Training failed. No changes were made to the database.")


if __name__ == "__main__":
    main()
