import smtplib, os, psycopg2, re
from smtplib import SMTPResponseException
#from email.message import EmailMessage
from dotenv import load_dotenv, find_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


#loading environment variables
try:
    load_dotenv(find_dotenv())
    con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("db_PASSWORD"), port=5431)
    cur = con.cursor()
except: raise RuntimeError("Database credentials error")


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise RuntimeError("Credentials error")


#path = os.getcwd()
#data = [[('2021-08-06 18:00:00', {'min_temp': '18.78', 'max_temp': '20.33', 'humidity': '69', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '242', 'wind_speed': 8, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-06 21:00:00', {'min_temp': '14.32', 'max_temp': '16.58', 'humidity': '76', 'conditions': 'brokenclouds', 'picture_name': '04n', 'wind': '253', 'wind_speed': 7, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'})], [('2021-08-07 00:00:00', {'min_temp': '13.56', 'max_temp': '13.56', 'humidity': '78', 'conditions': 'brokenclouds', 'picture_name': '04n', 'wind': '245', 'wind_speed': 6, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-07 03:00:00', {'min_temp': '13.71', 'max_temp': '13.71', 'humidity': '77', 'conditions': 'brokenclouds', 'picture_name': '04n', 'wind': '243', 'wind_speed': 6, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-07 06:00:00', {'min_temp': '13.73', 'max_temp': '13.73', 'humidity': '70', 'conditions': 'overcastclouds', 'picture_name': '04d', 'wind': '242', 'wind_speed': 7, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-07 09:00:00', {'min_temp': '14.04', 'max_temp': '14.04', 'humidity': '64', 'conditions': 'overcastclouds', 'picture_name': '04d', 'wind': '252', 'wind_speed': '6.7', 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-07 12:00:00', {'min_temp': '20.32', 'max_temp': '20.32', 'humidity': '50', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '273', 'wind_speed': 8, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-07 15:00:00', {'min_temp': '23.09', 'max_temp': '23.09', 'humidity': '40', 'conditions': 'scatteredclouds', 'picture_name': '03d', 'wind': '276', 'wind_speed': 7, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-07 18:00:00', {'min_temp': '23.92', 'max_temp': '23.92', 'humidity': '48', 'conditions': 'clearsky', 'picture_name': '01d', 'wind': '282', 'wind_speed': 4, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-07 21:00:00', {'min_temp': 20, 'max_temp': 20, 'humidity': '62', 'conditions': 'scatteredclouds', 'picture_name': '03n', 'wind': '235', 'wind_speed': '1.9', 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'})], [('2021-08-08 00:00:00', {'min_temp': '16.51', 'max_temp': '16.51', 'humidity': '81', 'conditions': 'scatteredclouds', 'picture_name': '03n', 'wind': '233', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-08 03:00:00', {'min_temp': '15.39', 'max_temp': '15.39', 'humidity': '86', 'conditions': 'scatteredclouds', 'picture_name': '03n', 'wind': '194', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-08 06:00:00', {'min_temp': '15.15', 'max_temp': '15.15', 'humidity': '84', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '150', 'wind_speed': 4, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-08 09:00:00', {'min_temp': '20.23', 'max_temp': '20.23', 'humidity': '66', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '162', 'wind_speed': 5, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-08 12:00:00', {'min_temp': '26.85', 'max_temp': '26.85', 'humidity': '47', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '169', 'wind_speed': 6, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-08 15:00:00', {'min_temp': 27, 'max_temp': 27, 'humidity': '50', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '181', 'wind_speed': 5, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-08 18:00:00', {'min_temp': '29.19', 'max_temp': '29.19', 'humidity': '46', 'conditions': 'scatteredclouds', 'picture_name': '03d', 'wind': '222', 'wind_speed': 3, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-08 21:00:00', {'min_temp': '21.15', 'max_temp': '21.15', 'humidity': '76', 'conditions': 'scatteredclouds', 'picture_name': '03n', 'wind': '342', 'wind_speed': 4, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'})], [('2021-08-09 00:00:00', {'min_temp': 18, 'max_temp': 18, 'humidity': '87', 'conditions': 'lightrain', 'picture_name': '10n', 'wind': '333', 'wind_speed': 3, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-09 03:00:00', {'min_temp': '16.08', 'max_temp': '16.08', 'humidity': '92', 'conditions': 'lightrain', 'picture_name': '10n', 'wind': '354', 'wind_speed': 3, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-09 06:00:00', {'min_temp': 16, 'max_temp': 16, 'humidity': '94', 'conditions': 'lightrain', 'picture_name': '10d', 'wind': '276', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-09 09:00:00', {'min_temp': '18.74', 'max_temp': '18.74', 'humidity': '82', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '6', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-09 12:00:00', {'min_temp': '23.47', 'max_temp': '23.47', 'humidity': '56', 'conditions': 'overcastclouds', 'picture_name': '04d', 'wind': '13', 'wind_speed': 3, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-09 15:00:00', {'min_temp': '26.09', 'max_temp': '26.09', 'humidity': '45', 'conditions': 'brokenclouds', 'picture_name': '04d', 'wind': '358', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-09 18:00:00', {'min_temp': '24.03', 'max_temp': '24.03', 'humidity': '56', 'conditions': 'overcastclouds', 'picture_name': '04d', 'wind': '4', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-09 21:00:00', {'min_temp': '21.54', 'max_temp': '21.54', 'humidity': '59', 'conditions': 'overcastclouds', 'picture_name': '04n', 'wind': '59', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'})], [('2021-08-10 00:00:00', {'min_temp': '18.21', 'max_temp': '18.21', 'humidity': '69', 'conditions': 'scatteredclouds', 'picture_name': '03n', 'wind': '60', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-10 03:00:00', {'min_temp': '16.63', 'max_temp': '16.63', 'humidity': '78', 'conditions': 'fewclouds', 'picture_name': '02n', 'wind': '127', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-10 06:00:00', {'min_temp': '15.64', 'max_temp': '15.64', 'humidity': '83', 'conditions': 'scatteredclouds', 'picture_name': '03d', 'wind': '120', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-10 09:00:00', {'min_temp': '20.48', 'max_temp': '20.48', 'humidity': '65', 'conditions': 'scatteredclouds', 'picture_name': '03d', 'wind': '126', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-10 12:00:00', {'min_temp': 24, 'max_temp': 24, 'humidity': '51', 'conditions': 'overcastclouds', 'picture_name': '04d', 
#'wind': '123', 'wind_speed': 3, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-10 15:00:00', {'min_temp': '26.13', 'max_temp': '26.13', 'humidity': '44', 'conditions': 'overcastclouds', 'picture_name': '04d', 'wind': '121', 'wind_speed': 3, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-10 18:00:00', {'min_temp': '25.96', 'max_temp': '25.96', 'humidity': '45', 'conditions': 'overcastclouds', 'picture_name': '04d', 'wind': '104', 'wind_speed': '2.5', 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'}), ('2021-08-10 21:00:00', {'min_temp': '20.24', 'max_temp': '20.24', 'humidity': '62', 'conditions': 'overcastclouds', 'picture_name': '04n', 'wind': '115', 'wind_speed': 2, 'ID': 702569, 'Location': 'Lutsk', 'Lat': '50.7593', 'Lon': '25.3424'})]]
#receiver = "yuriisorokin98@gmail.com"


