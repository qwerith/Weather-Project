import pytest, re, logging
from datetime import datetime
from requests.models import Response


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s")
handler = logging.FileHandler("logs.log")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)
    

data = {
  "cod": "200",
  "message": 0,
  "cnt": 40,
  "list": [
    {
      "dt": 1596564000,
      "main": {
        "temp": 293.55,
        "feels_like": 293.13,
        "temp_min": 293.55,
        "temp_max": 294.05,
        "pressure": 1013,
        "sea_level": 1013,
        "grnd_level": 976,
        "humidity": 84,
        "temp_kf": -0.5
      },
      "weather": [
        {
          "id": 500,
          "main": "Rain",
          "description": "light rain",
          "icon": "10d"
        }
      ],
      "clouds": {
        "all": 38
      },
      "wind": {
        "speed": 4.35,
        "deg": 309,
        "gust": 7.87
      },
      "visibility": 10000,
      "pop": 0.49,
      "rain": {
        "3h": 0.53
      },
      "sys": {
        "pod": "d"
      },
      "dt_txt": "2020-08-04 18:00:00"
    }],

    "city": {
        "id": 2643743,
        "name": "London",
        "coord": {
        "lat": 51.5073,
        "lon": -0.1277
        },
        "country": "GB",
        "timezone": 0,
        "sunrise": 1578384285,
        "sunset": 1578413272
    }
}

query_result = [(datetime(2021, 9, 16, 15, 0), '21.29', '21.42', '46   ', 'clear sky', '01d     ', '27', '1.18  ', 703448, 'Kyiv', '50.4333     ', '30.5167', 'UA      ', '1631763305   ', '1631808644 ', '3', 0.0), (datetime(2021, 9, 15, 15, 0), '21.29', '21.42', '46   ', 'clear sky', '01d     ', '27', '1.18  ', 703448, 'Kyiv', '50.4333     ', '30.5167', 'UA      ', '1631763305   ', '1631808644 ', '3', 0.0)]
final_data_list = [[('2021-09-16 15:00:00', {'min_temp': '21.29', 'max_temp': '21.42', 'humidity': '46', 'conditions': 'clear sky', 'picture_name': '01d', 'wind': '27', 'wind_speed': 1, 'ID': 703448, 'Location': 'Kyiv', 
'Lat': '50.4333', 'Lon': '30.5167', 'country': 'UA', 'sunrise': '1631763305', 'sunset': '1631808644', 'timezone': '3', 'pop': 0.0})], [('2021-09-15 15:00:00', {'min_temp': '21.29', 'max_temp': '21.42', 
'humidity': '46', 'conditions': 'clear sky', 'picture_name': '01d', 'wind': '27', 'wind_speed': 1, 'ID': 703448, 'Location': 'Kyiv', 'Lat': '50.4333', 'Lon': '30.5167', 'country': 'UA', 'sunrise': '1631763305', 'sunset': '1631808644', 'timezone': '3', 'pop': 0.0})]]

def input_type_check(location):
    pattern = '.*(\d{2,}).*(\d{2,}).*'
    return "name" if not re.search(pattern, location) else "coords"

def convert_location_to_query(location):
    #if input is coordinates, regex uses "pattern_replace" variable to strips all characters not noted in "[^. -1234567890]"
    pattern_replace = "[^. -1234567890]"
    if input_type_check(location) == "name":
        location = "q=" + location.capitalize()
    else:
        location = re.sub(pattern_replace,'',location)
        #divides coordinates string into two parts (latitude and longitude) and strips them from all characters noted in "[,'"!@#$%^&*()_+=|/?>,<`~]"
        location = (re.sub(r'''[,'"!@#$%^&*()_+=|/?>,<`~]''',"", location)).strip(" ").split(" ")
        lat = "lat=" + str(location[0])
        lon = "&lon=" + str(location[-1])
        location = lat + lon
    logger.info(location)
    return location


def get_input(location):
    #location = input("Enter location name: ")
    if type(location) != str:
        logger.warning(location)
        return "q=Lviv"
    if len(location) > 72 or len(location) <= 2:
        location = "q=Lviv"
    else:
        location = convert_location_to_query(location)
    return location

def test_convert_location_to_query():
  result = convert_location_to_query("lviv")
  assert type(result) == str
  assert convert_location_to_query("test") == "q=Test"
  assert convert_location_to_query("""sdasddsds#""") == "q=Sdasddsds#"

def test_get_input():
  assert get_input(None) == "q=Lviv"
  assert get_input("test") == "q=Test"
  assert get_input(1) == "q=Lviv"
  assert get_input(123445) == "q=Lviv"
  assert get_input("""'Drohobych' );  DROP TABLE locations; --' )""") == "q='drohobych' );  drop table locations; --' )"
