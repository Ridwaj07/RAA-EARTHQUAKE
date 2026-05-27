from flask import Flask, render_template, request, redirect, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import os
from flask_mail import Mail, Message

# ================= APP =================
app = Flask(__name__)
app.secret_key = "raa_super_secret_key"

# ================= EMAIL =================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'raa.earthquake.2.0@gmail.com'
app.config['MAIL_PASSWORD'] = 'soeg zmof dhse utjs'

mail = Mail(app)

# ================= DATABASE =================
database_url = os.environ.get("DATABASE_URL")
if database_url:
    database_url = database_url.replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= ADMIN =================
ADMIN_EMAILS = [
    "bharadwajrishav8434@gmail.com",
    "nitu9sharma9@gmail.com"
]

# ================= MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))

with app.app_context():
    db.create_all()

# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")

# ================= AUTH =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "Email already exists"

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["user_email"] = user.email
        return redirect("/")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.id
            session["user_email"] = user.email
            return redirect("/")

        return "Invalid login"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect("/login")

    user = db.session.get(User, session["user_id"])
    return render_template("account.html", user=user)

# ================= INDIA =================
@app.route("/india")
def india():
    earthquakes = []
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=30)

        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.date()}&endtime={end.date()}&minlatitude=6&maxlatitude=37&minlongitude=68&maxlongitude=97"

        response = requests.get(url, timeout=5)
        data = response.json()

        for item in data.get("features", []):
            earthquakes.append({
                "place": item["properties"].get("place"),
                "mag": item["properties"].get("mag"),
                "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
            })
    except Exception as e:
        print("INDIA ERROR:", e)

    return render_template("india.html", earthquakes=earthquakes)

# ================= WORLD =================
@app.route("/world", methods=["GET", "POST"])
def world():
    earthquakes = []
    countries = ["All Countries","India","United States","Japan","Turkey","Indonesia","Chile","Mexico","Philippines","Nepal","Iran"]

    selected_country = request.form.get("country") if request.method == "POST" else "All Countries"

    try:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=50&orderby=time"
        response = requests.get(url, timeout=5)
        data = response.json()

        for item in data.get("features", []):
            place = item["properties"].get("place", "")

            if selected_country != "All Countries":
                if selected_country.lower() not in place.lower():
                    continue

            earthquakes.append({
                "place": place,
                "mag": item["properties"].get("mag"),
                "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
            })
    except Exception as e:
        print("WORLD ERROR:", e)

    return render_template("world.html", earthquakes=earthquakes, countries=countries, selected_country=selected_country)

# ================= ASIA =================
@app.route("/asia", methods=["GET", "POST"])
def asia():
    earthquakes = []
    countries = {
        "India": {"minlat": 6, "maxlat": 37, "minlon": 68, "maxlon": 97},
        "Japan": {"minlat": 24, "maxlat": 46, "minlon": 123, "maxlon": 146}
    }

    selected_country = request.form.get("country") if request.method == "POST" else "India"
    region = countries[selected_country]

    try:
        end = datetime.utcnow()
        start = end - timedelta(days=30)

        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.date()}&endtime={end.date()}&minlatitude={region['minlat']}&maxlatitude={region['maxlat']}&minlongitude={region['minlon']}&maxlongitude={region['maxlon']}"

        response = requests.get(url, timeout=5)
        data = response.json()

        for item in data.get("features", []):
            place = item["properties"].get("place", "")

            if selected_country.lower() not in place.lower():
                continue

            earthquakes.append({
                "place": place,
                "mag": item["properties"].get("mag"),
                "time": datetime.fromtimestamp(item["properties"]["time"]/1000)
            })

    except Exception as e:
        print("ASIA ERROR:", e)

    return render_template("asia.html", earthquakes=earthquakes, countries=countries.keys(), selected_country=selected_country)

# ================= STATIC PAGES =================
@app.route("/about")
def about(): return render_template("about.html")

@app.route("/terms")
def terms(): return render_template("terms.html")

@app.route("/privacy")
def privacy(): return render_template("privacy.html")

@app.route("/disclaimer")
def disclaimer(): return render_template("disclaimer.html")

