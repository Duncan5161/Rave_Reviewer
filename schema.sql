CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT  NOT NULL,
    gender TEXT NOT NULL
, city TEXT NOT NULL);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE clubs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
name TEXT NOT NULL,
closing_time_monday TEXT,
closing_time_tuesday TEXT,
closing_time_wednesday TEXT,
closing_time_thursday TEXT,
closing_time_friday TEXT,
closing_time_saturday TEXT,
closing_time_sunday TEXT,
main_genre TEXT NOT NULL,
user_added_by TEXT NOT NULL,
city TEXT NOT NULL,
postcode TEXT);

CREATE TABLE reviews(
id INTEGER PRIMARY KEY AUTOINCREMENT,
description TEXT NOT NULL,
club TEXT NOT NULL,
date_visited TEXT NOT NULL,
night TEXT NOT NULL,
rating_overall INTEGER,
rating_crowd INTEGER,
rating_security INTEGER,
rating_sound INTEGER,
rating_womensafety INTEGER,
created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
user_added_by TEXT NOT NULL,
comments TEXT,
DJS TEXT);
