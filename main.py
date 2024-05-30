from flask import Flask, redirect, url_for, request, render_template, session 
from flask_bcrypt import Bcrypt
import sqlite3
import paho.mqtt.client as mqtt
import json


from api_routes import temperature_api

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "ajkdhkajcocioauiodjkcjaxl" #session secret key

# Connect to SQLite database
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS temperatures
             (timestamp TEXT, temperature REAL)''')

# Save (commit) the changes
conn.commit()

app.register_blueprint(temperature_api, url_prefix='/api')

#mqtt client
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected successfully.")
        client.subscribe("NSI/david/test/teploty")
    else:
        print(f"MQTT Connect failed with result code {rc}")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    payload = json.loads(msg.payload)

    if 'temperature' in payload and 'timestamp' in payload:
        
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        # Check if the temperature reading has already been added
        c.execute("SELECT * FROM temperatures WHERE timestamp = ?", (payload["timestamp"],))
        if c.fetchone() is not None:
            print("Temperature reading already added")
            conn.close()
            return

        c.execute("INSERT INTO temperatures VALUES (?, ?)", (payload["timestamp"], payload["temperature"]))
        print("Inserted new temperature reading")
        conn.commit()
        conn.close()
    else:
        print("Invalid payload received")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.eclipseprojects.io", 1883, 60)



@app.route('/')
def home():
    if "username" in session:
        # Create a new connection and cursor for this request
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("SELECT * FROM temperatures")
        temps = c.fetchall()

        # Close the connection
        conn.close()

        # Pass the list of tuples to the template
        return render_template('index.html', values=temps)
    else:
        print("no user logged in")
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    errorx = request.args.get("errorx") #get message from url to display
    if request.method == 'POST':
        user = request.form["username"]
        password = request.form["password"]

        # Create a new connection and cursor for this request
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("SELECT password FROM users WHERE username=?", (user,))
        result = c.fetchone()
        if result is not None:
            if bcrypt.check_password_hash(result[0], password):
                session["username"] = user
                return redirect(url_for('home')) #correct login
            else:
                eror = "bad password,  please try again" 
                return redirect(url_for('login',errorx = eror))
        else:
            eror = "user does not exist, please register" 
            return redirect(url_for('login',errorx = eror))    
    else:
        return render_template('login.html', errorx = errorx)

@app.route('/register', methods=['GET', 'POST'])
def register():
    errorx = request.args.get("errorx") #get message from url to display
    if request.method == 'GET':
        return render_template("register.html", errorx = errorx)
    if request.method == 'POST':
        newuser = request.form["rusername"]
        password = request.form["rpassword"]
        if password == "":
            eror = "password cannot be blank"
            return redirect(url_for("register", errorx = eror ))

        # Create a new connection and cursor for this request
        conn = sqlite3.connect('data.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (newuser,))
        result = c.fetchone()
        if result is not None: #check if the username is not already registered
            eror = "this username is already registered, choose a different username, or login"
            return redirect(url_for("register", errorx = eror )) 
        else: 
            # Hash and salt the password
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Insert the new user into the database
            c.execute("INSERT INTO users VALUES (?, ?)", (newuser, pw_hash))
            conn.commit()

            # Close the connection
            conn.close()

            return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)