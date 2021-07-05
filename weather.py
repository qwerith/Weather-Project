import requests, os, json, re
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
# import flask
# from flask import Flask, url_for
# from flask import render_template

data_path = os.path.join("C:", os.sep, "Users", "Yura", "Documents", "weather project", "data","")
load_dotenv(find_dotenv())
API_KEY = os.getenv("OWM_KEY")
if not API_KEY:
    raise RuntimeError("API key error")


def input_type_check(location):
    pattern = '.*(\d{2,}).*(\d{2,}).*'
    if not re.search(pattern, location):
        return "name"
    else:
        return "coords"


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
    file_time = datetime.strptime(file_time, fmt)
    difference = current_date - file_time if current_date > file_time else file_time - current_date
    dif_in_hours = int((difference.total_seconds()/ 60) / 60)
    if dif_in_hours >= 12:
        resault = None
    else:
        resault = True
    print(current_date)
    print(file_time)
    print(dif_in_hours)
    return resault


def cache_check(location):
    if input_type_check(location) == "name":
        location = location[2: ]
        for x in os.listdir(data_path):
            if x.split(" ")[0] == location:
                f = json.load(open(data_path + x, "r"))
                timestamp = f["list"][0]["dt_txt"]
                if upd_check(timestamp):
                    coords = re.sub(r'.text','', x.split(" ")[1])
                    cache = Cache(location, coords)
                    cache.read()
                    return True
        return None 
    else:
        for x in os.listdir(data_path):
            if re.sub(r'.text','', x.split(" ")[1]) == location:
                f = json.load(open(data_path + x, "r"))
                timestamp = f["list"][0]["dt_txt"]
                if upd_check(timestamp):
                    location_name = x.split(" ")[0]
                    cache = Cache(location_name, location)
                    cache.read()
                    return True
        return None 


def get_weather(API_KEY):
    #try:
    location_input = get_input()
    print(location_input)
    #except: TypeError("Invalid input")
    if cache_check(location_input) == None:
        request = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?{location_input}&units=metric&appid={API_KEY}")
        print(request.status_code)
        if request.status_code != 200:
            raise RuntimeError("Request failed", request.status_code)
        else:
            request = request.json()
            if input_type_check(location_input) == "coords":
                location = get_coords_or_name(location_input, request)
                coords = location_input
            else:
                coords = get_coords_or_name(location_input, request)
                location = location_input[2: ]
                print(coords)
            cache = Cache(location, coords)
            cache.write(request)
            cache.read()
    else:
        request = None
    return request


class Cache():

    def __init__(self, location_name, coords):
        self.location_name = location_name
        self.coords = coords
    
    def write(self, request_data):
        location_name = self.location_name
        coords = self.coords
        file_name = location_name + " " + coords + ".text"
        f = open(data_path + file_name, "w")
        json.dump(request_data, f)
        f.close()
    
    def read(self):
        location_name = self.location_name
        coords = self.coords
        dev_file = json.load((open(data_path + location_name + " " + coords + ".text", "r")))
        print(json.dumps(dev_file, indent = 4, sort_keys=True))


resault = get_weather(API_KEY)
