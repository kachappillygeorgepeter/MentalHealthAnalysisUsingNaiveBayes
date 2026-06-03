# ============================================================================
# Mental Health Sentiment Analysis System - Backend API
# ============================================================================
# 
# This is the main backend file that powers the Mental Health Sentiment 
# Analysis System. It analyzes sentences and predicts whether the user's 
# sentiment is "Depressed" or "Normal" based on word analysis and a simple
# Naive Bayes machine learning model.
#
# Technologies Used:
# - FastAPI: A modern, fast web framework for building APIs
# - MySQL: Database to store sentiment words and probability scores
# - Pandas: Data manipulation library
# - Scikit-learn: Machine learning library for Naive Bayes classifier
# - Uvicorn: ASGI server to run the FastAPI application
#
# ============================================================================

# Step 1: Import all required libraries
# ============================================================================

# FastAPI imports - for building the API
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Pydantic import - for data validation
from pydantic import BaseModel

# Database imports
import mysql.connector
from mysql.connector import Error

# Data processing imports
# pandas and numpy are not required in this file because the backend only loads stored scores

# Machine Learning is handled in a separate file so app.py only performs analysis

# Other imports
import traceback


# ============================================================================
# Step 2: Initialize FastAPI Application
# ============================================================================

# Create the FastAPI application instance
# FastAPI will automatically generate API documentation (Swagger UI)
app = FastAPI()

# Configure CORS (Cross-Origin Resource Sharing) to allow requests from frontend
# This enables the frontend to communicate with the backend from different domains
cors_origins = [
    "http://localhost:5500",      # Allow localhost from port 5500
    "http://127.0.0.1:5500",      # Allow 127.0.0.1 from port 5500
    "http://localhost:3000",      # Allow localhost from port 3000 (for development)
    "http://127.0.0.1:3000",      # Allow 127.0.0.1 from port 3000
]

# Add CORS middleware to the application
# This middleware handles CORS requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,           # Allow requests from these origins
    allow_credentials=True,                # Allow credentials (cookies, etc.)
    allow_methods=["*"],                   # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                   # Allow all headers
)


# ============================================================================
# Step 3: Database Configuration
# ============================================================================

# Database connection details
# IMPORTANT: Update these values with your actual MySQL credentials
DATABASE_CONFIG = {
    "host": "localhost",           # MySQL server address
    "user": "root",                # MySQL username
    "password": "your_password",   # MySQL password (change this!)
    "database": "mental_health_db" # Database name
}


# ============================================================================
# Step 4: Define Pydantic Models for Data Validation
# ============================================================================

# This model defines the structure of the request from the frontend
# Pydantic automatically validates that the incoming data matches this structure
class SentenceRequest(BaseModel):
    """
    Request model for the /analyze endpoint.
    
    Attributes:
        sentence (str): The user's input sentence to analyze for sentiment
    
    Example:
        {
            "sentence": "I feel lonely and hopeless today"
        }
    """
    sentence: str


# ============================================================================
# Step 5: Global Variables (Loaded at Startup)
# ============================================================================

# These variables will store data loaded from the database
depressed_words_dict = {}    # Dictionary to store depressed words and their scores
normal_words_dict = {}       # Dictionary to store normal words and their scores
stop_words_set = set()       # Set of stop words to filter out


# ============================================================================
# Step 6: Database Connection Function
# ============================================================================

def connect_database():
    """
    Establish a connection to the MySQL database.
    
    This function creates and returns a connection object that can be used
    to execute queries against the MySQL database.
    
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
        None: If connection fails
    
    Why this function exists:
        - We need to connect to MySQL to fetch words and probability scores
        - Centralizing connection logic makes it reusable
        - We can easily modify credentials in one place
    
    How it works:
        1. Uses the DATABASE_CONFIG to connect to MySQL
        2. If successful, returns the connection
        3. If fails, prints an error and returns None
    """
    try:
        # Attempt to connect to the MySQL database
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        
        if connection.is_connected():
            # Connection successful
            print("✓ Successfully connected to MySQL database!")
            return connection
    
    except Error as error:
        # Connection failed - print error message
        print(f"✗ Error connecting to MySQL: {error}")
        return None


