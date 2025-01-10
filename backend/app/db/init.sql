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

CREATE TABLE IF NOT EXISTS food_log (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    event_time TIMESTAMP WITH TIME ZONE NOT NULL,
    food_name TEXT NOT NULL,
    weight DECIMAL(6,2) CHECK (weight > 0), -- Weight in grams
    calories INTEGER CHECK (calories >= 0),
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

CREATE INDEX idx_food_log_telegram_id ON food_log(telegram_id);

CREATE TABLE IF NOT EXISTS water_log (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    event_time TIMESTAMP WITH TIME ZONE NOT NULL,
    volume INTEGER CHECK (volume > 0), -- Milliliters
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

CREATE INDEX idx_water_log_telegram_id ON water_log(telegram_id);

CREATE TABLE IF NOT EXISTS workout_log (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    event_time TIMESTAMP WITH TIME ZONE NOT NULL,
    type TEXT NOT NULL,
    length INTEGER CHECK (length > 0), -- Minutes
    calories INTEGER CHECK (calories >= 0),
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

CREATE INDEX idx_workout_log_telegram_id ON workout_log(telegram_id);
