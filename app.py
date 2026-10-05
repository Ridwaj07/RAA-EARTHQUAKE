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
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'raa.earthquake.2.0@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'soeg zmof dhse utjs')

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

# ================= USER MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))

# ================= MODELS & SEEDING =================
import json
from models import init_models
from seed_data import seed_all

models = init_models(db)

with app.app_context():
    db.create_all()
    seed_all(db, models)


# ================= HOME =================
@app.route("/")
def home():
    disasters = models.DisasterType.query.filter_by(is_active=True).order_by(models.DisasterType.display_order.asc()).all()
    featured_states = models.IndianState.query.filter(models.IndianState.seismic_zone.in_(['Zone V', 'Zone IV'])).limit(6).all()
    return render_template("index.html", disasters=disasters, featured_states=featured_states)


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

@app.route("/sitemap.xml")
def sitemap():
    base_url = "https://raa-earthquake2-0.onrender.com"
    pages = []
    # Dynamic list of routes to include in sitemap
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            # Exclude non-public or utility routes
            if rule.rule not in ["/rishav", "/logout", "/account", "/edit_account", "/sitemap.xml", "/robots.txt", "/ads.txt", "/ping", "/login", "/signup"]:
                if not rule.rule.startswith("/api/"):
                    pages.append(base_url + rule.rule)
    
    # Append dynamic multi-disaster pages
    try:
        disasters = models.DisasterType.query.filter_by(is_active=True).all()
        for d in disasters:
            pages.append(f"{base_url}/disasters/{d.slug}")
        states = models.IndianState.query.all()
        for s in states:
            pages.append(f"{base_url}/india-disaster-risk/{s.slug}")
        events = models.HistoricalEvent.query.all()
        for e in events:
            pages.append(f"{base_url}/historic-disasters/{e.id}")
    except Exception as err:
        print("SITEMAP DYNAMIC ERR:", err)
    
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in sorted(list(set(pages))):
        sitemap_xml += f'  <url><loc>{page}</loc><lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod><changefreq>daily</changefreq></url>\n'
    sitemap_xml += '</urlset>'
    
    return sitemap_xml, 200, {'Content-Type': 'application/xml'}


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

# ================= MULTI-DISASTER PLATFORM ROUTES =================

@app.route("/disasters")
def disasters_hub():
    disasters = models.DisasterType.query.filter_by(is_active=True).order_by(models.DisasterType.display_order.asc()).all()
    categories = {}
    for d in disasters:
        cat = d.category or "General"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(d)
    return render_template("disasters/index.html", categories=categories, disasters=disasters)

@app.route("/disasters/<slug>")
def disaster_detail(slug):
    disaster = models.DisasterType.query.filter_by(slug=slug, is_active=True).first_or_404()
    guide = models.SafetyGuide.query.filter_by(disaster_slug=slug, is_active=True).first()
    before_steps = json.loads(guide.before_steps) if (guide and guide.before_steps) else []
    during_steps = json.loads(guide.during_steps) if (guide and guide.during_steps) else []
    after_steps = json.loads(guide.after_steps) if (guide and guide.after_steps) else []
    
    events = models.HistoricalEvent.query.filter_by(disaster_type=slug).order_by(models.HistoricalEvent.year.desc()).all()
    other_disasters = models.DisasterType.query.filter(models.DisasterType.slug != slug, models.DisasterType.is_active == True).limit(6).all()
    
    return render_template("disasters/detail.html", disaster=disaster, guide=guide, before_steps=before_steps, during_steps=during_steps, after_steps=after_steps, events=events, other_disasters=other_disasters)

@app.route("/india-disaster-risk")
def india_risk():
    states = models.IndianState.query.order_by(models.IndianState.name.asc()).all()
    for s in states:
        s.hazards_list = json.loads(s.major_hazards) if s.major_hazards else []
    return render_template("india_risk/index.html", states=states)

@app.route("/india-disaster-risk/<slug>")
def state_risk_detail(slug):
    state = models.IndianState.query.filter_by(slug=slug).first_or_404()
    hazards_list = json.loads(state.major_hazards) if state.major_hazards else []
    hazard_objs = models.DisasterType.query.filter(models.DisasterType.slug.in_(hazards_list)).all() if hazards_list else []
    contacts = models.EmergencyContact.query.filter((models.EmergencyContact.state == state.name) | (models.EmergencyContact.country == 'India')).all()
    events = models.HistoricalEvent.query.filter_by(state=state.name).order_by(models.HistoricalEvent.year.desc()).all()
    return render_template("india_risk/detail.html", state=state, hazard_objs=hazard_objs, contacts=contacts, events=events)

@app.route("/preparedness")
def preparedness():
    guides = models.SafetyGuide.query.filter_by(is_active=True).all()
    disasters = models.DisasterType.query.filter_by(is_active=True).all()
    return render_template("preparedness/index.html", guides=guides, disasters=disasters)

@app.route("/emergency-contacts")
def emergency_contacts():
    contacts = models.EmergencyContact.query.filter_by(is_active=True).all()
    national_contacts = [c for c in contacts if not c.state or c.country == 'India']
    state_contacts = [c for c in contacts if c.state]
    return render_template("preparedness/emergency_contacts.html", national_contacts=national_contacts, state_contacts=state_contacts)