# ============================================================================
# Step 7: Load Words from Database Functions
# ============================================================================

def load_depressed_words():
    """
    Load all depressed words and their probability scores from the database.
    
    This function fetches data from the 'depressed_words' table and stores
    it in a dictionary for quick lookup.
    
    Returns:
        dict: Dictionary with words as keys and probability scores as values
              Example: {"hopeless": 0.85, "lonely": 0.90}
        empty dict: If loading fails
    
    Why this function exists:
        - We need to compare user words against depressed words
        - Loading into memory makes lookups very fast
        - We can easily reload this data if needed
    
    How it works:
        1. Connect to the database
        2. Execute query to fetch all rows from depressed_words table
        3. Store each word with its probability score in a dictionary
        4. Return the dictionary
    """
    
    # Initialize empty dictionary
    words_dict = {}
    
    try:
        # Connect to database
        connection = connect_database()
        
        if connection is None:
            # Connection failed
            return words_dict
        
        # Create a cursor to execute queries
        cursor = connection.cursor()
        
        # SQL query to fetch all depressed words and their scores
        # The query selects the word column and probability_score column
        query = "SELECT word, probability_score FROM depressed_words"
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all results from the query
        # Results come back as tuples: (word, probability_score)
        results = cursor.fetchall()
        
        # Loop through each result and add to dictionary
        for word, score in results:
            words_dict[word.lower()] = score  # Convert word to lowercase for consistency
        
        print(f"✓ Loaded {len(words_dict)} depressed words from database")
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
    
    except Error as error:
        # Error occurred during query execution
        print(f"✗ Error loading depressed words: {error}")
    
    return words_dict


def load_normal_words():
    """
    Load all normal words and their probability scores from the database.
    
    This function is very similar to load_depressed_words() but fetches
    from the 'normal_words' table instead.
    
    Returns:
        dict: Dictionary with words as keys and probability scores as values
              Example: {"happy": 0.80, "excited": 0.75}
        empty dict: If loading fails
    
    Why this function exists:
        - We need to compare user words against normal words
        - Loading into memory makes lookups very fast
        - Similar to load_depressed_words() for consistency
    
    How it works:
        1. Connect to the database
        2. Execute query to fetch all rows from normal_words table
        3. Store each word with its probability score in a dictionary
        4. Return the dictionary
    """
    
    # Initialize empty dictionary
    words_dict = {}
    
    try:
        # Connect to database
        connection = connect_database()
        
        if connection is None:
            # Connection failed
            return words_dict
        
        # Create a cursor to execute queries
        cursor = connection.cursor()
        
        # SQL query to fetch all normal words and their scores
        query = "SELECT word, probability_score FROM normal_words"
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all results from the query
        results = cursor.fetchall()
        
        # Loop through each result and add to dictionary
        for word, score in results:
            words_dict[word.lower()] = score  # Convert word to lowercase for consistency
        
        print(f"✓ Loaded {len(words_dict)} normal words from database")
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
    
    except Error as error:
        # Error occurred during query execution
        print(f"✗ Error loading normal words: {error}")
    
    return words_dict


