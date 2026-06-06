# Mental Health Sentiment Analysis System

A FastAPI-based backend application that analyzes text and predicts whether the sentiment indicates a depressed or normal emotional state using a Naive Bayes classifier and a MySQL database.

## Install Dependencies

```bash
cd BackEnd
pip install -r requirements.txt
```

## Database Setup

1. Start MySQL.
2. Run the SQL commands in `setup_database.sql`.
3. Update the database credentials in `app.py`.

### Run the Application

```bash
uvicorn app:app --reload
```

The API will be available at:

```
http://localhost:8000
```

API documentation:

```
http://localhost:8000/docs
```

## Project Structure

```text
BackEnd/
├── app.py
├── requirements.txt
├── SETUP_GUIDE.md
└── setup_database.sql
```

## Features

- REST API built with FastAPI
- Naive Bayes sentiment classification using Scikit-learn
- MySQL integration for storing sentiment words and scores
- Stop-word filtering
- Automatic API documentation with Swagger UI
- Input validation using Pydantic
- CORS support for frontend integration

## API Endpoints

### GET /

Checks whether the API is running.

Example:

```bash
curl http://localhost:8000/
```

### POST /analyze

Analyzes a sentence and returns sentiment scores and prediction.

Example:

```bash
curl -X POST http://localhost:8000/analyze \
-H "Content-Type: application/json" \
-d '{"sentence":"I feel lonely and hopeless"}'
```

Example Response:

```json
{
  "sentence": "I feel lonely and hopeless",
  "filtered_words": ["feel", "lonely", "hopeless"],
  "depressed_score": 2.75,
  "normal_score": 0.0,
  "prediction": "Depressed"
}
```

## How It Works

1. Receive text input from the frontend.
2. Convert text to lowercase and remove punctuation.
3. Remove stop words.
4. Calculate sentiment scores using words stored in the database.
5. Compare scores and generate a prediction.
6. Validate results using a Naive Bayes classifier.

## Database Tables

### depressed_words

| id  | word      | probability_score |
| --- | --------- | ----------------- |
| 1   | hopeless  | 0.95              |
| 2   | lonely    | 0.92              |
| 3   | worthless | 0.90              |

### normal_words

| id  | word      | probability_score |
| --- | --------- | ----------------- |
| 1   | happy     | 0.92              |
| 2   | excited   | 0.87              |
| 3   | motivated | 0.85              |

### stop_words

| id  | word |
| --- | ---- |
| 1   | the  |
| 2   | is   |
| 3   | and  |

## Technologies Used

| Technology             | Purpose            |
| ---------------------- | ------------------ |
| FastAPI                | API framework      |
| Uvicorn                | Application server |
| MySQL                  | Database           |
| Scikit-learn           | Machine learning   |
| Pandas                 | Data processing    |
| Pydantic               | Data validation    |
| mysql-connector-python | MySQL connectivity |

## Frontend Integration

Example request from JavaScript:

```javascript
const response = await fetch("http://localhost:8000/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    sentence: userInput,
  }),
});

const result = await response.json();
console.log(result);
```

## Troubleshooting

### Cannot connect to MySQL

- Verify MySQL is running.
- Check database credentials.
- Ensure the database has been created.

### No module named 'fastapi'

```bash
pip install -r requirements.txt
```

### CORS errors

Update the allowed origins in the FastAPI CORS configuration and restart the server.

## Learning Objectives

This project demonstrates:

- FastAPI backend development
- REST API design
- MySQL integration with Python
- Text preprocessing
- Naive Bayes sentiment classification
- Frontend-to-backend communication

## License

This project is intended for educational and learning purposes.
