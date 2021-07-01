import urllib3, requests, bs4, sys, os, json, datetime, re
#from bs4 import BeautifulSoup
# import flask
# from flask import Flask, url_for
# from flask import render_template

data_path = r"C:\Users\Yura\Documents\weather project\data\ "
API_KEY = os.getenv("WEATHER_KEY")
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


def input_handler():
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


def get_weather(API_KEY):
    #try:
    location_input = input_handler()
    print(location_input)
    #except: TypeError("Invalid input")
    url = f"http://api.openweathermap.org/data/2.5/forecast?{location_input}&units=metric&appid={API_KEY}"
    request = requests.get(url)
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
        cach = Cache(location, coords)
        cach.write(request)
        cach.read()
    return request


class Cache():

    def __init__(self, location_name, coords):
        self.location_name = location_name
        self.coords = coords
    
    def write(self, request_data):
        location_name = self.location_name
        coords = self.coords
        file_name = location_name + " " + coords + ".text"
        f = open(data_path.rstrip(" ") + file_name, "w")
        json.dump(request_data, f)
        f.close()
    
    def read(self):
        location_name = self.location_name
        coords = self.coords
        dev_file = json.load((open(data_path.rstrip(" ") + location_name + " " + coords + ".text", "r")))
        print(json.dumps(dev_file, indent = 4, sort_keys=True))


resault = get_weather(API_KEY)