def load_stop_words():
    """
    Load all stop words from the database.
    
    Stop words are common English words (like "the", "is", "and") that don't
    carry much meaning. We remove them because they don't help in sentiment analysis.
    
    Returns:
        set: A set containing all stop words
             Example: {"the", "is", "and", "a", "an"}
        empty set: If loading fails
    
    Why this function exists:
        - Stop words don't contribute to sentiment analysis
        - Removing them makes the analysis more accurate
        - Loading into a set makes lookups very fast
    
    How it works:
        1. Connect to the database
        2. Execute query to fetch all rows from stop_words table
        3. Store each word in a set (sets are faster for lookups)
        4. Return the set
    """
    
    # Initialize empty set (sets are faster for "in" lookups than lists)
    words_set = set()
    
    try:
        # Connect to database
        connection = connect_database()
        
        if connection is None:
            # Connection failed
            return words_set
        
        # Create a cursor to execute queries
        cursor = connection.cursor()
        
        # SQL query to fetch all stop words
        query = "SELECT word FROM stop_words"
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all results from the query
        results = cursor.fetchall()
        
        # Loop through each result and add to set
        # Note: results come back as tuples, so we use results[0] to get just the word
        for (word,) in results:
            words_set.add(word.lower())  # Convert to lowercase for consistency
        
        print(f"✓ Loaded {len(words_set)} stop words from database")
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
    
    except Error as error:
        # Error occurred during query execution
        print(f"✗ Error loading stop words: {error}")
    
    return words_set


# ============================================================================
# Step 8: Text Processing Functions
# ============================================================================

def remove_stop_words(words_list, stop_words):
    """
    Remove stop words from a list of words.
    
    This function filters out common words that don't contribute to sentiment
    analysis, leaving only the meaningful words for analysis.
    
    Arguments:
        words_list (list): List of words to filter
                          Example: ["i", "feel", "lonely", "and", "hopeless", "today"]
        stop_words (set): Set of stop words to remove
                         Example: {"i", "and", "the"}
    
    Returns:
        list: List of words without stop words
              Example: ["feel", "lonely", "hopeless", "today"]
    
    Why this function exists:
        - Stop words like "the", "is", "and" don't help sentiment analysis
        - Removing them makes the analysis cleaner and more accurate
        - Centralizing this logic makes the code reusable
    
    How it works:
        1. Create an empty list for filtered words
        2. Loop through each word in the input list
        3. If the word is NOT in stop_words, add it to the filtered list
        4. Return the filtered list
    """
    
    # Initialize empty list to store filtered words
    filtered_words = []
    
    # Loop through each word in the input list
    for word in words_list:
        # Check if the word is NOT a stop word
        if word not in stop_words:
            # Add this word to the filtered list
            filtered_words.append(word)
    
    # Return the list of meaningful words
    return filtered_words


# ============================================================================
# Step 9: Sentiment Scoring Functions
# ============================================================================

def calculate_scores(filtered_words, depressed_dict, normal_dict):
    """
    Calculate sentiment scores based on filtered words.
    
    This function compares each word against the depressed_words and normal_words
    dictionaries, summing up the probability scores for each category.
    
    Arguments:
        filtered_words (list): List of words after removing stop words
                              Example: ["feel", "lonely", "hopeless"]
        depressed_dict (dict): Dictionary of depressed words and their scores
                              Example: {"lonely": 0.90, "hopeless": 0.85}
        normal_dict (dict): Dictionary of normal words and their scores
                           Example: {"happy": 0.80}
    
    Returns:
        tuple: (depressed_score, normal_score)
               Example: (1.75, 0.00)
    
    Why this function exists:
        - We need to quantify how many sentiment words appear in the text
        - Scoring allows us to make a prediction
        - Centralizing this logic makes it reusable
    
    How it works:
        1. Initialize both scores to 0
        2. Loop through each filtered word
        3. If word is in depressed_dict, add its score to depressed_score
        4. If word is in normal_dict, add its score to normal_score
        5. Return both scores
    
    Example:
        If we have words ["feel", "lonely", "hopeless", "today"]:
        - "feel" is in neither dictionary
        - "lonely" is in depressed_dict with score 0.90 → add to depressed_score
        - "hopeless" is in depressed_dict with score 0.85 → add to depressed_score
        - "today" is in neither dictionary
        Result: depressed_score = 1.75, normal_score = 0.00
    """
    
    # Initialize both scores to 0
    depressed_score = 0.0
    normal_score = 0.0
    
    # Loop through each word in the filtered list
    for word in filtered_words:
        # Check if word is in the depressed words dictionary
        if word in depressed_dict:
            # Add the probability score to the depressed score
            depressed_score += depressed_dict[word]
        
        # Check if word is in the normal words dictionary
        if word in normal_dict:
            # Add the probability score to the normal score
            normal_score += normal_dict[word]
    
    # Return both scores as a tuple
    # The tuple is (depressed_score, normal_score)
    return depressed_score, normal_score


