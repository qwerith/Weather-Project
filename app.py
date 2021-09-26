import os, re, requests, logging
from flask import Flask, redirect, request, session, render_template, flash, url_for
from weather import get_weather
from accounts import Accounts, input_validation, login_required, generate_temporary_password
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv, find_dotenv
from mailing import send_gmail, day_of_week, set_up_track, compose_weather_mail_msg, stop_tracking, compose_recovery_mail_msg
from flask import Response
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s")
handler = logging.FileHandler("logs.log")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# Map-tiles url
url_root = "http://tile.openweathermap.org/map" 
temp_storage = []
load_dotenv(find_dotenv())
secret_key = os.getenv("FLASK_SECRET_KEY")

if not secret_key:
    logger.error("Flask secret key error")
    raise RuntimeError("Flask secret key error")

app_key = os.getenv("OWM_MAP_KEY")
if not app_key:
    logger.error("OWM map key error")
    raise RuntimeError("OWM map key error")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = secret_key
bcrypt = Bcrypt(app)


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST" and request.form.get("location"):
        location = request.form.get("location").capitalize()
        print(location)
        DATA = get_weather(location)
        STATUS = f"{location} not found"
        if type(DATA) == RuntimeError:
            return render_template('index.html', status=STATUS)
        else:
            DATA = convert_timestamp(DATA, DATA[0][0][1]['timezone'])
            if session.get("user_id") != None:
                location_list = Quick_search.find_cache()
                search_result = Quick_search.create_quick_search(location, location_list)
                Quick_search.write_quick_search_buffer(search_result)
                search_result = Quick_search.query_quick_search()
            else:
                search_result = None
        return render_template("index.html", data=DATA, day_of_week = day_of_week, compass=compass, search_result=search_result)
    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = [request.form.get("username"), request.form.get("email"), request.form.get("password"), request.form.get("confirm_password")]
    if request.method == "POST" and all(char != "" for char in form) and len(form[0]) < 20:
        input_valid = input_validation(form[1:4])
        form.clear()
        if not input_valid == []:     
            flash(input_valid, "info")
            return render_template("register.html")
        else:
            user = Accounts(request.form.get("email"), request.form.get("password"))
            user_status = user.register(request.form.get("username"))
            flash(user_status, "info")
            user_info = request.form.get("email")
            logger.info(f"User {user_info} registration status, {user_status}")
            return redirect(url_for("login"))
    else:
        form.clear()
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form.get("email") != "" and request.form.get("password") != "":
        session.pop("user_id", None)
        input_valid = input_validation([request.form.get("email"), request.form.get("password")])
        if input_valid != []:
            flash(input_valid, "info")
            return render_template("login.html") 
        else:
            user = Accounts(request.form.get("email"), request.form.get("password"))
            user = user.user_verification()
            if user:
                logger.info(f"User {user[1][0][0]} has loged in successfully!")
                session["user_id"] = user[1][0][0]
                session["username"] = user[1][0][1]
                session["email"] = user[1][0][2]    
                print(session["user_id"])
                return redirect("/")
            else:
                flash(["Wrong email or password"], "info")
                return render_template("login.html")        
    else:
        return render_template("login.html")


@login_required
@app.route("/logout", methods=["GET"])
def logout():
    Quick_search.clear_buffer()
    user_id = session["user_id"]
    logger.info(f"User {user_id} has loged out")
    session.pop("user_id", None)
    return redirect("/")


@login_required
@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST" and request.form.get("password") != "":
        input_valid = input_validation([session["email"], request.form.get("password")])
        print(session["email"])
        if input_valid != []:
            print("test")
            flash(input_valid, "info")
            return render_template("delete.html")
        user = Accounts(session["email"], request.form.get("password"))
        if user.user_verification():
            user_info = session["email"]
            user.delete()
            Quick_search.clear_buffer()
            logger.info(f"User {user_info} has been deleted successfully!")
            session.pop("user_id", None)
            return redirect("/")
        return redirect("/delete")
    return render_template("delete.html")


