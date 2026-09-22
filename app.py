from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from urllib.parse import quote
from functools import wraps
from dotenv import load_dotenv
import os

from data.medicines import MEDICINES, CATEGORIES
from data.doctors   import DOCTORS, SPECIALTIES, AI_SYMPTOM_MAP
from data.image_urls import MEDICINE_IMAGES
import database  # MongoDB connection module

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "medismart_secret_key_2024")

# ── Jinja2 custom filter ──────────────────────────────────────
app.jinja_env.filters['urlencode'] = lambda s: quote(str(s), safe='')

# ── Patch all medicine images with reliable URLs ──────────────
for med in MEDICINES:
    if med["id"] in MEDICINE_IMAGES:
        med["image"] = MEDICINE_IMAGES[med["id"]]

# ── In-memory fallback stores ─────────────────────────────────
# Used when MongoDB is not available. Replaced by DB ops below.
USERS_MEM         = {}   # { email: {name, email, password, phone} }
ORDERS_MEM        = []
BOOKINGS_MEM      = []
PRESCRIPTIONS_MEM = []

# ── Helper: are we using MongoDB? ────────────────────────────
def use_mongo():
    return database.MONGO_CONNECTED

# ── Auth helpers ──────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_email" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def current_user():
    email = session.get("user_email")
    if not email:
        return None
    if use_mongo():
        user = database.users_col.find_one({"email": email}, {"_id": 0})
        return user
    return USERS_MEM.get(email)

def get_medicine_by_id(med_id):
    return next((m for m in MEDICINES if m["id"] == int(med_id)), None)

def get_doctor_by_id(doc_id):
    return next((d for d in DOCTORS if d["id"] == int(doc_id)), None)

# ════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ════════════════════════════════════════════════════════════════

# ── Home ─────────────────────────────────────────────────────
@app.route("/")
def index():
    featured = sorted(MEDICINES, key=lambda x: x["rating"], reverse=True)[:12]
    return render_template("index.html", medicines=featured, categories=CATEGORIES)

# ── Medicines ────────────────────────────────────────────────
@app.route("/medicines")
def medicines():
    category  = request.args.get("category", "")
    search    = request.args.get("search", "").lower()
    sort      = request.args.get("sort", "")
    price_max = request.args.get("price_max", 9999, type=int)
    rx_filter = request.args.get("rx", "")

    result = list(MEDICINES)
    if category:
        result = [m for m in result if m["category"].lower() == category.lower()]
    if search:
        result = [m for m in result if search in m["name"].lower()
                  or search in m["brand"].lower()
                  or any(search in t for t in m["tags"])]
    if price_max < 9999:
        result = [m for m in result if m["price"] <= price_max]
    if rx_filter == "otc":
        result = [m for m in result if not m["prescription_required"]]
    elif rx_filter == "rx":
        result = [m for m in result if m["prescription_required"]]

    sort_map = {
        "price_asc":  (lambda x: x["price"],    False),
        "price_desc": (lambda x: x["price"],    True),
        "discount":   (lambda x: x["discount"], True),
        "rating":     (lambda x: x["rating"],   True),
    }
    if sort in sort_map:
        key, rev = sort_map[sort]
        result.sort(key=key, reverse=rev)

    return render_template("medicines.html", medicines=result, categories=CATEGORIES,
                           active_category=category, search_query=search,
                           sort=sort, total=len(result))

@app.route("/medicine/<int:med_id>")
def medicine_detail(med_id):
    medicine = get_medicine_by_id(med_id)
    if not medicine:
        return render_template("404.html"), 404
    related = [m for m in MEDICINES
               if m["category"] == medicine["category"] and m["id"] != med_id][:4]
    return render_template("medicine_detail.html", medicine=medicine, related=related)

# ── Cart ─────────────────────────────────────────────────────
@app.route("/cart")
def cart():
    return render_template("cart.html")