# ============================================================================
# Step 10: Machine Learning Model Function
# ============================================================================

# Machine learning is handled in a separate file called ml_train.py.
# That file trains a Naive Bayes model and updates probability scores in MySQL.
# app.py only uses the stored probability scores for analysis.


# ============================================================================
# Step 11: Main Prediction Function
# ============================================================================

def predict_sentiment(sentence, depressed_dict, normal_dict, stop_words):
    """
    Predict whether a sentence expresses depressed or normal sentiment.
    
    This is the main function that orchestrates all the pieces:
    1. Clean the sentence
    2. Remove stop words
    3. Calculate scores
    4. Use machine learning for additional prediction
    5. Make a final prediction
    
    Arguments:
        sentence (str): User's input sentence
                       Example: "I feel lonely and hopeless today"
        depressed_dict (dict): Dictionary of depressed words
        normal_dict (dict): Dictionary of normal words
        stop_words (set): Set of stop words to remove
    
    Returns:
        dict: Dictionary with analysis results
              {
                "sentence": "I feel lonely and hopeless today",
                "filtered_words": ["feel", "lonely", "hopeless", "today"],
                "depressed_score": 1.75,
                "normal_score": 0.00,
                "prediction": "Depressed"
              }
    
    Why this function exists:
        - It brings all the analysis steps together
        - It returns all the information needed by the frontend
        - It's easy to test and modify
    
    How it works:
        1. Convert sentence to lowercase
        2. Split into words
        3. Remove stop words
        4. Calculate scores
        5. Make prediction based on scores
        6. Return results as a dictionary
    """
    
    # Step 1: Clean the sentence
    # ==========================
    
    # Convert to lowercase for consistency
    # "Hello" and "hello" should be treated as the same word
    sentence_lower = sentence.lower()
    
    # Step 2: Split into words
    # ========================
    
    # Remove punctuation and split by spaces
    # This is a simple approach - we just split by spaces
    words = sentence_lower.split()
    
    # Step 3: Remove stop words
    # =========================
    
    # Remove common words that don't help with sentiment
    filtered_words = remove_stop_words(words, stop_words)
    
    # Step 4: Calculate sentiment scores
    # ===================================
    
    # Sum up the probability scores for each category
    depressed_score, normal_score = calculate_scores(
        filtered_words,
        depressed_dict,
        normal_dict
    )
    
    # Step 5: Determine prediction based on scores
    # ============================================
    
    # If depressed score is higher, predict "Depressed"
    # Otherwise, predict "Normal"
    if depressed_score > normal_score:
        prediction = "Depressed"
    else:
        prediction = "Normal"
    
    # Step 6: Return results as a dictionary
    # ======================================
    
    # This dictionary will be converted to JSON and sent to the frontend
    result = {
        "sentence": sentence,                      # Original sentence from user
        "filtered_words": filtered_words,          # Words after removing stop words
        "depressed_score": round(depressed_score, 2),  # Rounded to 2 decimal places
        "normal_score": round(normal_score, 2),        # Rounded to 2 decimal places
        "prediction": prediction                   # Final prediction
    }
    
    return result


# ============================================================================
# Step 12: Initialize Application Data (Startup Event)
# ============================================================================

@app.on_event("startup")
def startup_event():
    """
    This function runs automatically when the FastAPI server starts.
    
    It loads all necessary stored data from the database.
    This ensures the API is ready before the first request.
    
    Why this function exists:
        - We only want to load data once, not for every request
        - This makes the API faster after startup
        - If something fails to load, we know immediately
    """
    
    global depressed_words_dict, normal_words_dict, stop_words_set
    
    print("\n" + "="*70)
    print("Starting Mental Health Sentiment Analysis API...")
    print("="*70 + "\n")
    
    # Load all data from database
    print("📚 Loading data from database...")
    depressed_words_dict = load_depressed_words()
    normal_words_dict = load_normal_words()
    stop_words_set = load_stop_words()
    
    print("\n" + "="*70)
    print("✓ API is ready to receive requests!")
    print("="*70 + "\n")


