-- ============================================================================
-- Mental Health Sentiment Analysis System - Database Setup Script
-- ============================================================================
--
-- This SQL script sets up the entire database for the backend API.
-- 
-- How to use this file:
-- 1. Open MySQL Command Line or MySQL Workbench
-- 2. Open this file or copy its contents
-- 3. Execute all queries
-- 4. Verify that the data was inserted correctly
--
-- ============================================================================

-- Step 1: Create the database
-- ============================================================================
CREATE DATABASE IF NOT EXISTS mental_health_db;

-- Select the database
USE mental_health_db;

-- Step 2: Create depressed_words table
-- ============================================================================
-- This table stores words that indicate depression and their probability scores.
-- 
-- Columns:
--   - id: Unique identifier (auto-increments)
--   - word: The sentiment word (must be unique)
--   - probability_score: How strongly this word indicates depression (0.0 to 1.0)
--
-- Example:
--   "lonely" with score 0.90 means this word is 90% likely to indicate depression

CREATE TABLE IF NOT EXISTS depressed_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    probability_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample depressed words with probability scores
INSERT INTO depressed_words (word, probability_score) VALUES
-- Strong depression indicators
('hopeless', 0.95),
('depressed', 0.95),
('suicidal', 0.98),
('lonely', 0.92),
('worthless', 0.90),
('miserable', 0.93),
('despair', 0.96),

-- Common negative emotions
('sad', 0.88),
('unhappy', 0.86),
('anxious', 0.82),
('stressed', 0.80),
('worried', 0.79),
('scared', 0.85),
('frustrated', 0.75),
('disappointed', 0.74),

-- Other depression-related words
('tired', 0.70),
('confused', 0.65),
('empty', 0.89),
('numb', 0.87),
('broken', 0.84),
('pain', 0.83),
('struggle', 0.81),
('fail', 0.78),
('weak', 0.76),
('helpless', 0.91)
ON DUPLICATE KEY UPDATE probability_score = VALUES(probability_score);

-- Step 3: Create normal_words table
-- ============================================================================
-- This table stores words that indicate normal/positive sentiment and their scores.
-- 
-- Columns:
--   - id: Unique identifier (auto-increments)
--   - word: The sentiment word (must be unique)
--   - probability_score: How strongly this word indicates normal/positive mood
--
-- Example:
--   "happy" with score 0.85 means this word is 85% likely to indicate normal mood

CREATE TABLE IF NOT EXISTS normal_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    probability_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample normal/positive words with probability scores
INSERT INTO normal_words (word, probability_score) VALUES
-- Strong positive words
('happy', 0.92),
('wonderful', 0.93),
('excellent', 0.94),
('amazing', 0.91),
('fantastic', 0.90),
('love', 0.88),
('beautiful', 0.85),

-- Energy and motivation
('excited', 0.87),
('energetic', 0.86),
('motivated', 0.85),
('confident', 0.84),
('strong', 0.82),
('powerful', 0.81),

-- Positive emotions
('joyful', 0.89),
('peaceful', 0.80),
('calm', 0.78),
('grateful', 0.86),
('blessed', 0.87),
('proud', 0.83),

-- Other positive words
('great', 0.80),
('good', 0.75),
('nice', 0.72),
('helpful', 0.79),
('kind', 0.81),
('hopeful', 0.88),
('positive', 0.84),
('brave', 0.82),
('smart', 0.80),
('successful', 0.83)
ON DUPLICATE KEY UPDATE probability_score = VALUES(probability_score);

-- Step 4: Create stop_words table
-- ============================================================================
-- This table stores common English words that don't contribute to sentiment
-- analysis and should be removed from user input before analysis.
-- 
-- Why remove stop words?
--   - Words like "the", "is", "and" appear in almost all sentences
--   - They don't tell us anything about sentiment
--   - Removing them makes analysis cleaner and more accurate
--
-- Columns:
--   - id: Unique identifier (auto-increments)
--   - word: The stop word to be filtered out

CREATE TABLE IF NOT EXISTS stop_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert common English stop words
INSERT INTO stop_words (word) VALUES
-- Articles
('a'), ('an'), ('the'),

-- Conjunctions
('and'), ('or'), ('but'), ('yet'),