# Inserts weather information into string for further conversion to HTML
def create_html_table_rows(data):
    length = len(data[0])
    count = -1
    html_snippets = []
    for i in range(length):
        count += 1
        if count < length:
            table_row = f"""<tr>
                                <td style="padding: 0 10px;">{data[0][count][0].split(" ")[1][:5]}</td>
                                <td style="padding: 0 5%;min-width:160px;"> {data[0][count][1]["min_temp"]} / {data[0][count][1]["max_temp"]}°</td>
                                <td style="padding: 0 5%;">{data[0][count][1]["humidity"]}%</td>
                                <td style="padding: 0 5%;">{data[0][count][1]["pop"]}%</td>
                                <td style="padding: 0 10px;">{data[0][count][1]["conditions"]}</td>
                                <td style="padding: 0 10px;"><img src="http://openweathermap.org/img/wn/{data[0][count][1]["picture_name"]}@2x.png"alt=""style="width:50px;height:50px;"></td>
                                <td style="padding: 0 10px;">{data[0][count][1]["wind_speed"]} m/s</td>
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
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    day_number = str(date).split(" ")[0].split("-")[2]
    if day_number[0] == '0':
        day_number = day_number[1]
    day = (str(date.strftime('%A')), day_number, date.strftime("%B"))
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
        print("Error code:", e.smtp_code,"\n", e.smtp_error)
        return (e.smtp_code, e.smtp_error)


# Inserts into DB mailing table information for further usage in send_gmail function
def set_up_track(user_id, location_id):
    cur.execute("SELECT EXISTS(SELECT 1 FROM mailing WHERE user_id = %s LIMIT 1)", (user_id, ))
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
    try:
        cur.execute("DELETE FROM mailing WHERE user_id=%s", (user_id,))
        con.commit()
        return True
    except: return None


# Creates html message for sending by "send_gmail" function
def compose_weather_mail_msg(data):
    date = day_of_week(data[0][0][0])
    date_info = str(date[0]) +" "+ str(date[1])
    snippet = create_html_table_rows(data)
    plane_txt = "Weather message"
    html_txt = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="width:auto;min-width:600px;">
            <h1>Weather on {date_info}</h1>
            <div>
                <table style="padding:1.5%;color:white;background-color:#212529;border-radius:50px;">
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
                <h4> {data[0][0][1]['Location']} Id: {data[0][0][1]['ID']} Lat: {data[0][0][1]['Lat']} Lon: {data[0][0][1]['Lon']}</h4>
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
        <body style="width:30%;">
            <h1>Your recovery password</h1>
            <div style="padding:1.5%;color:white;background-color:#212529;text-align:center;">
                <h1 style="padding:50px 50px;">{password}</h1>
            </div>
            <div>
            <h3>If you did not make this request just ignore this message</h3>
            </div>
        </body>
        </html>
        """
    data = [plane_txt, html_txt]
    return data


# Queries DB for tracking info, parse response into [[location,email],[location,email],[location,email]...]
def query_mailing_table():
    mailing_list = []
    #regex removes <'" ()> from i
    filter = """['" ()]"""
    cur.execute("SELECT (location_name, email) FROM location INNER JOIN mailing ON location.id=mailing.location_id INNER JOIN users ON mailing.user_id=users.id ORDER BY location ASC LIMIT 40")
    try:
        con.commit()
        result = cur.fetchall()
    except: return RuntimeError("An error occured during DB query")
    if result[0][0] != "":
        for i in result:
            i = re.sub(filter,'',i[0]).split(",")
            mailing_list.append(i)
    return mailing_list


#send_gmail(data, receiver)

