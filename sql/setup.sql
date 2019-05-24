CREATE TYPE hall AS ENUM ('Covel', 'Bruin Plate', 'De Neve', 'FEAST', 'Bruin Café', 'Café 1919', 'Rendezvous', 'The Study at Hedrick');
CREATE TYPE mealtime AS ENUM('Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Late Night');

CREATE TABLE IF NOT EXISTS food(
    food_id SERIAL UNIQUE,
    name VARCHAR(120) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS groups(
    group_id VARCHAR(20),
    bot_id VARCHAR(30),
    notify BOOLEAN,
    PRIMARY KEY (group_id)
);

CREATE TABLE IF NOT EXISTS menu(
    day DATE DEFAULT NOW(),
    dining_hall hall,
    meal mealtime,
    food_id INT,
    FOREIGN KEY (food_id) REFERENCES food(food_id),
    PRIMARY KEY (day, dining_hall, meal, food_id)
);

CREATE TABLE IF NOT EXISTS tracked_items(
    group_id VARCHAR(20),
    food_id INT,
    PRIMARY KEY (group_id, food_id),
    FOREIGN KEY (food_id) REFERENCES food(food_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);

CREATE TABLE IF NOT EXISTS hours(
    meal mealtime,
    hour VARCHAR(20),
    hall hall,
    day DATE DEFAULT NOW(),
    PRIMARY KEY (meal, hour, day, hall)
);

CREATE TABLE IF NOT EXISTS temporary_queries(
    token VARCHAR(10),
    group_id VARCHAR(20),
    food_id INTEGER,
    time TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (token)
);


CREATE SCHEMA IF NOT EXISTS auth;

CREATE TYPE auth.permissions AS ENUM ('admin', 'cron', 'developer');
CREATE EXTENSION "uuid-ossp";

CREATE TABLE IF NOT EXISTS auth.users(
    username VARCHAR(50) UNIQUE NOT NULL,
    user_id SERIAL PRIMARY KEY,
    token uuid NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    date_joined timestamptz DEFAULT NOW(),
    permission auth.permissions
);