-- Prepositions
('in'), ('on'), ('at'), ('to'), ('for'), ('of'), ('from'), ('with'),
('by'), ('about'), ('up'), ('into'), ('through'), ('during'),
('before'), ('after'), ('above'), ('below'), ('between'), ('under'),
('again'), ('further'), ('then'), ('once'),

-- Pronouns
('i'), ('you'), ('he'), ('she'), ('it'), ('we'), ('they'),
('me'), ('him'), ('her'), ('us'), ('them'),
('my'), ('your'), ('his'), ('her'), ('its'), ('our'), ('their'),
('mine'), ('yours'), ('hers'), ('ours'), ('theirs'),
('this'), ('that'), ('these'), ('those'),

-- Auxiliary verbs
('am'), ('is'), ('are'), ('was'), ('were'), ('be'), ('been'), ('being'),
('have'), ('has'), ('had'), ('do'), ('does'), ('did'), ('will'), ('would'),
('could'), ('should'), ('may'), ('might'), ('must'), ('can'),

-- Other common words
('just'), ('only'), ('not'), ('no'), ('nor'),
('so'), ('than'), ('too'), ('very'),
('as'), ('each'), ('such'), ('which'), ('who'),
('what'), ('when'), ('where'), ('why'), ('how'),
('all'), ('some'), ('any'), ('few'), ('many'), ('most'), ('other'),
('same'), ('more'), ('less'),
('down'), ('out'), ('off'), ('over'),
('own'), ('both'), ('while'),
('here'), ('there'), ('now'), ('then'),
('your'), ('their'), ('an'), ('is'), ('was'),
('should'), ('could'), ('would'), ('may'), ('might'),
('because'), ('however'), ('therefore'), ('thus'), ('hence'),
('also'), ('as'), ('been'), ('being'),
('whether'), ('unless'), ('while'), ('although'),
('unless'), ('if'), ('else'), ('since'), ('until')
ON DUPLICATE KEY UPDATE word = VALUES(word);

-- ============================================================================
-- Verification Queries
-- ============================================================================
--
-- Run these queries to verify that your data was inserted correctly
-- and to see the structure of your tables.
--

-- View all depressed words
SELECT 'DEPRESSED WORDS' as 'Table';
SELECT COUNT(*) as 'Total Words' FROM depressed_words;
SELECT word, probability_score FROM depressed_words ORDER BY probability_score DESC LIMIT 10;

-- View all normal words
SELECT '\nNORMAL WORDS' as 'Table';
SELECT COUNT(*) as 'Total Words' FROM normal_words;
SELECT word, probability_score FROM normal_words ORDER BY probability_score DESC LIMIT 10;

-- View all stop words
SELECT '\nSTOP WORDS' as 'Table';
SELECT COUNT(*) as 'Total Words' FROM stop_words;
SELECT word FROM stop_words LIMIT 20;

-- ============================================================================
-- Example Queries for Testing
-- ============================================================================
--
-- These queries show how the backend app will use the data
--

-- Check if a word is in the depressed_words table
SELECT word, probability_score FROM depressed_words WHERE word = 'lonely';

-- Get all depressed words with high probability (> 0.85)
SELECT word, probability_score FROM depressed_words WHERE probability_score > 0.85 ORDER BY probability_score DESC;

-- Get all normal words with high probability (> 0.85)
SELECT word, probability_score FROM normal_words WHERE probability_score > 0.85 ORDER BY probability_score DESC;

-- Check if a word is a stop word
SELECT word FROM stop_words WHERE word = 'the';

-- ============================================================================
-- OPTIONAL: Clear all data (use if you want to start fresh)
-- ============================================================================
--
-- Uncomment these lines if you want to delete all data and start over:
--
-- DELETE FROM depressed_words;
-- DELETE FROM normal_words;
-- DELETE FROM stop_words;
--
-- Or delete the entire database:
--
-- DROP DATABASE mental_health_db;
--

-- ============================================================================
-- END OF SETUP SCRIPT
-- ============================================================================

-- You can now use the database with the FastAPI backend!
-- 
-- Next steps:
-- 1. Update the DATABASE_CONFIG in app.py with your MySQL credentials
-- 2. Install Python dependencies: pip install -r requirements.txt
-- 3. Run the server: uvicorn app:app --reload
-- 4. Test the API at http://localhost:8000/docs
