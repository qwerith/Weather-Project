import unittest
from mailing import send_gmail
from app import track
from flask import Flask, redirect, request, session, render_template, flash, url_for

class Mailing_Test(unittest.TestCase):

    def test_smtplib_work(self):
        message = "It works!!!"
        receiver = "yuriisorokin98@gmail.com"
        self.assertEqual(send_gmail(message, receiver), None)

    def test_cron_job(self):
        pass

    #def test_db_query(self):
        #pass

    def test_endpoint_response(self):
        self.assertEqual(track(), redirect("/"))

    #def test_db_update(self):
        #pass

if __name__=='__main__':
    unittest.main()