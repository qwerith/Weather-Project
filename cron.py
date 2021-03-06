from weather import get_weather
from mailing import query_mailing_table, compose_weather_mail_msg, send_gmail
from app import convert_timestamp

# Called by cron job every morning in 6:00 to send emails with weather data
def cron_mailing():
    mailing_list = query_mailing_table()
    if type(mailing_list) != RuntimeError:
        for i in mailing_list:
            DATA = get_weather(i[0])
            DATA = convert_timestamp(DATA, DATA[0][0][1]['timezone'])
            if not send_gmail(compose_weather_mail_msg(DATA), i[1]):
                #print("succsess")
                return True
    else:
        #print("An error in query_mailing()")
        return None

cron_mailing()