@login_required
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST" and request.form.get("password") != "":
        input_valid = input_validation([session["email"], request.form.get("password"),
        request.form.get("password_new"), request.form.get("password_new_confirm")])
        if input_valid != []:
            flash(input_valid, "info")
            return redirect("/change_password")
        user = Accounts(session["email"], request.form.get("password"))
        if user.user_verification():
            user.change_password(request.form.get("password_new"))
            user_info = session["user_id"]
            logger.info(f"User {user_info} password has been changed!")
            return redirect("/")
        return redirect("/change_password")
    return render_template("change_password.html")


@app.route("/restore_password", methods=["GET", "POST"])
def restore_password():
    if request.method == "POST":
        input_valid = input_validation([session.get("recovery_email"), request.form.get("temp_passsword"), request.form.get("password_new"), request.form.get("password_new_confirm")])
        if input_valid != []:
            flash(input_valid, "info")
            return render_template("restore_password.html")
        temp_password_hash = session.get("temporary_password_hash")
        if temp_password_hash:
            user = Accounts(session.get("recovery_email"), request.form.get("password_new"))
            if not user.restore_password(temp_password_hash, request.form.get("temp_passsword")):
                return redirect("/restore_password")
            user_info = session["recovery_email"]
            logger.info(f"User {user_info} successfully recovered account!")
            session.pop("temporary_password_hash", None)
            return redirect("/login")
        return redirect("/send_temporary_password")
    return render_template("restore_password.html")


@app.route("/send_temporary_password", methods=["GET", "POST"])
def send_temporary_password():
    if request.method == "POST":
        input_valid = input_validation([request.form.get("email"), "Unknown"])
        if input_valid != []:
            flash(input_valid, "info")
            return render_template("send_temporary_password.html")
        session["recovery_email"] = request.form.get("email") 
        temp_password = generate_temporary_password(request.form.get("email"))
        session["temporary_password_hash"] = temp_password[0]
        if type(temp_password[0]) == str and len(temp_password) > 0:
            message = compose_recovery_mail_msg(temp_password[1])
        else:
            logger.warning(TypeError("Excpected password value of type string"))
            flash("Account does not exist", "info")
            return render_template("send_temporary_password.html")
        send_gmail(message, request.form.get("email"))
        message = None
        temp_password = None
        user_info = request.form.get("email")
        logger.info(f"Temporary password was sent to {user_info}")
        return redirect("/restore_password")
    return render_template("send_temporary_password.html")


@login_required
@app.route("/track", methods=["POST"])
def track():
    #regex removes <'" ()> from request.form.get("location") value
    filter = """['" ()]"""
    if request.method == "POST" and check_session(request.form.get("location")) == None:
        search_result = Quick_search.query_quick_search()
        session.pop("track", None)
        session.pop("track_name", None)
        location_name = re.sub(filter,"",request.form.get("location")).split(",")[0]
        location_id = re.sub(filter,"",request.form.get("location")).split(",")[1]
        print(location_name, location_id)
        session["track"] = location_id
        session["track_name"] = location_name
        DATA = get_weather(location_name)
        if set_up_track(session["user_id"], location_id) and type(DATA) != RuntimeError:
            DATA = convert_timestamp(DATA, DATA[0][0][1]['timezone'])
            send_gmail(compose_weather_mail_msg(DATA), session["email"])
            user_info = session["user_id"]
            logger.info(f"User {user_info} started tracking!")
            return render_template("index.html", data=DATA, day_of_week = day_of_week, compass=compass, search_result=search_result) 
        return redirect("/")
    return redirect("/")


@login_required
@app.route("/stop_track", methods=["POST"])
def stop_track():
    if request.method == "POST":
        search_result = Quick_search.query_quick_search()
        session.pop("track", None)
        session.pop("track_name", None)
        if stop_tracking(session["user_id"]):
            location_name = request.form.get("location")
            DATA = get_weather(location_name)
            if type(DATA) == RuntimeError:
                return redirect("/")
            else: 
                DATA = convert_timestamp(DATA, DATA[0][0][1]['timezone'])
                print(search_result)
                user_info = session["user_id"]
                logger.info(f"User {user_info} stopped tracking!")
                return render_template("index.html", data=DATA, day_of_week = day_of_week, compass=compass, search_result=search_result) 
    return redirect("/")


