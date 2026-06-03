# Mental Health Sentiment Analysis System - Backend Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Database Setup](#database-setup)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Testing the API](#testing-the-api)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start, make sure you have:

- **Python 3.8+** installed ([Download Python](https://www.python.org/))
- **MySQL Server** installed and running ([Download MySQL](https://dev.mysql.com/downloads/mysql/))
- **MySQL Workbench** or command-line client (optional but helpful)
- A terminal/command prompt

To check if Python is installed:
```bash
python --version
```

To check if MySQL is installed and running:
```bash
mysql --version
```

---

## Installation Steps

### Step 1: Install Python Dependencies

Navigate to the BackEnd folder and install all required packages:

```bash
# Using pip to install from requirements.txt
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install fastapi uvicorn scikit-learn pandas mysql-connector-python pydantic
```

**What each package does:**
- `fastapi`: Web framework for building the API
- `uvicorn`: Server to run the FastAPI application
- `scikit-learn`: Machine learning library for Naive Bayes
- `pandas`: Data manipulation library
- `mysql-connector-python`: Connect to MySQL database
- `pydantic`: Data validation using Python type hints

---

## Database Setup

### Step 2: Create MySQL Database

1. **Open MySQL Command Line** or **MySQL Workbench**

2. **Create the database:**

```sql
CREATE DATABASE mental_health_db;
```

3. **Select the database:**

```sql
USE mental_health_db;
```

4. **Create the depressed_words table:**

```sql
CREATE TABLE depressed_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    probability_score FLOAT NOT NULL
);
```

5. **Insert sample depressed words:**

```sql
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
('tired', 0.80),
('frustrated', 0.86),
('disappointed', 0.84),
('confused', 0.75),
('worried', 0.88),
('scared', 0.91);
```

6. **Create the normal_words table:**

```sql
CREATE TABLE normal_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    probability_score FLOAT NOT NULL
);
```

7. **Insert sample normal words:**

```sql
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
('joyful', 0.87),
('loved', 0.86),
('grateful', 0.84),
('calm', 0.77),
('hopeful', 0.88),
('strong', 0.79);
```

8. **Create the stop_words table:**

```sql
CREATE TABLE stop_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE
);
```

9. **Insert stop words:**

```sql
INSERT INTO stop_words (word) VALUES
('the'), ('is'), ('and'), ('a'), ('an'), ('in'), ('on'), ('at'),
('to'), ('for'), ('of'), ('i'), ('you'), ('he'), ('she'), ('it'),
('we'), ('they'), ('have'), ('has'), ('do'), ('does'), ('did'),
('been'), ('be'), ('are'), ('am'), ('was'), ('were'), ('would'),
('could'), ('should'), ('may'), ('might'), ('must'), ('can'),
('just'), ('only'), ('or'), ('as'), ('by'), ('from'), ('with'),
('this'), ('that'), ('these'), ('those'), ('my'), ('your'),
('his'), ('her'), ('its'), ('our'), ('their'), ('not');
```

10. **Verify the data was inserted:**

```sql
SELECT COUNT(*) FROM depressed_words;
SELECT COUNT(*) FROM normal_words;
SELECT COUNT(*) FROM stop_words;
```

---

## Configuration

### Step 3: Update Database Credentials

Open `app.py` and find the `DATABASE_CONFIG` section (around line 90):

```python
DATABASE_CONFIG = {
    "host": "localhost",           # MySQL server address
    "user": "root",                # MySQL username (change if different)
    "password": "your_password",   # MySQL password (change this!)
    "database": "mental_health_db" # Database name
}
```

Update with your MySQL credentials:
- `host`: Usually "localhost" unless using remote MySQL
- `user`: Your MySQL username (default is "root")
- `password`: Your MySQL password
- `database`: Should be "mental_health_db"

**Example:**
```python
DATABASE_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mypassword123",
    "database": "mental_health_db"
}
```

---

## Running the Application

### Step 4: Start the FastAPI Server

Navigate to the BackEnd folder in your terminal:

```bash
cd BackEnd
```

Run the application with Uvicorn:

```bash
uvicorn app:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
INFO:     Started reloader process [5678]
```

You should also see:
```
======================================================================
Starting Mental Health Sentiment Analysis API...
======================================================================

📚 Loading data from database...
✓ Loaded 15 depressed words from database
✓ Loaded 15 normal words from database
✓ Loaded 49 stop words from database

🤖 Training machine learning model...
✓ Naive Bayes model trained successfully!

======================================================================
✓ API is ready to receive requests!
======================================================================
```

The server is now running on:
- **Main API**: `http://localhost:8000`
- **Interactive API docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative docs (ReDoc)**: `http://localhost:8000/redoc`

---

## Testing the API

### Option 1: Test in Browser (Interactive Docs)

1. Open your browser and go to: `http://localhost:8000/docs`
2. You'll see the Swagger UI with all available endpoints
3. Click on `/analyze` endpoint
4. Click "Try it out"
5. Enter a sentence in the text field:
   ```json
   {
       "sentence": "I feel lonely and hopeless today"
   }
   ```
6. Click "Execute"
7. You should see the prediction results!

### Option 2: Test with cURL (Command Line)

**Test the root endpoint:**
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
    "message": "Mental Health Sentiment Analysis API is running"
}
```

**Test the analyze endpoint:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"sentence": "I feel lonely and hopeless today"}'
```

Expected response:
```json
{
    "sentence": "I feel lonely and hopeless today",
    "filtered_words": ["feel", "lonely", "hopeless"],
    "depressed_score": 2.65,
    "normal_score": 0.0,
    "prediction": "Depressed"
}
```

### Option 3: Test with Python

Create a file called `test_api.py`:

```python
import requests

# Test root endpoint
print("Testing root endpoint...")
response = requests.get("http://localhost:8000/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test analyze endpoint with depressed sentiment
print("Testing analyze endpoint with depressed sentiment...")
data = {"sentence": "I feel lonely and hopeless today"}
response = requests.post("http://localhost:8000/analyze", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test analyze endpoint with normal sentiment
print("Testing analyze endpoint with normal sentiment...")
data = {"sentence": "I feel happy and excited today"}
response = requests.post("http://localhost:8000/analyze", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")
```

Run it:
```bash
python test_api.py
```

### Option 4: Test from Frontend

Use JavaScript's `fetch` API to test from your HTML/JavaScript:

```javascript
// Test the API
async function analyzeText() {
    const sentence = "I feel lonely and hopeless today";
    
    try {
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sentence: sentence
            })
        });
        
        const data = await response.json();
        console.log('Prediction:', data.prediction);
        console.log('Depressed Score:', data.depressed_score);
        console.log('Normal Score:', data.normal_score);
        console.log('Filtered Words:', data.filtered_words);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Call the function
analyzeText();
```

---

## Troubleshooting

### Error: "No module named 'fastapi'"

**Solution:** Install missing dependencies
```bash
pip install fastapi uvicorn
```

Or use the requirements.txt file:
```bash
pip install -r requirements.txt
```

### Error: "Cannot connect to MySQL"

**Solutions:**
1. Check if MySQL is running
   - On Windows: Start MySQL from Services or Command Prompt
   - On Mac/Linux: Check MySQL status
   
2. Verify DATABASE_CONFIG credentials in `app.py`
   
3. Make sure the database exists:
   ```bash
   mysql -u root -p
   SHOW DATABASES;
   ```

4. If database doesn't exist, create it:
   ```bash
   CREATE DATABASE mental_health_db;
   ```

### Error: "Table 'mental_health_db.depressed_words' doesn't exist"

**Solution:** Run the SQL commands from the Database Setup section to create tables.

### Error: "CORS error in browser"

**This is expected if:**
- You're using a different port than 5500
- You're using a different domain

**Solution:** Add your frontend URL to the `cors_origins` list in `app.py`:

```python
cors_origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",      # Add your frontend port here
    "http://127.0.0.1:3000",
]
```

Then restart the server.

### Error: "Address already in use"

**Solution:** The server is already running or the port is occupied.

1. Find and stop the existing server (Ctrl+C in terminal)
2. Or use a different port:
   ```bash
   uvicorn app:app --reload --port 8001
   ```

### Error: "ModuleNotFoundError: No module named 'sklearn'"

**Solution:**
```bash
pip install scikit-learn
```

### The API is slow or not responding

**Solutions:**
1. Check if MySQL is responding (it might be hung)
2. Restart MySQL service
3. Restart the FastAPI server
4. Check the terminal for error messages

---

## Next Steps

Once the API is running:

1. **Integrate with Frontend**: Update your HTML/JavaScript to call `/analyze` endpoint
2. **Add More Words**: Insert more depressed/normal words into MySQL tables to improve accuracy
3. **Customize Stop Words**: Add or remove stop words based on your needs
4. **Deploy**: Move your backend to a hosting service (e.g., Heroku, AWS, Azure)

---

## File Structure

```
MentalHealthAnalysis/
├── BackEnd/
│   ├── app.py                 # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── SETUP_GUIDE.md        # This file
├── FrontEnd/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── ... (other files)
└── index.html
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

## Questions?

If you encounter any issues:
1. Check the error message in the terminal
2. Review the TROUBLESHOOTING section above
3. Check the console output when the app starts up
4. Make sure all dependencies are installed

Happy coding! 🚀
