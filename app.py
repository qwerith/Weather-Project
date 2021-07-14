from flask import Flask, redirect, request, session, render_template, url_for
from weather import get_weather
app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST" and request.form.get("location"):
        print(request.form.get("location"))
        DATA = get_weather(request.form.get("location"))
        print(DATA)
        try:
            return render_template("index.html", data=DATA)
        except: render_template("index.html")
         
    else:
        return render_template("index.html")


if __name__=="__main__":
    app.run()    