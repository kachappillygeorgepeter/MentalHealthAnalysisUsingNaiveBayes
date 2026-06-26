UPDATE emotional_words
SET
    happy_count = 0, happy_score = 0.0,
    sad_count = 0, sad_score = 0.0,
    confused_count = 0, confused_score = 0.0,
    angry_count = 0, angry_score = 0.0,
    fear_count = 0, fear_score = 0.0,
    disgust_count = 0, disgust_score = 0.0,
    neutral_count = 0, neutral_score = 0.0
WHERE id >= 0;

UPDATE message_emotion_probabilities
SET
    probability = 0.0,
    `count` = 0
WHERE id >= 0;

SELECT *
FROM emotional_words;

SELECT *
FROM message_emotion_probabilities;