@app.route("/map/<tile_name>/<z>/<x>/<y>")
def get_tile(tile_name,z,x,y):
    print(tile_name,z,x,y)
    tile_name = tile_name.split("=")[1]
    z = int(float(z.split("=")[1]))
    x = int(float(x.split("=")[1]))
    y = int(float(y.split("=")[1]))
    req = requests.get(f"{url_root}/{tile_name}/{z}/{x}/{y}.png?appid={app_key}")
    if req.status_code != 200:
        logger.warning(f"Map request error {req.status_code}")
        print(f"Map request error {req.status_code}")
    return Response(req.content, content_type = req.headers['content-type'])


class Quick_search():
    """Manages quick search info, saves into buffer, queries info on call, deletes"""

    def find_cache():
        for i in temp_storage:
            if i.get(session.get("user_id")):
                v = list(i.values())
                search_list = v[0]
                print(search_list)
                return search_list
        return [{"search_0" : False}, {"search_1" : False}, {"search_2" : False}]

    def write_quick_search_buffer(search_result):
        for i in temp_storage:
            if i.get(session.get("user_id")):
                i.update({session.get("user_id") : search_result})
                return temp_storage
        temp_storage.append({session.get("user_id") : search_result})
        return temp_storage
    
    def clear_buffer():
        for i in temp_storage:
            if i.get(session.get("user_id")):
                i.pop(session.get("user_id"))
                return True
        return False

    def create_quick_search(location, search_list):
        if location not in [search_list[0]["search_0"], search_list[1]["search_1"], search_list[2]["search_2"]]:
            if search_list[0]["search_0"] == None:
                search_list[0].update({"search_0" : location})
            elif search_list[0]["search_0"] != None and search_list[1]["search_1"] == None:
                search_list[1].update({"search_1" : search_list[0]["search_0"]})
                search_list[0] = ({"search_0" : location})
            else:
                search_list[2].update({"search_2":search_list[1]["search_1"]})
                search_list[1].update({"search_1":search_list[0]["search_0"]})
                search_list[0] = ({"search_0" : location})
        return search_list
    
    def query_quick_search():
        search_list = [{"search_0" : False}, {"search_1" : False}, {"search_2" : False}]
        if session.get("user_id") != None:
            for i in temp_storage:
                if i.get(session["user_id"]):
                    return i
            return {"Unknown": search_list}
        return {"Unknown": search_list}


# Checks if track request already exists
def check_session(location):
    filter = """['" ()]"""
    try:
        if session.get("track") == re.sub(filter,"",location).split(",")[1]:
            return True
        return None
    except: return None


def convert_timestamp(data, utc_difference):
    logger.info(f"Function called with {data[0][0][1]['sunrise']}, {data[0][0][1]['sunset']}, {utc_difference}")
    sunrise = datetime.fromtimestamp(int(data[0][0][1]['sunrise']))
    sunset = datetime.fromtimestamp(int(data[0][0][1]['sunset']))
    difference_in_hours = timedelta(hours = int(utc_difference))
    sunrise = (sunrise + difference_in_hours).strftime('%H:%M')
    sunset = (sunset + difference_in_hours).strftime('%H:%M')
    data[0][0][1]['sunrise'] = sunrise
    data[0][0][1]['sunset'] = sunset
    if int(utc_difference) > 0:
        data[0][0][1]['timezone'] = "+" + data[0][0][1]['timezone']
    return data
    

def compass(direction):
    try:
        int(direction)
    except:
        logger.warning("ValueError occured!")
        return str(135)
    direction = int(direction)
    if direction > 135:
        direction = (direction - 135)
    elif direction < 135:
        direction = (135 - direction)
    return str(direction)
    
        
if __name__=="__main__":
    app.run()    