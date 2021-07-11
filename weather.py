import requests, os, json, re, psycopg2
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
# import flask
# from flask import Flask, url_for
# from flask import render_template

load_dotenv(find_dotenv())
con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("db_PASSWORD"))
cur = con.cursor()
#cur.execute("SELECT id,username,email FROM users LIMIT 5")
#rows = cur.fetchall()
#cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", ("Yurii","yurii@gmail.com","qwerty"))
#for r in rows:
    #print(f"id {r[0]} |username {r[1]} |email {r[2]}")
#con.commit()

data_path = os.path.join("C:", os.sep, "Users", "Yura", "Documents", "weather project", "data","")
API_KEY = os.getenv("OWM_KEY")
if not API_KEY:
    raise RuntimeError("API key error")


def input_type_check(location):
    pattern = '.*(\d{2,}).*(\d{2,}).*'
    return "name" if not re.search(pattern, location) else "coords"


def string_handler(location):
    pattern_replace = "[^. -1234567890]"
    if input_type_check(location) == "name":
        location = "q=" + location
    else:
        location = re.sub(pattern_replace,'',location)
        location = (re.sub(r'''[,'"!@#$%^&*()_+=|/?>,<`~]''',"", location)).lstrip(" ").rstrip(" ").split(" ")
        lat = "lat=" + str(location[0])
        lon = "&lon=" + str(location[-1])
        location = lat + lon
    return location


def get_input():
    location = input("Enter location name: ")
    if len(location) > 30 or len(location) <= 2:
        location = "q=Lviv"
    else:
        location = string_handler(location)
    return location


def get_coords_or_name(location, request):
    pattern = '.*(\d{2,}).*(\d{2,}).*'
    if re.search(pattern, location):
        location = request["city"]["name"]
    else:
        location = str(request["city"]["coord"])
        location = string_handler(location)
    return location


def upd_check(file_time):
    fmt = '%Y-%m-%d %H:%M:%S'
    current_date = datetime.now().strftime(fmt)
    current_date = datetime.strptime(current_date, fmt)
    file_time = file_time[0][0]
    difference = current_date - file_time if current_date > file_time else file_time - current_date
    dif_in_hours = int((difference.total_seconds()/ 60) / 60)
    print(current_date)
    print(file_time)
    print(dif_in_hours)
    return None if dif_in_hours >= 12 else True


def cache_check(location):
    if input_type_check(location) == "name":
        location = location[2: ]
        query = "SELECT request_date FROM location WHERE location_name = %s"
        parameters = (location,)
    else:
        query = "SELECT request_date FROM location WHERE lon = %s AND lat = %s"
        lon = location.split("&")[0].split("=")[1]
        lat = location.split("&")[1].split("=")[1]
        parameters = (lon,lat)
    try:
        cur.execute(query,parameters)
        timestamp = cur.fetchall()
        con.commit()
        if upd_check(timestamp):
            return (True, )
        return (None, "outdated")
    except: return (None, "not_exists")
    

def get_weather(API_KEY):
    try:
        location_input = get_input()
        print(location_input)
    except: TypeError("Invalid input")
    check = cache_check(location_input) 
    if check[0] == None:
        request = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?{location_input}&units=metric&appid={API_KEY}")
        print(request.status_code)
        if request.status_code != 200:
            raise RuntimeError("Request failed", request.status_code)
        else:
            request = request.json()
            con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("db_PASSWORD"))
            cur = con.cursor()
            cache = Cache()
            if check[1] == "not_exists":
                cache.create(request, location_input)
            cache.write(request)
            #cache.read()
            cur.close()
            con.close()
    else:
        print("TODO")
        cache = Cache()
        #cache.read()
        

class Cache():

    def __init__(self):
        print()

    def create(self, request_data, location_input):
        if input_type_check(location_input) == "coords":
            location_name = get_coords_or_name(location_input, request_data)
            coords = location_input
        else:
            coords = get_coords_or_name(location_input, request_data)
            location_name = location_input[2: ]
        db_location = [request_data["city"]["id"], location_name, coords.split("&")[0].split("=")[1], 
        coords.split("&")[1].split("=")[1], datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')]
        cur.execute("INSERT INTO location (id, location_name, lat, lon, request_date) VALUES (%s, %s, %s, %s, %s)",
        (db_location[0], db_location[1], db_location[2], db_location[3], db_location[4]))
        con.commit()

    def parse_response(self, request_data):
        db_weather = []
        paremeters = [["dt"], ["main","temp_min"], ["main","temp_max"],["main","humidity"],
        ["weather", 0,"description"], ["wind", "deg"], ["weather", 0, "icon"], ["wind", "speed"]]
        for i in request_data["list"]:
            temp_list = []
            for p in paremeters:
                length = len(p)
                if length == 2:
                    temp_list.append(i[p[0]][p[1]]) 
                elif length == 3:
                    temp_list.append(i[p[0]][p[1]][p[2]]) 
                else:
                    temp_list.append(i[p[0]]) 
            db_weather.append(temp_list)
        return db_weather

    def write(self, request_data):
        count = 0
        command = """INSERT INTO weather (date, min_temp, max_temp, humidity, conditions, wind, picture_name, location_id, wind_speed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        location_id = request_data["city"]["id"]
        db_weather = self.parse_response(request_data)
        exists = cur.execute("SELECT EXISTS(SELECT 1 FROM weather WHERE location_id = %s LIMIT 1)",(location_id,))
        cur.fetchall()
        print(exists)
        if exists == True:
            cur.execute("DELETE FROM weather WHERE location_id=%s",(location_id,))
            cur.execute(f"UPDATE location SET request_date = %s WHERE id = {location_id}", [(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))])
        for i in db_weather:
            cur.execute(command,(datetime.fromtimestamp(db_weather[count][0]), db_weather[count][1], db_weather[count][2],
            db_weather[count][3], db_weather[count][4], db_weather[count][5], db_weather[count][6], location_id, db_weather[count][7]))
            count += 1
        con.commit()
    
    def read(self):
        dev_file = json.load((open(data_path + self.location_name + " " + self.coords + ".text", "r")))
        #print(json.dumps(dev_file, indent = 4, sort_keys=True))
        

resault = get_weather(API_KEY)
