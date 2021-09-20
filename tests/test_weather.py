import unittest
from weather import *
from datetime import datetime
from unittest import mock
from unittest.mock import patch
from requests.models import Response

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
'Lat': '50.4333', 'Lon': '30.5167', 'country': 'UA', 'sunrise': '1631763305', 'sunset': '1631808644', 'timezone': '3', 'pop': 0.0})]]
            
class Weather_Test(unittest.TestCase):

    def test_convert_location_to_query(self):
      self.assertEqual(type(convert_location_to_query("lviv")), str)
      self.assertEqual(convert_location_to_query("test"), "q=Test")
      self.assertEqual(convert_location_to_query("""sdasddsds#"""), "q=Sdasddsds#")
    
    def test_get_input(self):
      self.assertEqual(get_input(None), "q=Lviv")
      self.assertEqual(get_input("test"), "q=Test")
      self.assertEqual(get_input(1), "q=Lviv")
      self.assertEqual(get_input(123445), "q=Lviv")
      self.assertEqual(get_input("""'Drohobych' );  DROP TABLE locations; --' )"""), "q='drohobych' );  drop table locations; --' )")
    
    # requires empty db to run correctly
    def test_get_weather(self):
      mock_response = Response()
      mock_response.status_code = 200
      mock_response._content = str(data)
      mock_response_bad = Response()
      mock_response_bad.status_code = 401
      mock_response_bad._content = None
      with mock.patch("weather.requests", return_value=mock_response):
        self.assertEqual(type(get_weather("Lviv")), list)
      with mock.patch("weather.requests", return_value=mock_response_bad):
        self.assertEqual(type(get_weather("Rome")), RuntimeError)
      self.assertEqual(type(get_weather("""'Drohobych' );  DROP TABLE locations; --' )""")), RuntimeError)
    
    def test_write_location(self):
      self.assertRaises(Exception, Cache.write_location, 1, 1)
      self.assertRaises(Exception, Cache.write_location, data, "Kyiv")

    def test_parse_api_response(self):
      self.assertEqual(type(Cache.parse_api_response(data)), list)
      self.assertEqual(Cache.parse_api_response(data), [[1596564000, 293.55, 294.05, 84, 'light rain', 309, '10d', 4.35, 0.49]])
    
    def test_parse_database_response(self):
      self.assertEqual(type(Cache.parse_database_response(query_result)), list)
      self.assertEqual(Cache.parse_database_response(query_result), final_data_list)
    
    def test_read(self):
      self.assertEqual(Cache.read(2132312312312), [])
      self.assertEqual(type(Cache.read("sddssd")), RuntimeError)


if __name__=='__main__':
    unittest.main()
    