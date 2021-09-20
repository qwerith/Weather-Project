import requests, os, json, re, psycopg2, logging
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from cache_check import cache_check, input_type_check, check_by_id
from enum import Enum

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s")
handler = logging.FileHandler("logs.log")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)
    
#loading environment variables
try:
    load_dotenv(find_dotenv())
    con = psycopg2.connect(host = os.getenv("HOST"), database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("db_PASSWORD"), port = 5431)
    cur = con.cursor()
except psycopg2.OperationalError as e:
    logger.exception("Database credentials error")
    raise RuntimeError("Database credentials error") from e
    

API_KEY = os.getenv("OWM_KEY")
if not API_KEY:
    logger.error("API key error")
    raise RuntimeError("API key error")


class Parse_var(Enum):
    """Used to store parameters for different functions in one place"""
    API_RES_PARAMS = [["dt"], ["main","temp_min"], ["main","temp_max"],["main","humidity"],
        ["weather", 0,"description"], ["wind", "deg"], ["weather", 0, "icon"], ["wind", "speed"], ["pop"]]
    # "" Not used, added to list because it needs to be of certain length
    DB_RES_KEYS = ["min_temp", "max_temp", "humidity", "conditions", "picture_name", "wind", "wind_speed", "ID", "Location", "Lat", "Lon", "country", "sunrise", "sunset", "timezone", "pop", ""]


#converts input value to request string
def convert_location_to_query(location):
    #if input is coordinates, regex uses "pattern_replace" variable to strips all characters not noted in "[^. -1234567890]"
    pattern_replace = "[^. -1234567890]"
    if input_type_check(location) == "name":
        location = "q=" + location.capitalize()
    else:
        location = re.sub(pattern_replace,'',location)
        #divides coordinates string into two parts (latitude and longitude) and strips them from all characters noted in "[,'"!@#$%^&*()_+=|/?>,<`~]"
        location = (re.sub(r'''[,'"!@#$%^&*()_+=|/?>,<`~]''',"", location)).strip(" ").split(" ")
        lat = "lat=" + str(location[0])
        lon = "&lon=" + str(location[-1])
        location = lat + lon
    logger.info(location)
    return location


def get_input(location):
    #location = input("Enter location name: ")
    if type(location) != str:
        logger.warning(location)
        return "q=Lviv"
    if len(location) > 72 or len(location) <= 2:
        location = "q=Lviv"
    else:
        location = convert_location_to_query(location)
    return location


#checks whether input is location name or location coordinates
#returns coordinates or location name depending on input
def get_coords_or_name(location, request):
    #uses "pattern" to define whether input coincides with coordinates, example: """chars(49.3580)chars(23.5123)chars"""
    pattern = '.*(\d{2,}).*(\d{2,}).*'
    if re.search(pattern, location):
        location = request["city"]["name"]
    else:
        location = str(request["city"]["coord"])
        location = convert_location_to_query(location)
    return location
    

#makes request to Open Weather Map API if no cached data is found or it is outdated
def get_weather(location_input):
    try:
        location_input = get_input(location_input)
        print(location_input)
    except TypeError:
        logger.exception("Invalid input")
        raise
    check = cache_check(location_input)
    if check[0] == None:
        request = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?{location_input}&units=metric&appid={API_KEY}")
        print(request.status_code)
        #parsed = request.json()
        #print(json.dumps(parsed, indent=4, sort_keys=True))
        if request.status_code != 200:
            logger.warning(request.status_code)
            return RuntimeError("Request failed", request.status_code)
        if check[1] == "not_exists" and check_by_id(request.json()["city"]["id"]) == None:
            Cache.write_location(request.json(), location_input)
            Cache.write_weather(request.json(), check[1])
        else:
            Cache.write_weather(request.json(), "outdated")
        return Cache.read(request.json()["city"]["id"])
    else:
        return Cache.read(check[2])