@app.route("/disaster-kit-guide")
def disaster_kit_guide():
    return render_template("preparedness/kit_guide.html")

@app.route("/disaster-glossary")
def disaster_glossary():
    query = request.args.get("q", "").strip()
    category = request.args.get("cat", "").strip()
    
    terms_query = models.GlossaryTerm.query
    if query:
        terms_query = terms_query.filter(models.GlossaryTerm.term.ilike(f"%{query}%") | models.GlossaryTerm.simple_definition.ilike(f"%{query}%"))
    if category:
        terms_query = terms_query.filter_by(category=category)
        
    terms = terms_query.order_by(models.GlossaryTerm.term.asc()).all()
    categories_raw = db.session.query(models.GlossaryTerm.category).distinct().all()
    categories = [c[0] for c in categories_raw if c[0]]
    
    return render_template("resources/glossary.html", terms=terms, query=query, category=category, categories=categories)

@app.route("/official-data-sources")
def official_data_sources():
    sources = models.DataSource.query.order_by(models.DataSource.priority.asc()).all()
    return render_template("resources/data_sources.html", sources=sources)

@app.route("/live-disaster-feeds")
def live_disaster_feeds():
    sources = models.DataSource.query.filter_by(status='operational').all()
    return render_template("resources/live_feeds.html", sources=sources)

@app.route("/historic-disasters")
def historic_disasters():
    events = models.HistoricalEvent.query.order_by(models.HistoricalEvent.year.desc()).all()
    disasters = models.DisasterType.query.filter_by(is_active=True).all()
    return render_template("resources/historic.html", events=events, disasters=disasters)

@app.route("/historic-disasters/<int:event_id>")
def historic_disaster_detail(event_id):
    event = models.HistoricalEvent.query.get_or_404(event_id)
    related_disaster = models.DisasterType.query.filter_by(slug=event.disaster_type).first()
    return render_template("resources/historic_detail.html", event=event, related_disaster=related_disaster)

# ================= CORE PLATFORM PAGES (QUALITY UPGRADE) =================

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/how-it-works")
def how_it_works():
    return render_template("how-it-works.html")

@app.route("/official-resources")
def official_resources():
    return render_template("official-resources.html")

@app.route("/earthquake-search")
def earthquake_search():
    return render_template("earthquake_search.html")

@app.route("/earthquake/<event_id>")
@app.route("/earthquake-detail/<event_id>")
def earthquake_detail(event_id):
    eq_data = None
    error_msg = None
    try:
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid={event_id}&format=geojson"
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            eq_data = res.json()
        else:
            error_msg = "Earthquake record not found or unavailable."
    except Exception as e:
        print("DETAIL API ERROR:", e)
        error_msg = "Unable to fetch live event details from USGS at this moment."
    
    return render_template("earthquake_detail.html", event_id=event_id, eq=eq_data, error_msg=error_msg)

# ================= API ENDPOINTS =================

@app.route("/api/earthquakes")
def api_earthquakes():
    feed = request.args.get("feed", "all_day") # all_hour, all_day, all_week, all_month, 4.5_day, 2.5_day, significant_month
    min_mag = request.args.get("min_mag", type=float)
    query = request.args.get("q", "").strip().lower()
    
    valid_feeds = {
        "hour": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
        "all_day": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
        "all_week": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson",
        "all_month": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson",
        "m45_day": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson",
        "m45_week": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson",
        "m45_month": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson",
        "significant_month": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
    }
    
    feed_url = valid_feeds.get(feed, valid_feeds["all_day"])
    try:
        response = requests.get(feed_url, timeout=7)
        data = response.json()
        features = data.get("features", [])
        
        results = []
        for f in features:
            props = f.get("properties", {})
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [0, 0, 0])
            mag = props.get("mag") or 0.0
            place = props.get("place") or "Unknown location"
            time_ms = props.get("time") or 0
            
            if min_mag is not None and mag < min_mag:
                continue
            if query and query not in place.lower():
                continue
                
            results.append({
                "id": f.get("id"),
                "place": place,
                "mag": round(mag, 1),
                "time": time_ms,
                "time_formatted": datetime.utcfromtimestamp(time_ms / 1000).strftime("%Y-%m-%d %H:%M:%S UTC") if time_ms else "N/A",
                "longitude": coords[0] if len(coords) > 0 else None,
                "latitude": coords[1] if len(coords) > 1 else None,
                "depth_km": coords[2] if len(coords) > 2 else None,
                "url": props.get("url"),
                "status": props.get("status"),
                "tsunami": props.get("tsunami", 0),
                "felt": props.get("felt"),
                "alert": props.get("alert")
            })
            
        return jsonify({
            "count": len(results),
            "generated": data.get("metadata", {}).get("generated"),
            "earthquakes": results[:200]
        })
    except Exception as e:
        print("API SEARCH ERROR:", e)
        return jsonify({"error": "Failed to fetch earthquakes", "earthquakes": []}), 500

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
        return jsonify({"total": total, "significant": significant, "max_mag": max_mag, "countries": "Global"})
    except:
        return jsonify({"total": 0, "significant": 0, "max_mag": 0, "countries": "Global"})

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

# ================= ERROR HANDLERS =================
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("404.html", error_title="500 — Server Error", error_msg="Something went wrong processing your request. Please try again shortly."), 500

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)