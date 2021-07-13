import os, re, psycopg2
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

#loading environment variables
try:
    load_dotenv(find_dotenv())
    con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("db_PASSWORD"))
    cur = con.cursor()
except: raise RuntimeError("Database credentials error")

#checks whether input is location name or location coordinates
#uses "pattern" to define whether input coincides with coordinates, example: """chars(49.3580)chars(23.5123)chars"""
def input_type_check(location):
    pattern = '.*(\d{2,}).*(\d{2,}).*'
    return "name" if not re.search(pattern, location) else "coords"

#compares "request_date" from "location" table with current utc date
#if "request_date" older then 12 hours(roughly), returns None(means outdated)
def upd_check(file_time):
    fmt = '%Y-%m-%d %H:%M:%S'
    current_date = datetime.now().strftime(fmt)
    current_date = datetime.strptime(current_date, fmt)
    difference = current_date - file_time if current_date > file_time else file_time - current_date
    dif_in_hours = int((difference.total_seconds()/ 60) / 60)
    print(current_date)
    print(file_time)
    print(dif_in_hours)
    return None if dif_in_hours >= 12 else True

#queries "location" table for "request_date" and "location_id"
#returns output dapanding on data status(True/None,""/"outdated"/"not_exists", id(if data exists and UPD))
def cache_check(location):
    if input_type_check(location) == "name":
        location = location[2: ]
        query = "SELECT request_date, id FROM location WHERE location_name = %s"
        parameters = (location,)
    else:
        query = "SELECT request_date, id FROM location WHERE lat = %s AND lon = %s"
        lat = location.split("&")[0].split("=")[1]
        lon = location.split("&")[1].split("=")[1]
        parameters = (lat,lon)
    try:
        cur.execute(query,parameters)
        timestamp_id = cur.fetchall()
        con.commit()
    except: raise RuntimeError("Query failed")
    try:
        if upd_check(timestamp_id[0][0]):
            return (True,"",timestamp_id[0][1])
        return (None, "outdated")
    except: return (None, "not_exists")

    