# ── Login / Register / Logout ────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if use_mongo():
            user = database.users_col.find_one({"email": email})
        else:
            user = USERS_MEM.get(email)

        if user and user["password"] == password:
            session["user_email"] = email
            session["user_name"]  = user["name"]
            flash(f"Welcome back, {user['name']}! 👋", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        phone    = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm_password", "").strip()

        # Check if email already exists
        if use_mongo():
            exists = database.users_col.find_one({"email": email})
        else:
            exists = USERS_MEM.get(email)

        if exists:
            flash("An account with this email already exists.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            user_doc = {"name": name, "email": email,
                        "phone": phone, "password": password}
            if use_mongo():
                try:
                    database.users_col.insert_one(user_doc)
                except Exception as e:
                    flash("Registration failed. Please try again.", "error")
                    return render_template("register.html")
            else:
                USERS_MEM[email] = user_doc

            session["user_email"] = email
            session["user_name"]  = name
            flash(f"Account created! Welcome to MediSmart, {name}! 🎉", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# ── Dashboard ────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    email = session["user_email"]
    user  = current_user()

    if use_mongo():
        user_bookings      = list(database.bookings_col.find(
            {"email": email}, {"_id": 0}))
        user_prescriptions = list(database.prescriptions_col.find(
            {"email": email}, {"_id": 0}))
    else:
        user_bookings      = [b for b in BOOKINGS_MEM      if b["email"] == email]
        user_prescriptions = [p for p in PRESCRIPTIONS_MEM if p["email"] == email]

    return render_template("dashboard.html",
                           user=user,
                           bookings=user_bookings,
                           prescriptions=user_prescriptions)

# ── Prescription Upload ──────────────────────────────────────
@app.route("/prescription", methods=["GET", "POST"])
@login_required
def prescription():
    if request.method == "POST":
        doctor_name = request.form.get("doctor_name", "").strip()
        notes       = request.form.get("notes", "").strip()
        file        = request.files.get("prescription_file")
        filename    = file.filename if file and file.filename else "No file uploaded"
        rx_doc = {
            "email":       session["user_email"],
            "doctor_name": doctor_name,
            "notes":       notes,
            "filename":    filename,
            "status":      "Under Review"
        }
        if use_mongo():
            database.prescriptions_col.insert_one(rx_doc)
        else:
            PRESCRIPTIONS_MEM.append(rx_doc)

        flash("Prescription uploaded successfully! Our pharmacist will verify it shortly. ✅", "success")
        return redirect(url_for("dashboard"))
    return render_template("prescription.html")

# ── AI Health Assistant ──────────────────────────────────────
@app.route("/ai-assistant")
def ai_assistant():
    return render_template("ai_assistant.html", medicines=MEDICINES)

@app.route("/api/ai/ask", methods=["POST"])
def ai_ask():
    data     = request.get_json() or {}
    question = data.get("question", "").lower().strip()
    medicine = data.get("medicine", "").strip()

    if not question:
        return jsonify({"answer": "Please ask a question.", "type": "warning"})

    # Medicine-specific questions
    if medicine:
        med_obj = next((m for m in MEDICINES
                        if m["name"].lower() == medicine.lower()), None)
        if med_obj:
            if any(k in question for k in ["after food", "with food", "before food", "empty stomach"]):
                return jsonify({"answer": f"<strong>{med_obj['name']}</strong> is best taken after food to reduce stomach irritation. Always follow your doctor's specific instructions.", "type": "info"})
            if any(k in question for k in ["side effect", "bloating", "nausea", "effect"]):
                effects = ", ".join(med_obj["side_effects"])
                return jsonify({"answer": f"Common side effects of <strong>{med_obj['name']}</strong>: {effects}. Contact your doctor if these persist.", "type": "warning"})
            if any(k in question for k in ["dose", "dosage", "how much", "how many"]):
                return jsonify({"answer": f"<strong>Dosage for {med_obj['name']}</strong>: {med_obj['dosage']}", "type": "info"})
            if any(k in question for k in ["missed", "forget", "skip"]):
                return jsonify({"answer": f"If you missed a dose of <strong>{med_obj['name']}</strong>, take it as soon as you remember. If it's almost time for the next dose, skip the missed one. Never double up.", "type": "info"})
            if any(k in question for k in ["interact", "combination", "with other"]):
                inter = ", ".join(med_obj["interactions"])
                return jsonify({"answer": f"<strong>{med_obj['name']}</strong> may interact with: {inter}. Always inform your doctor of all medicines you are taking.", "type": "warning"})
            if any(k in question for k in ["precaution", "warning", "avoid"]):
                prec = ", ".join(med_obj["precautions"])
                return jsonify({"answer": f"<strong>Precautions for {med_obj['name']}</strong>: {prec}.", "type": "warning"})
            if any(k in question for k in ["use", "for what", "treats", "benefit"]):
                uses = ", ".join(med_obj["uses"])
                return jsonify({"answer": f"<strong>{med_obj['name']}</strong> is used for: {uses}.", "type": "success"})

    # General health questions
    general_answers = {
        ("fever", "temperature"):       ("For mild fever, rest and stay hydrated. Paracetamol 500mg can help reduce temperature. Seek medical attention if fever exceeds 103°F or lasts more than 3 days.", "info"),
        ("headache",):                  ("Common causes include dehydration, stress, or eye strain. Drink water, rest in a dark room. If severe or frequent, consult a doctor.", "info"),
        ("cold", "runny nose"):         ("Rest, stay warm, and drink plenty of fluids. Steam inhalation helps. Antihistamines like Cetirizine can relieve symptoms.", "info"),
        ("diabetes", "blood sugar"):    ("Monitor blood sugar regularly, follow prescribed medications, eat a balanced low-GI diet, and exercise daily. Regular check-ups are essential.", "info"),
        ("bp", "blood pressure", "hypertension"): ("Reduce salt intake, exercise regularly, avoid stress. Take prescribed BP medication consistently. Monitor BP at home.", "info"),
        ("stomach", "gastric", "acidity", "heartburn"): ("Avoid spicy and oily food, eat smaller meals. Antacids or Omeprazole can help. Consult a doctor if symptoms persist.", "info"),
        ("sleep", "insomnia"):          ("Maintain a regular sleep schedule, avoid screens before bed, limit caffeine. Consult a doctor if insomnia persists beyond 2 weeks.", "info"),
        ("vitamin", "deficiency"):      ("Common deficiencies in India include Vitamin D3, B12, and Iron. A blood test can confirm deficiency. Supplements help when prescribed.", "info"),
    }
    for keywords, (answer, atype) in general_answers.items():
        if any(k in question for k in keywords):
            return jsonify({"answer": answer, "type": atype})

    return jsonify({
        "answer": "I'm not sure about that specific question. Please select a medicine above for detailed information, or consult a certified doctor on our platform for personalised advice.",
        "type": "info"
    })

# ── Doctor Consultation ──────────────────────────────────────
@app.route("/consult")
def consult():
    specialty = request.args.get("specialty", "")
    symptom   = request.args.get("symptom", "").lower()
    result    = list(DOCTORS)

    if specialty:
        result = [d for d in result if d["specialty"].lower() == specialty.lower()]

    # AI symptom-based recommendation
    recommended_ids = []
    if symptom:
        for keyword, doc_ids in AI_SYMPTOM_MAP.items():
            if keyword in symptom:
                recommended_ids.extend(doc_ids)
        recommended_ids = list(set(recommended_ids))
        if recommended_ids:
            result = [d for d in DOCTORS if d["id"] in recommended_ids]

    return render_template("consult.html", doctors=result,
                           specialties=SPECIALTIES,
                           active_specialty=specialty,
                           symptom_query=symptom)

@app.route("/consult/<int:doc_id>")
def doctor_detail(doc_id):
    doctor = get_doctor_by_id(doc_id)
    if not doctor:
        return render_template("404.html"), 404
    related = [d for d in DOCTORS if d["specialty"] == doctor["specialty"] and d["id"] != doc_id][:3]
    return render_template("doctor_detail.html", doctor=doctor, related=related)

@app.route("/book/<int:doc_id>", methods=["GET", "POST"])
@login_required
def book_consultation(doc_id):
    doctor = get_doctor_by_id(doc_id)
    if not doctor:
        return render_template("404.html"), 404
    if request.method == "POST":
        consult_type = request.form.get("consult_type", "chat")
        slot         = request.form.get("slot", "")
        date         = request.form.get("date", "")
        symptoms     = request.form.get("symptoms", "")
        fee_map      = {"chat": doctor["fee_chat"], "audio": doctor["fee_audio"], "video": doctor["fee_video"]}
        fee          = fee_map.get(consult_type, doctor["fee_chat"])
        booking_doc = {
            "email":        session["user_email"],
            "doctor_name":  doctor["name"],
            "specialty":    doctor["specialty"],
            "consult_type": consult_type,
            "slot":         slot,
            "date":         date,
            "symptoms":     symptoms,
            "fee":          fee,
            "status":       "Confirmed"
        }
        if use_mongo():
            database.bookings_col.insert_one(booking_doc)
        else:
            BOOKINGS_MEM.append(booking_doc)

        flash(f"✅ Consultation with {doctor['name']} booked for {date} at {slot}! Check your dashboard.", "success")
        return redirect(url_for("dashboard"))
    return render_template("book_consultation.html", doctor=doctor)

# ════════════════════════════════════════════════════════════════
# API ROUTES
# ════════════════════════════════════════════════════════════════
@app.route("/api/medicines")
def api_medicines():
    return jsonify(MEDICINES)

@app.route("/api/medicines/<int:med_id>")
def api_medicine_detail(med_id):
    medicine = get_medicine_by_id(med_id)
    if not medicine:
        return jsonify({"error": "Medicine not found"}), 404
    return jsonify(medicine)

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").lower()
    if not q:
        return jsonify([])
    results = [
        {"id": m["id"], "name": m["name"], "brand": m["brand"],
         "price": m["price"], "category": m["category"]}
        for m in MEDICINES
        if q in m["name"].lower() or q in m["brand"].lower()
           or any(q in t for t in m["tags"])
    ][:8]
    return jsonify(results)

@app.route("/api/categories")
def api_categories():
    return jsonify(CATEGORIES)

@app.route("/api/doctors")
def api_doctors():
    return jsonify(DOCTORS)

# ── MongoDB status check ──────────────────────────────────────
@app.route("/api/db-status")
def db_status():
    return jsonify({
        "mongodb_connected": database.MONGO_CONNECTED,
        "database": "MediSmart" if database.MONGO_CONNECTED else None,
        "storage_mode": "MongoDB" if database.MONGO_CONNECTED else "In-Memory (fallback)"
    })

# ── Error handlers ────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
