import smtplib, os
from smtplib import SMTPResponseException
from email.message import EmailMessage
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise RuntimeError("Credentials error")

path = os.getcwd()
body = "It works!!!"
receiver = "yuriisorokin98@gmail.com"


def send_gmail(body, receiver):
    msg = EmailMessage()
    msg["subject"]= "Python test"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    msg.set_content(body)

    with open(f"{path}\\templates\\mailing.html", "r") as f:
        data = f.read()
    msg.add_alternative(data, subtype="html")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)        
    except SMTPResponseException as e:
        print("Error code:", e.smtp_code,"\n", e.smtp_error)
        return (e.smtp_code, e.smtp_error)


#send_gmail(body, receiver)