# ============================================================================
# Step 13: FastAPI Endpoints
# ============================================================================

@app.get("/")
def read_root():
    """
    Root endpoint - GET /
    
    This is a simple endpoint that returns a welcome message.
    It's useful for checking if the API is running.
    
    Returns:
        dict: A simple welcome message
    
    Example response:
        {
            "message": "Mental Health Sentiment Analysis API is running"
        }
    
    When to use this endpoint:
        - To check if the server is online
        - For health checks
        - To verify the API is accessible
    """
    
    return {
        "message": "Mental Health Sentiment Analysis API is running"
    }


@app.post("/analyze")
def analyze_sentiment(request: SentenceRequest):
    """
    Main analysis endpoint - POST /analyze
    
    This endpoint receives a sentence from the frontend, analyzes it for
    sentiment, and returns a prediction (Depressed or Normal).
    
    Arguments:
        request (SentenceRequest): The request body containing the sentence
                                  Example: {"sentence": "I feel lonely"}
    
    Returns:
        dict: Analysis results including the prediction
              {
                "sentence": "I feel lonely and hopeless today",
                "filtered_words": ["feel", "lonely", "hopeless", "today"],
                "depressed_score": 1.75,
                "normal_score": 0.00,
                "prediction": "Depressed"
              }
    
    Possible responses:
        - 200 OK: Analysis successful
        - 400 Bad Request: Invalid request format
        - 500 Internal Server Error: Server error during analysis
    
    When to use this endpoint:
        - When the user submits a sentence for analysis
        - When the frontend needs a sentiment prediction
    
    Example request:
        POST /analyze
        {
            "sentence": "I feel lonely and hopeless today"
        }
    
    How it works:
        1. Receives the sentence from the request
        2. Calls predict_sentiment() to analyze the sentence
        3. Returns the analysis results to the frontend
    """
    
    try:
        # Extract the sentence from the request
        sentence = request.sentence
        
        # Validate that the sentence is not empty
        if not sentence or sentence.strip() == "":
            return {
                "error": "Sentence cannot be empty",
                "sentence": sentence
            }
        
        # Call the predict_sentiment function to analyze the sentence
        result = predict_sentiment(
            sentence,
            depressed_words_dict,
            normal_words_dict,
            stop_words_set
        )
        
        # Return the result to the frontend
        return result
    
    except Exception as error:
        # If an error occurs, return an error message
        print(f"✗ Error during analysis: {error}")
        print(traceback.format_exc())
        
        return {
            "error": "An error occurred during sentiment analysis",
            "details": str(error)
        }


# ============================================================================
# Step 14: Running Instructions
# ============================================================================

