CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT,
    weight NUMERIC(5,2),
    city VARCHAR(255),
    target_active_minutes_per_day INT DEFAULT 30,
    target_calories_per_day INT DEFAULT 2000
);

CREATE INDEX idx_telegram_id ON users(telegram_id);
