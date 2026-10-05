from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import serial
import threading
import time
import joblib
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = "secret123"

model = joblib.load("aqi_model.pkl")

arduino = serial.Serial('COM3',9600)
time.sleep(2)

# Demo Login Credentials
USER = {
    "username": "admin",
    "password": "1234"
}

sensor_data = {
    "mq2":0,
    "mq7":0,
    "mq135":0,
    "temp":0,
    "hum":0,
    "pres":0,
    "aqi":0
}


# ---------------- SERIAL DATA ----------------
def read_serial():

    global sensor_data

    while True:

        try:

            line = arduino.readline().decode().strip()
            print("Serial:",line)

            if "MQ2:" in line:
                parts = line.split()
                mq2 = float(parts[1])
                mq7 = float(parts[3])
                mq135 = float(parts[5])
                temp = float(parts[7])
                hum = float(parts[9])

                pres = random.uniform(1004,1006)

                features = pd.DataFrame(
                [[mq2,mq7,mq135,temp,hum,pres]],
                columns=["MQ2","MQ7","MQ135","Temperature","Humidity","Pressure"]
                )

                prediction = model.predict(features)[0]

                sensor_data["mq2"] = mq2
                sensor_data["mq7"] = mq7
                sensor_data["mq135"] = mq135
                sensor_data["temp"] = temp
                sensor_data["hum"] = hum
                sensor_data["pres"] = round(pres,2)
                sensor_data["aqi"] = round(prediction,2)

        except Exception as e:
            print("Error:",e)


thread = threading.Thread(target=read_serial)
thread.daemon = True
thread.start()



# ---------------- LOGIN PAGE ----------------
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == USER["username"] and password == USER["password"]:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid Login")

    return render_template("login.html")



# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("index.html")



# ---------------- SENSOR DATA API ----------------
@app.route("/data")
def data():
    return jsonify(sensor_data)



# ---------------- ABOUT PAGE ----------------
@app.route("/about")
def about():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("about.html")



# ---------------- CONTACT PAGE ----------------
@app.route("/contact")
def contact():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("contact.html")



# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.pop("user",None)
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(debug=False)