class Cache():
    """Manages cache in postgres database, parses data for further usage in flask templates"""
    #inserts rows in "location" table if particular location is not found by "cache_check()" function
    def write_location(request_data, location_input):
        if input_type_check(location_input) == "coords":
            location_name = get_coords_or_name(location_input, request_data)
            coords = location_input
        else:
            coords = get_coords_or_name(location_input, request_data)
            location_name = location_input[2: ]
        db_location = [request_data["city"]["id"], location_name, coords.split("&")[0].split("=")[1], 
        coords.split("&")[1].split("=")[1], datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), request_data["city"]["country"], 
        request_data["city"]["sunrise"], request_data["city"]["sunset"], int((int(request_data["city"]["timezone"])/60)/60)]
        try:
            print(datetime.fromtimestamp(request_data["city"]["sunset"]))
            cur.execute("INSERT INTO location (id, location_name, lat, lon, request_date, country, sunrise, sunset, timezone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (db_location[0], db_location[1], db_location[2], db_location[3], db_location[4], db_location[5], db_location[6], db_location[7], db_location[8]))
            con.commit()
        except Exception:
            logger.exception("Cache Operation Error")
            raise

    #parses data in particular order for further insertion into "weather" table
    def parse_api_response(request_data):
        db_weather = []
        parameters = Parse_var.API_RES_PARAMS.value
        for i in request_data["list"]:
            temp_list = []
            for p in parameters:
                length = len(p)
                if length == 2:
                    temp_list.append(i[p[0]][p[1]])
                elif length == 3:
                    temp_list.append(i[p[0]][p[1]][p[2]]) 
                else:
                    if p == "pop":
                        i[p[0]] = int(i[p[0]])
                    temp_list.append(i[p[0]])
            db_weather.append(temp_list)
        #print(db_weather)
        return db_weather

    #inserts data into "weather table" if it is found to be absent or outdated by "cache_check()"" function
    #updates "reques_date" row in "location" table if weather data is outdated
    def write_weather(request_data, status):
        count = 0
        command = """INSERT INTO weather (date, min_temp, max_temp, humidity, conditions, wind, picture_name, location_id, wind_speed, pop) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        location_id = request_data["city"]["id"]
        db_weather = Cache.parse_api_response(request_data)
        #exists = cur.execute("SELECT EXISTS(SELECT 1 FROM weather WHERE location_id = %s LIMIT 1)",(location_id,))
        if status == "outdated":
            cur.execute("DELETE FROM weather WHERE location_id=%s", (location_id,))
            cur.execute("UPDATE location SET request_date = %s, sunrise = %s, sunset = %s WHERE id = %s", ((datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 
            request_data["city"]["sunrise"], request_data["city"]["sunset"], location_id)))
        for i in db_weather:
            cur.execute(command,(datetime.fromtimestamp(db_weather[count][0]), db_weather[count][1], db_weather[count][2],
            db_weather[count][3], db_weather[count][4], db_weather[count][5], db_weather[count][6], location_id, db_weather[count][7], db_weather[count][8]))
            count += 1  
        con.commit()

    #organises and returns list
    def parse_database_response(query_result):
        keys = Parse_var.DB_RES_KEYS.value
        weather_dict = {}
        final_data_list = []
        group_list = []
        for i in query_result:
            count = 0
            temp_dict = {}
            date = i[0].strftime('%Y-%m-%d %H:%M:%S')
            for char in i[1:]:
                if type(char) != int and type(char) != float:
                    #normalises string data by removing whitespaces
                    char = char.lstrip(" ").rstrip(" ")
                    if "."  in char and len(char) == 4:
                        char = round(float(char))
                temp_dict.update({keys[count]:char})
                count += 1 
            weather_dict.update({date:temp_dict})
        #sorts data in groups by comparing first part of timestamp(year, month, day)
        for i in weather_dict.keys():
            group_by_date = i
            break
        for i in weather_dict.items():
            iterable_date = i[0]
            if str(group_by_date).split(" ")[0] == str(iterable_date).split(" ")[0]:
                group_list.append(i)
            else:
                final_data_list.append(group_list)
                group_list = []
                group_list.append(i)
                group_by_date = i[0]
        try:
            final_data_list.append(group_list)
        except:
            logger.warning(f"Function ended with {group_list}")
        return final_data_list

    #queries "location" and "weather" tables for data
    def read(id):
        try:
            cur.execute("""SELECT date, min_temp, max_temp, humidity, conditions, picture_name, wind, wind_speed, location_id, location_name, lat, lon, country, sunrise, sunset, timezone, pop 
            FROM weather INNER JOIN location ON weather.location_id=location.id WHERE location_id=%s ORDER BY date ASC""", (id, ))
            query_result = cur.fetchall()
            con.commit()
        except:
            logger.warning("Query failed!")
            return RuntimeError("Query failed!")
        return Cache.parse_database_response(query_result)
        

result = get_weather("London")
print(result)
