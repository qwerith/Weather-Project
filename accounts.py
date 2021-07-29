import psycopg2, os, re
from dotenv import load_dotenv, find_dotenv
from flask_bcrypt import Bcrypt
from flask import redirect, session
bcrypt = Bcrypt()

#loading environment variables
try:
    load_dotenv(find_dotenv())
    con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("db_PASSWORD"), port=5431)
    cur = con.cursor()
except: raise RuntimeError("Database credentials error")


class Accounts():
    def __init__(self, email, password):
        self.email = email.strip(" ")
        self.password = password.strip(" ")

    def register(self, username):
        if cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email=%s LIMIT 1)", (self.email, )):
            return "Account already exists"  
        else:
            try:
                cur.execute("INSERT INTO users (username, email, password) VALUES ( %s, %s, %s )", (username.strip(" "), self.email, bcrypt.generate_password_hash(self.password).decode("utf-8")))
                con.commit()
                return "Your account has been successfully created"
            except: return "Registration failed"    
    
    def user_verification(self):
        cur.execute("SELECT id, username, email, password FROM users WHERE email=%s LIMIT 1", (self.email, ))
        con.commit()
        user = cur.fetchall()
        if user and bcrypt.check_password_hash(user[0][3], self.password): 
            return(True, user)
        else:
            return(None)
    
    def delete(self):
        cur.execute("DELETE FROM users WHERE email=%s", (self.email, ))
        con.commit()

    def change_password(self, new_password):
        cur.execute("UPDATE users SET password=%s WHERE email=%s", (bcrypt.generate_password_hash(new_password).decode("utf-8"), self.email))
        con.commit()


def input_validation(user_input):
    #regex form for email validation
    response = []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.match(email_pattern, user_input[0])):
        response.append("Invalid email")
    if not len(user_input[1]) >= 5 and len(user_input[1]) <= 10:
        response.append("\nPassword must be 5 to 10 characters long")  
    if len(user_input) == 3:
        if not user_input[1] == user_input[2]:
            response.append("Passwords do not match")
    if len(user_input) == 4:
        if not user_input[2] == user_input[3]:
            response.append("Passwords do not match")
    return response


def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get("user_id") != None:
            func(*args, **kwargs)
            return func(*args, **kwargs)
        return redirect("/login")
    return wrapper

