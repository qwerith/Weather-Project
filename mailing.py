import smtplib
import os
import psycopg2
import re
import logging
from smtplib import SMTPResponseException
#from email.message import EmailMessage
from dotenv import load_dotenv, find_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("""%(asctime)s:%(name)s:
                                %(filename)s:%(funcName)s:
                                %(levelname)s:%(message)s""")
handler = logging.FileHandler("logs.log")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)


#loading environment variables
try:
    load_dotenv(find_dotenv())
    con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"),
                            user = os.getenv("USER"),password = os.getenv("db_PASSWORD"),
                            port=5432)
    cur = con.cursor()
except RuntimeError("Database credentials error"):
    logger.exception("Database credentials error")
    raise


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    logger.error("Email credentials error")
    raise RuntimeError("Credentials error")


# Inserts weather information into string for further conversion to HTML
def create_html_table_rows(data):
    length = len(data[0])
    count = -1
    html_snippets = []
    for i in range(length):
        count += 1
        if count < length:
            table_row = f"""
            <tr>
                <td style="padding: 0 10px;align-items:center;text-align:center;">
                    {data[0][count][0].split(" ")[1][:5]}</td>
                <td style="padding: 0 5%;min-width:160px;align-items:center;
                    text-align:center;">
                    {int(round(float(data[0][count][1]["min_temp"])))} 
                    / {int(round(float(data[0][count][1]["max_temp"])))}°</td>
                <td style="padding: 0 2%;align-items:center;text-align:center;">
                    {data[0][count][1]["humidity"]}%</td>
                <td style="padding: 0 5%;align-items:center;text-align:center;">
                    {int(round(float(data[0][count][1]["pop"])* 100))}%</td>
                <td style="padding: 0 10px;align-items:center;text-align:center;">
                    {data[0][count][1]["conditions"]}</td>
                <td style="padding: 0 10px;align-items:center;text-align:center;">
                    <img src="http://openweathermap.org/img/wn/{data[0][count][1]["picture_name"]}@2x.png"alt=""style="width:50px;height:50px;"></td>
                <td style="padding: 0 10px;align-items:center;text-align:center;">
                    {data[0][count][1]["wind_speed"]} m/s</td>
            </tr>
                        """
            html_snippets.append(table_row)
    # Adding "" to the list prevents index out of range error
    if length < 5:
        for i in range(5):
            html_snippets.append("")
    return html_snippets 


# Converts date to day of week, day number and month
def day_of_week(date):
    if type(date) != str:
        logger.warning(TypeError)
        return date
    try:
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        logger.warning(ValueError)
        return date
    day_number = str(date).split(" ")[0].split("-")[2]
    if day_number[0] == '0':
        day_number = day_number[1]
    day = (str(date.strftime('%A')), day_number, date.strftime("%B"))
    print(day)
    return day


# Sends email containing HTML to "receiver" address
def send_gmail(data, receiver):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "MyWeatherApp"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    #msg.set_content(body)
    text = MIMEText(data[0], 'plain')
    html = MIMEText(data[1], "html")
    msg.attach(text)
    msg.attach(html)
    #print(msg.as_string())
    #msg.add_alternative(data, subtype="html")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)        
    except SMTPResponseException as e:
        logger.exception(f"Error code:{e.smtp_code}, {e.smtp_error}")
        print("Error code:", e.smtp_code,"\n", e.smtp_error)
        return (e.smtp_code, e.smtp_error)


# Inserts into DB mailing table information for further usage in send_gmail function
def set_up_track(user_id, location_id):
    logger.info(f"Function called with {user_id}, {location_id}")
    cur.execute("""SELECT EXISTS
                    (SELECT 1 FROM mailing WHERE user_id = %s LIMIT 1)""", 
                (user_id, ))
    con.commit()
    result = cur.fetchall()
    command = "INSERT INTO mailing (location_id, user_id) VALUES (%s, %s)"
    if result[0][0] != False:
        command = "UPDATE mailing SET location_id = %s WHERE user_id = %s"
    try:
        cur.execute(command, (location_id, user_id))
        con.commit()
        return True
    except: return None


# Removes user info from mailing table
def stop_tracking(user_id):
    logger.info(f"Function called with {user_id}")
    try:
        cur.execute("DELETE FROM mailing WHERE user_id=%s", (user_id,))
        con.commit()
        return True
    except: return None


# Creates html message for sending by "send_gmail" function
def compose_weather_mail_msg(data):
    if type(data) != list:
        logger.error(TypeError)
        raise TypeError
    try:
        length = len(data[0])
    except IndexError:
        logger.error(IndexError)
        raise
    date = day_of_week(data[0][0][0])
    date_info = str(date[0]) +" "+ str(date[1])
    snippet = create_html_table_rows(data)
    plane_txt = "Weather message"
    sunrise = str(data[0][0][1]['sunrise'])
    sunset = str(data[0][0][1]['sunset'])
    html_txt = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="width:75%;min-width:100%;hight:75%;min-hight:50%">
            <h2>Weather on {date_info}</h2>
            <div>
                <table style="padding:1.5%;color:white;
                    background-color:#212529;
                    border-radius:50px;">
                        <thead style="font-size:130%;">
                            <tr>
                                <th style="padding: 0 10px;">Time </th>
                                <th style="padding: 0 10px;"> Temperature°C </th>
                                <th style="padding: 0 10px;"> Humidity</th>
                                <th style="padding: 0 10px;">Precipitation</th>
                                <th style="padding: 0 10px;">Conditions </th>
                                <th></th>
                                <th style="padding: 0 10px 0 0;">Wind</th>
                            </tr>
                        </thead>
                        <tbody style="font-size:105%;">
                            {snippet[0]}
                            {snippet[1]}
                            {snippet[2]}
                            {snippet[3]}
                            {snippet[4]}
                            {snippet[5]}
                        </tbody>
                </table>
            </div>
            <br>
            <div>
                <h4> {data[0][0][1]['Location']} Id: {data[0][0][1]['ID']} 
                    Lat: {data[0][0][1]['Lat']} Lon: {data[0][0][1]['Lon']} 
                </h4>
                <h4> Sunrise: {sunrise} Sunset: {sunset} </h4>
            </div>
        </body>
        </html>
        """
    data = [plane_txt, html_txt]
    return data



# Compose message for password recovery
def compose_recovery_mail_msg(password):
    plane_txt = "MyWeatherApp"
    html_txt = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="width:50%;">
            <h1>Your recovery password</h1>
            <div style="padding:1.5%;color:white;background-color:#212529;text-align:center;">
                <h1 style="padding:50px 50px;">{password}</h1>
            </div>
            <div>
            <h3>If you did not make this request just ignore this message :)</h3>
            </div>
        </body>
        </html>
        """
    data = [plane_txt, html_txt]
    return data


# Queries DB for tracking info, parse response into [[location,email],
# [location,email],[location,email]...]
def query_mailing_table():
    mailing_list = []
    #regex removes <'" ()> from i
    filter = """['" ()]"""
    cur.execute("""SELECT (location_name, email) FROM
    location INNER JOIN mailing ON location.id=mailing.location_id
    INNER JOIN users ON mailing.user_id=users.id
    ORDER BY location ASC LIMIT 40""")
    try:
        con.commit()
        result = cur.fetchall()
    except: 
        logger.warning("An error occured during DB query")
        return RuntimeError("An error occured during DB query")
    if result != []:
        for i in result:
            i = re.sub(filter,'',i[0]).split(",")
            mailing_list.append(i)
    return mailing_list


#send_gmail(data, receiver)

