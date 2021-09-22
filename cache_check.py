import os, re, psycopg2, logging
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s")
handler = logging.FileHandler("logs.log")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

#loading environment variables
try:
    load_dotenv(find_dotenv())
    con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("db_PASSWORD"), port = 5431)
    cur = con.cursor()
except psycopg2.OperationalError as e:
    logger.exception("Database credentials error")
    raise RuntimeError("Database credentials error") from e

#checks whether input is location name or location coordinates
#uses "pattern" to define whether input coincides with coordinates, example: """chars(49.3580)chars(23.5123)chars"""
def input_type_check(location):
    pattern = '.*(\d{2,}).*(\d{2,}).*'
    return "name" if not re.search(pattern, location) else "coords"

#compares "request_date" from "location" table with current utc date
#if "request_date" older then 12 hours(roughly), returns None(means outdated)
def upd_check(file_time):
    fmt = '%Y-%m-%d %H:%M:%S'
    current_date = datetime.utcnow().strftime(fmt)
    current_date = datetime.strptime(current_date, fmt)
    difference = current_date - file_time if current_date > file_time else file_time - current_date
    dif_in_hours = int((difference.total_seconds()/ 60) / 60)
    print(current_date)
    print(file_time)
    print(dif_in_hours)
    return None if dif_in_hours >= 6 else True

#queries "location" table for "request_date" and "location_id"
#returns output dapanding on data status(True/None,""/"outdated"/"not_exists", id(if data exists and UPD))
def cache_check(location):
    if input_type_check(location) == "name":
        parameters = (location[2: ],)
        query = "SELECT request_date, id FROM location WHERE location_name = %s"
    else:
        query = "SELECT request_date, id FROM location WHERE lat = %s AND lon = %s"
        parameters = (location.split("&")[0].split("=")[1], location.split("&")[1].split("=")[1])
    try:
        cur.execute(query,parameters)
        timestamp_id = cur.fetchall()
        con.commit()
    except RuntimeError:
        logger.exception(f"Query failed: {query}{parameters}")
        raise
    try:
        if upd_check(timestamp_id[0][0]):
            return (True,"",timestamp_id[0][1])
        return (None, "outdated")
    except:
        logger.warning(Exception)
        return (None, "not_exists")

def check_by_id(id):
    query = "SELECT EXISTS(SELECT 1 FROM location WHERE id = %s LIMIT 1)"
    cur.execute(query,(id, ))
    con.commit()
    exists = cur.fetchall()
    if exists[0][0] == False:
        return None
    return True


    