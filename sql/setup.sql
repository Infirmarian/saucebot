CREATE SCHEMA IF NOT EXISTS dining;

CREATE TYPE dining.hall AS ENUM ('Covel', 'Bruin Plate', 'De Neve', 'FEAST', 'Bruin Café', 'Café 1919', 'Rendezvous', 'The Study at Hedrick');
CREATE TYPE dining.mealtime AS ENUM('Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Late Night');


CREATE TABLE IF NOT EXISTS dining.food(
    food_id SERIAL UNIQUE,
    name VARCHAR(120) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS dining.groups(
    group_id VARCHAR(20),
    bot_id VARCHAR(30),
    notify BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (group_id)
);

CREATE TABLE IF NOT EXISTS dining.menu(
    day DATE DEFAULT NOW(),
    dining_hall dining.hall,
    meal dining.mealtime,
    food_id INT,
    FOREIGN KEY (food_id) REFERENCES dining.food(food_id),
    PRIMARY KEY (day, dining_hall, meal, food_id)
);

CREATE TABLE IF NOT EXISTS dining.tracked_items(
    group_id VARCHAR(20),
    food_id INT,
    PRIMARY KEY (group_id, food_id),
    FOREIGN KEY (food_id) REFERENCES dining.food(food_id),
    FOREIGN KEY (group_id) REFERENCES dining.groups(group_id)
);

CREATE TABLE IF NOT EXISTS dining.hours(
    meal dining.mealtime,
    hour VARCHAR(20),
    hall dining.hall,
    day DATE DEFAULT NOW(),
    PRIMARY KEY (meal, hour, day, hall)
);

CREATE TABLE IF NOT EXISTS dining.temporary_queries(
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

