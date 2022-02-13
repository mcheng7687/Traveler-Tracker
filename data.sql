DROP DATABASE IF EXISTS  traveler_tracker;
CREATE DATABASE traveler_tracker;

\c traveler_tracker

DROP TABLE IF EXISTS country;
CREATE TABLE country
(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  currency_code TEXT
);

DROP TABLE IF EXISTS city;
CREATE TABLE city
(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  country_id INTEGER REFERENCES country(id)
);

DROP TABLE IF EXISTS traveler;
CREATE TABLE traveler
(
  id SERIAL PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  home_country INTEGER REFERENCES country(id)
);

DROP TABLE IF EXISTS traveler_city;
CREATE TABLE traveler_city
(
  traveler_id PRIMARY KEY REFERENCES traveler(id) ON DELETE CASCADE,
  country_id PRIMARY KEY REFERENCES country(id) ON DELETE CASCADE
);