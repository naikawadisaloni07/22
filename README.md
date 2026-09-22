# MediSmart AI — Healthcare & Online Pharmacy Platform

AI-Powered Smart Healthcare & Online Pharmacy Management System  
Built with: **Python Flask · MongoDB · HTML/CSS/JS**

---

## Quick Start

### 1. Install Python
Download from https://python.org (3.10 or higher)  
✅ During install, check **"Add Python to PATH"**

### 2. Install dependencies
```
pip install flask pymongo python-dotenv
```

### 3. Configure MongoDB

**Option A — Local MongoDB (free, offline)**
1. Download MongoDB Community from https://mongodb.com/try/download/community
2. Install and start MongoDB service
3. No further config needed — app connects to `localhost:27017` by default

**Option B — MongoDB Atlas (free cloud)**
1. Go to https://cloud.mongodb.com
2. Create a free cluster
3. Click **Connect → Drivers → Python** and copy the connection string
4. Edit the `.env` file:
```
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

### 4. Run the server
```
python run.py
```

### 5. Open the app
Visit: **http://localhost:5000**

### 6. Check MongoDB connection
Visit: **http://localhost:5000/api/db-status**

You should see:
```json
{
  "mongodb_connected": true,
  "database": "MediSmart",
  "storage_mode": "MongoDB"
}
```

If MongoDB is not available, the app runs with in-memory fallback automatically.

---

## Project Structure

```
MediSmart/
├── app.py              ← Flask app + all routes
├── database.py         ← MongoDB connection module  ← NEW
├── run.py              ← Dev server launcher
├── requirements.txt    ← Python dependencies
├── .env                ← MongoDB URI (do not commit!)  ← NEW
├── .gitignore          ← Protects .env from git  ← NEW
├── data/
│   ├── medicines.py    ← 75 medicines static data
│   ├── doctors.py      ← 8 doctors static data
│   └── image_urls.py   ← Reliable image URLs
├── static/
│   ├── css/style.css
│   └── js/
│       ├── cart.js
│       ├── main.js
│       └── imgfix.js
└── templates/
    ├── base.html
    ├── index.html
    ├── medicines.html
    ├── medicine_detail.html
    ├── cart.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── prescription.html
    ├── ai_assistant.html
    ├── consult.html
    ├── doctor_detail.html
    ├── book_consultation.html
    └── 404.html
```

---

## MongoDB Collections

| Collection | Stores |
|---|---|
| `users` | Registered user accounts |
| `bookings` | Doctor consultation bookings |
| `prescriptions` | Uploaded prescription records |
| `orders` | Medicine orders |
| `medicines` | (Ready for future migration) |
| `doctors` | (Ready for future migration) |

---

## Pages & Routes

| Route | Page |
|---|---|
| `/` | Homepage |
| `/medicines` | Medicine listing with filters |
| `/medicine/<id>` | Medicine detail |
| `/cart` | Shopping cart |
| `/login` | Login |
| `/register` | Register |
| `/dashboard` | User dashboard |
| `/prescription` | Upload prescription |
| `/consult` | Doctor listing |
| `/consult/<id>` | Doctor profile |
| `/book/<id>` | Book consultation |
| `/ai-assistant` | AI Health Assistant |
| `/api/db-status` | MongoDB connection check |

---

## Coupon Codes (for testing)
| Code | Discount |
|---|---|
| `MEDI20` | 20% off |
| `FIRST99` | ₹99 flat off |
| `HEALTH10` | 10% off |
