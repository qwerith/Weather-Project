import psycopg2
import os
from dotenv import load_dotenv, find_dotenv

#loading environment variables
try:
    load_dotenv(find_dotenv())
    con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"),
                          user = os.getenv("USER"), password = os.getenv("db_PASSWORD"),
                          port = 5432)
    cur = con.cursor()
except psycopg2.OperationalError as e:
    raise RuntimeError("Database credentials error") from e

cur.execute("""CREATE TABLE location (
id serial PRIMARY KEY,
location_name char(100),
lat char(100),
lon char(100),
request_date timestamp without time zone,
country char(100),
sunrise char(100),
sunset char(100),
timezone char(100));


CREATE TABLE weather (
id serial PRIMARY KEY,
date timestamp without time zone,
min_temp char(100),
max_temp char(100),
humidity char(100),
conditions char(100),
wind char(100),
picture_name char(100),
location_id INT
  REFERENCES location(id),
wind_speed char(100),
pop double precision);


CREATE TABLE users (
id SERIAL PRIMARY KEY,
username CHAR(100),
email CHAR(100) UNIQUE,
password TEXT,
chosen_location CHAR(100));


CREATE TABLE mailing (
user_id INT,
	FOREIGN KEY (user_id)
        REFERENCES users(id),
location_id INT,
	FOREIGN KEY (location_id)
		REFERENCES location(id));

""")
con.commit()
