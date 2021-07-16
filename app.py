from flask import Flask, redirect, request, session, render_template, url_for
from weather import get_weather
app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST" and request.form.get("location"):
        print(request.form.get("location"))
        location = request.form.get("location")
        DATA = get_weather(location)
        data_list = []
        group_list = []
        STATUS = f"{location} not found"
        for i in DATA.keys():
            group_date = i
            break
        for i in DATA.items():
            i_date = i[0]
            if str(group_date).split(" ")[0] == str(i_date).split(" ")[0]:
                group_list.append(i)
            else:
                data_list.append(group_list)
                group_list = []
                group_date = str(i[0])   
        print(data_list)
        return render_template('index.html', status=STATUS) if type(DATA) == RuntimeError else render_template("index.html", data=data_list) 
    else:
        return render_template("index.html")


if __name__=="__main__":
    app.run()    