"""
HOW TO RUN THIS APPLICATION:

1. Install all required packages:
   ================================
   
   pip install fastapi uvicorn scikit-learn pandas mysql-connector-python pydantic
   
   Or run all at once:
   
   pip install fastapi uvicorn scikit-learn pandas mysql-connector-python pydantic

2. Set up MySQL Database:
   =======================
   
   a. Make sure MySQL is running on your computer
   
   b. Create the database:
      CREATE DATABASE mental_health_db;
   
   c. Create the tables with sample data (see below)
   
   d. Update DATABASE_CONFIG in this file with your MySQL credentials

3. Set up MySQL Tables:
   =====================
   
   Run these SQL commands in your MySQL client:
   
   --- Create depressed_words table ---
   CREATE TABLE depressed_words (
       id INT AUTO_INCREMENT PRIMARY KEY,
       word VARCHAR(100) NOT NULL UNIQUE,
       probability_score FLOAT NOT NULL
   );
   
   INSERT INTO depressed_words (word, probability_score) VALUES
   ('hopeless', 0.85),
   ('lonely', 0.90),
   ('worthless', 0.88),
   ('sad', 0.92),
   ('depressed', 0.95),
   ('anxious', 0.87),
   ('stressed', 0.85),
   ('miserable', 0.93),
   ('unhappy', 0.89),
   ('tired', 0.80);
   
   --- Create normal_words table ---
   CREATE TABLE normal_words (
       id INT AUTO_INCREMENT PRIMARY KEY,
       word VARCHAR(100) NOT NULL UNIQUE,
       probability_score FLOAT NOT NULL
   );
   
   INSERT INTO normal_words (word, probability_score) VALUES
   ('happy', 0.80),
   ('excited', 0.75),
   ('motivated', 0.82),
   ('great', 0.78),
   ('wonderful', 0.85),
   ('energetic', 0.80),
   ('positive', 0.83),
   ('peaceful', 0.79),
   ('confident', 0.81),
   ('joyful', 0.87);
   
   --- Create stop_words table ---
   CREATE TABLE stop_words (
       id INT AUTO_INCREMENT PRIMARY KEY,
       word VARCHAR(100) NOT NULL UNIQUE
   );
   
   INSERT INTO stop_words (word) VALUES
   ('the'), ('is'), ('and'), ('a'), ('an'), ('in'), ('on'), ('at'),
   ('to'), ('for'), ('of'), ('i'), ('you'), ('he'), ('she'), ('it'),
   ('we'), ('they'), ('have'), ('has'), ('do'), ('does'), ('did'),
   ('been'), ('be'), ('are'), ('am'), ('was'), ('were'), ('would'),
   ('could'), ('should'), ('may'), ('might'), ('must'), ('can');

4. Run the application:
   =====================
   
   In your terminal, navigate to the BackEnd folder and run:
   
   uvicorn app:app --reload
   
   What this means:
   - uvicorn: The server that runs FastAPI applications
   - app:app: First 'app' is the filename (app.py), second 'app' is the FastAPI instance
   - --reload: Automatically restart server when you make code changes

5. Access the API:
   ================
   
   The API will be available at:
   
   http://localhost:8000
   
   Swagger UI (interactive documentation):
   http://localhost:8000/docs
   
   Alternative API docs:
   http://localhost:8000/redoc

6. Test the endpoints:
   ====================
   
   Using curl (command line):
   
   Test root endpoint:
   curl http://localhost:8000/
   
   Test analyze endpoint:
   curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{"sentence": "I feel lonely and hopeless today"}'
   
   Using Python:
   
   import requests
   
   # Test root
   response = requests.get("http://localhost:8000/")
   print(response.json())
   
   # Test analyze
   data = {"sentence": "I feel lonely and hopeless today"}
   response = requests.post("http://localhost:8000/analyze", json=data)
   print(response.json())

7. Connect from Frontend:
   ======================
   
   In your JavaScript frontend, use fetch to send requests:
   
   fetch('http://localhost:8000/analyze', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json'
       },
       body: JSON.stringify({
           sentence: userInputValue
       })
   })
   .then(response => response.json())
   .then(data => {
       console.log('Prediction:', data.prediction);
       console.log('Depressed Score:', data.depressed_score);
       console.log('Normal Score:', data.normal_score);
   });

TROUBLESHOOTING:

Problem: "No module named 'fastapi'"
Solution: Install with: pip install fastapi uvicorn

Problem: "Cannot connect to MySQL"
Solution: 
  1. Make sure MySQL is running
  2. Check DATABASE_CONFIG has correct credentials
  3. Make sure database 'mental_health_db' exists

Problem: "Table doesn't exist" error
Solution: Run the SQL commands to create tables and insert sample data

Problem: "CORS error in browser"
Solution: The CORS middleware is already configured for localhost:5500
          If using different port, add it to cors_origins list

"""

# ============================================================================
# END OF FILE
# ============================================================================
