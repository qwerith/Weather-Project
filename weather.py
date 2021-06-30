import urllib3, requests, bs4, sys, os, json, datetime, re
#from bs4 import BeautifulSoup
# import flask
# from flask import Flask, url_for
# from flask import render_template

data_directory = r"C:\Users\Yura\Documents\weather project\data\ "
API_KEY = os.getenv("WEATHER_KEY")
if not API_KEY:
    raise RuntimeError("API key error")


def input_handler():
    location = input("Enter location name: ")
    pattern = '.*(\d{4,}).*(\d{4,}).*'
    pattern_replace = "[^-1234567890]"
    if len(location) > 30 or len(location) <= 2:
        location = "Lviv"
    elif not re.search(pattern, location):
        location = "q=" + location
        print(location)
    else: 
        location = re.sub(pattern_replace,'',location)
        print(location)
        strlen = int((len(location)/2))
        lat = str(location[0 : strlen ])
        lat = "lat=" + re.sub(r'(\d\d)(\d*)', r'\1.\2', lat)
        lon = str(location[strlen : ])
        lon = "&lon=" + re.sub(r'(\d\d)(\d*)', r'\1.\2', lon)
        location = lat + lon
        print(lat, "\n",lon)
    return location


def get_weather(API_KEY):
    try:
        location = input_handler()
        print(location)
    except: TypeError("Invalid input")
    url = f"http://api.openweathermap.org/data/2.5/forecast?{location}&units=metric&appid={API_KEY}"
    request = requests.get(url)
    print(request.status_code)
    if request.status_code != 200:
        raise RuntimeError("Request failed", request.status_code)
    else:
        file_name = location[2: ] + ".text"
        f = open(data_directory + file_name, "w")
        json.dump(request.json(), f)
        f.close()
        request = request.json()
    return request


resault = get_weather(API_KEY)

place_name = resault["city"]["name"]
dev_file = json.load((open(data_directory + place_name  + ".text", "r")))
print(json.dumps(dev_file, indent = 4, sort_keys=True))
