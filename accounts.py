import psycopg2 
import os
import re
import string
import random
import logging
from dotenv import load_dotenv, find_dotenv
from flask_bcrypt import Bcrypt
from flask import redirect, session
bcrypt = Bcrypt()

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
                           user = os.getenv("USER"), password = os.getenv("db_PASSWORD"),
                           port=5432)
    cur = con.cursor()
except RuntimeError("Database credentials error"):
    logger.exception("Database credentials error")
    raise


class Accounts():
    """Manages user accounts, queries data for session module, password changes and recovery"""
    def __init__(self, email, password):
        self.email = email.strip(" ")
        self.password = password.strip(" ")

    def register(self, username):
        try:
            con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"),
                                   user = os.getenv("USER"), password = os.getenv("db_PASSWORD"),
                                   port=5432)
            cur = con.cursor()
        except:
            logger.error(RuntimeError("Database credentials error"))
            raise RuntimeError("Database credentials error")
        cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s LIMIT 1)", (self.email, ))
        con.commit()
        result = cur.fetchall()
        if result[0][0] != False:
            return ["Account already exists"]  
        else:
            try:
                cur.execute("INSERT INTO users (username, email, password) VALUES ( %s, %s, %s )",
                            (username.strip(" "), self.email,
                            bcrypt.generate_password_hash(self.password).decode("utf-8")))
                con.commit()
                con.close()
                return ["Your account has been successfully created"]
            except:
                con.close()
                return ["Registration failed"]
    
    def user_verification(self):
        cur.execute("SELECT id, username, email, password FROM users WHERE email=%s LIMIT 1",
                    (self.email, ))
        con.commit()
        user = cur.fetchall()
        if user and bcrypt.check_password_hash(user[0][3], self.password): 
            return(True, user)
        else:
            return None
    
    def delete(self):
        cur.execute("DELETE FROM users WHERE email=%s", (self.email, ))
        con.commit()

    def change_password(self, new_password):
        cur.execute("UPDATE users SET password=%s WHERE email=%s",
                    (bcrypt.generate_password_hash(new_password).decode("utf-8"), self.email))
        con.commit()
    
    def restore_password(self, temp_password_hash, temp_password):
        if bcrypt.check_password_hash(temp_password_hash, temp_password):
            cur.execute("UPDATE users SET password=%s WHERE email=%s",
                        (bcrypt.generate_password_hash(self.password).decode("utf-8"), self.email))
            con.commit()
            return True
        return None
        
# Generates random password for recovery process                
def generate_temporary_password(email):
    cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email = %s LIMIT 1)", (email, ))
    con.commit()
    result = cur.fetchall()
    if result[0][0] != False:
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        size = random.randint(5, 10)
        temp_password = ''.join(random.choice(chars) for x in range(size))
        password_hash = bcrypt.generate_password_hash(temp_password).decode("utf-8")
        return password_hash, temp_password
    return None, ""


def input_validation(user_input):
    #regex form for email validation
    try:
        len(user_input) > 1
        for i in user_input:
            if type(i) != str:
                return ["Invalid data type"]
    except IndexError:
        logger.error(IndexError)
        raise
    response = []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    punctuation = """[!#$%&'()*+, -./:;"<=>?@[\]^_`{|}~:]"""
    if not (re.match(email_pattern, user_input[0])):
        response.append("Invalid email")
    if (not len(user_input[1]) >= 5 and len(user_input[1]) <= 10 or
        re.findall(punctuation, user_input[1]) != []):
            response.append("Password must be 5 to 10 characters long")  
    if len(user_input) == 3:
        if not user_input[1] == user_input[2] or re.findall(punctuation, user_input[2]) != []:
            response.append("Passwords do not match")
    if len(user_input) == 4:
        if not user_input[2] == user_input[3] or re.findall(punctuation, user_input[3]) != []:
            response.append("Passwords do not match")
    return response


def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get("user_id") != None:
            func(*args, **kwargs)
            return func(*args, **kwargs)
        return redirect("/login")
    return wrapper