# ================= CONTACT =================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            name = request.form.get("name")
            email = request.form.get("email")
            message = request.form.get("message")

            msg = Message(
                subject="New Contact Message",
                sender=app.config['MAIL_USERNAME'],
                recipients=["raa.earthquake.2.0@gmail.com"]
            )

            msg.body = f"Name: {name}\nEmail: {email}\n\n{message}"
            mail.send(msg)

            return render_template("contact.html", success=True)

        except Exception as e:
            print("MAIL ERROR:", e)
            return render_template("contact.html", error=True)

    return render_template("contact.html")

# ================= EXTRA =================
@app.route("/guide")
def guide(): return render_template("guide.html")

@app.route("/map")
def map(): return render_template("map.html")

@app.route("/ads.txt")
def ads(): return send_from_directory('.', 'ads.txt')

@app.route("/ping")
def ping(): return "ok"

@app.route("/robots.txt")
def robots():
    return send_from_directory('.', 'robots.txt')

# ================= EXISTING ARTICLES =================
@app.route("/earthquake")
def earthquake(): return render_template("earthquake.html")

@app.route("/what-is-earthquake")
def what_is_earthquake(): return render_template("what-is-earthquake.html")

@app.route("/richter-scale")
def richter_scale(): return render_template("richter-scale.html")

@app.route("/biggest-earthquakes")
def biggest_earthquakes(): return render_template("biggest-earthquakes.html")

@app.route("/earthquake-safety")
def earthquake_safety(): return render_template("earthquake-safety.html")

@app.route("/earthquakes-india")
def earthquakes_india(): return render_template("earthquakes-india.html")

# ================= NEW ARTICLES =================
@app.route("/earthquake-preparedness")
def earthquake_preparedness(): return render_template("earthquake-preparedness.html")

@app.route("/magnitude-vs-intensity")
def magnitude_vs_intensity(): return render_template("magnitude-vs-intensity.html")

@app.route("/japan-earthquakes")
def japan_earthquakes(): return render_template("japan-earthquakes.html")

@app.route("/early-warning-systems")
def early_warning_systems(): return render_template("early-warning-systems.html")

@app.route("/earthquake-prediction")
def earthquake_prediction(): return render_template("earthquake-prediction.html")

@app.route("/tsunamis-earthquakes")
def tsunamis_earthquakes(): return render_template("tsunamis-earthquakes.html")

@app.route("/earthquake-safety-schools")
def earthquake_safety_schools(): return render_template("earthquake-safety-schools.html")

@app.route("/earthquake-safety-home")
def earthquake_safety_home(): return render_template("earthquake-safety-home.html")

@app.route("/earthquake-facts-myths")
def earthquake_facts_myths(): return render_template("earthquake-facts-myths.html")

@app.route("/tectonic-plates")
def tectonic_plates(): return render_template("tectonic-plates.html")

@app.route("/earthquake-resistant-buildings")
def earthquake_resistant_buildings(): return render_template("earthquake-resistant-buildings.html")

@app.route("/psychology-of-disasters")
def psychology_of_disasters(): return render_template("psychology-of-disasters.html")

@app.route("/economic-impact-earthquakes")
def economic_impact_earthquakes(): return render_template("economic-impact-earthquakes.html")

@app.route("/future-seismicity-climate")
def future_seismicity_climate(): return render_template("future-seismicity-climate.html")

@app.route("/ancestral-earthquake-knowledge")
def ancestral_earthquake_knowledge(): return render_template("ancestral-earthquake-knowledge.html")

@app.route("/ethics-of-disaster-response")
def ethics_of_disaster_response(): return render_template("ethics-of-disaster-response.html")

# ================= API ENDPOINT =================
@app.route("/api/stats")
def api_stats():
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
        response = requests.get(url, timeout=5)
        data = response.json()
        features = data.get("features", [])
        total = len(features)
        significant = len([f for f in features if f["properties"].get("mag", 0) and f["properties"]["mag"] >= 4.5])
        max_mag = max([f["properties"].get("mag", 0) or 0 for f in features]) if features else 0
        return jsonify({"total": total, "significant": significant, "max_mag": max_mag, "countries": 50})
    except:
        return jsonify({"total": 0, "significant": 0, "max_mag": 0, "countries": 0})

# ================= ADMIN =================
@app.route("/rishav")
def rishav():
    if session.get("user_email") not in ADMIN_EMAILS:
        return redirect("/")
    return render_template("rishav.html")

@app.route("/edit_account")
def edit_account():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("edit_account.html")

# ================= ERROR HANDLER =================
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404

@app.errorhandler(500)
def error(e):
    return "Something went wrong. Please try again.", 500

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)