import unittest
from mailing import *
from unittest import mock
from unittest.mock import patch

data = [[('2021-09-15 15:00:00', {'min_temp': '21.59', 'max_temp': '21.64', 'humidity': '50', 'conditions': 'few clouds',
         'picture_name': '02d', 'wind': '159', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424',
          'country': 'UA', 'sunrise': '1631678045', 'sunset': '1631723631', 'timezone': '3', 'pop': 0.0})]]

data_short = []
data_dict = {}

class Mailing_Test(unittest.TestCase):

    def test_send_gmail(self):
        message = "It works!!!"
        receiver = "yuriisorokin98@gmail.com"
        with mock.patch("mailing.smtplib", return_value=200):
            self.assertEqual(send_gmail(message, receiver), None)
        
    def test_create_html_table_rows(self):
        self.assertEqual(type(create_html_table_rows(data)), list)

    def test_day_of_week(self):
        self.assertEqual(type(day_of_week("2021-09-19 21:00:00")), tuple)
        self.assertEqual(day_of_week("2021-09-19 21:00:00"), ('Sunday', '19', 'September'))
        self.assertEqual(day_of_week("12321231232"), "12321231232")
        self.assertEqual(day_of_week(1), 1)
        
    def test_set_up_track(self):
        self.assertEqual(set_up_track(-1, -2), None)
    
    def test_stop_tracking(self):
        self.assertEqual(stop_tracking("1"), None)
    
    def test_compose_weather_mail_msg(self):
        self.assertEqual(type(compose_weather_mail_msg(data)), list)
    
    def test_raises_compose_weather_mail_msg(self):
        self.assertRaises(IndexError, compose_weather_mail_msg, data_short)
        self.assertRaises(TypeError, compose_weather_mail_msg, data_dict)
    
    def test_compose_recovery_mail_msg(self):
        self.assertEqual(type(compose_recovery_mail_msg("12345")), list)
    
    def test_query_mailing_table(self):
        self.assertEqual(type(query_mailing_table()), list)

if __name__=='__main__':
    unittest.main()