-- Mental Health Sentiment Analysis System - Database Setup Script
-----------------------------------------------------------------------------------------------------------
-- Create the database and select it
CREATE DATABASE IF NOT EXISTS mental_health_db;
USE mental_health_db;
-----------------------------------------------------------------------------------------------------------
-- Create stop_words table
-- Columns:
--   - id
--   - word(unique)
CREATE TABLE IF NOT EXISTS stop_words(
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    INDEX idx_word(word)
);
INSERT INTO stop_words(word)
VALUES -- Articles
    ('a'),
    ('an'),
    ('the'),
    -- Conjunctions (Coordinating)
    ('and'),
    ('or'),
    ('but'),
    ('yet'),
    ('nor'),
    ('so'),
    ('for'),
    -- Conjunctions (Subordinating)
    ('because'),
    ('although'),
    ('though'),
    ('if'),
    ('unless'),
    ('while'),
    ('when'),
    ('whenever'),
    ('where'),
    ('wherever'),
    ('since'),
    ('until'),
    ('whether'),
    ('before'),
    ('after'),
    ('as'),
    ('whereas'),
    ('lest'),
    ('provided'),
    ('that'),
    ('once'),
    ('above'),
    ('below'),
    ('between'),
    ('under'),
    ('again'),
    ('further'),
    ('then'),
    ('once'),
    -- Pronouns
    ('i'),
    ('you'),
    ('he'),
    ('she'),
    ('it'),
    ('we'),
    ('they'),
    ('me'),
    ('him'),
    ('her'),
    ('us'),
    ('them'),
    ('my'),
    ('your'),
    ('his'),
    ('her'),
    ('its'),
    ('our'),
    ('their'),
    ('mine'),
    ('yours'),
    ('hers'),
    ('ours'),
    ('theirs'),
    ('this'),
    ('that'),
    ('these'),
    ('those'),
    -- Auxiliary verbs
    ('am'),
    ('is'),
    ('are'),
    ('was'),
    ('were'),
    ('be'),
    ('been'),
    ('being'),
    ('have'),
    ('has'),
    ('had'),
    ('do'),
    ('does'),
    ('did'),
    ('will'),
    ('would'),
    ('could'),
    ('should'),
    ('may'),
    ('might'),
    ('must'),
    ('can'),
    -- Other common words
    ('just'),
    ('only'),
    ('not'),
    ('no'),
    ('than'),
    ('too'),
    ('very'),
    ('each'),
    ('such'),
    ('which'),
    ('who'),
    ('what'),
    ('why'),
    ('how'),
    ('all'),
    ('some'),
    ('any'),
    ('few'),
    ('many'),
    ('most'),
    ('other'),
    ('same'),
    ('more'),
    ('less'),
    ('down'),
    ('out'),
    ('off'),
    ('over'),
    ('own'),
    ('both'),
    ('here'),
    ('there'),
    ('now'),
    ('then'),
    ('however'),
    ('therefore'),
    ('thus'),
    ('hence'),
    ('also'),
    ('else') ON DUPLICATE KEY
UPDATE word =
VALUES(word);
-----------------------------------------------------------------------------------------------------------
-- Create depressed_words table
-- Columns:
--   - id (auto-increments)
--   - word (must be unique)
--   - probability_score (0.0-1.0)
CREATE TABLE IF NOT EXISTS depressed_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    probability_score FLOAT NOT NULL
);
INSERT INTO depressed_words (word, probability_score)
VALUES ('hopeless', 0.95),
    ('depressed', 0.95),
    ('suicidal', 0.98),
    ('lonely', 0.92),
    ('worthless', 0.90),
    ('miserable', 0.93),
    ('despair', 0.96),
    ('sad', 0.88),
    ('unhappy', 0.86),
    ('anxious', 0.82),
    ('stressed', 0.80),
    ('worried', 0.79),
    ('scared', 0.85),
    ('frustrated', 0.75),
    ('disappointed', 0.74),
    ('tired', 0.70),
    ('confused', 0.65),
    ('empty', 0.89),
    ('numb', 0.87),
    ('broken', 0.84),
    ('pain', 0.83),
    ('struggle', 0.81),
    ('fail', 0.78),
    ('weak', 0.76),
    ('helpless', 0.91) ON DUPLICATE KEY
UPDATE probability_score =
VALUES(probability_score);
-- Create normal_words table
-- Columns:
--   - id (auto-increments)
--   - word (must be unique)
--   - probability_score (0.0-1.0)
CREATE TABLE IF NOT EXISTS normal_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    probability_score FLOAT NOT NULL,
);
INSERT INTO normal_words (word, probability_score)
VALUES ('happy', 0.92),
    ('wonderful', 0.93),
    ('excellent', 0.94),
    ('amazing', 0.91),
    ('fantastic', 0.90),
    ('love', 0.88),
    ('beautiful', 0.85),
    ('excited', 0.87),
    ('energetic', 0.86),
    ('motivated', 0.85),
    ('confident', 0.84),
    ('strong', 0.82),
    ('powerful', 0.81),
    ('joyful', 0.89),
    ('peaceful', 0.80),
    ('calm', 0.78),
    ('grateful', 0.86),
    ('blessed', 0.87),
    ('proud', 0.83),
    ('great', 0.80),
    ('good', 0.75),
    ('nice', 0.72),
    ('helpful', 0.79),
    ('kind', 0.81),
    ('hopeful', 0.88),
    ('positive', 0.84),
    ('brave', 0.82),
    ('smart', 0.80),
    ('successful', 0.83) ON DUPLICATE KEY
UPDATE probability_score =
VALUES(probability_score);
-- ============================================================================
-- Verification Queries
-- ============================================================================
SELECT 'DEPRESSED WORDS' AS `Table`;
SELECT COUNT(*) AS 'Total Words'
FROM depressed_words;
SELECT word,
    probability_score
FROM depressed_words
ORDER BY probability_score DESC
LIMIT 10;
SELECT '\nNORMAL WORDS' AS `Table`;
SELECT COUNT(*) AS 'Total Words'
FROM normal_words;
SELECT word,
    probability_score
FROM normal_words
ORDER BY probability_score DESC
LIMIT 10;
SELECT '\nSTOP WORDS' AS `Table`;
SELECT COUNT(*) AS 'Total Words'
FROM stop_words;
SELECT word
FROM stop_words
LIMIT 20;
-- ============================================================================
-- END OF SETUP SCRIPT
-- ============================================================================