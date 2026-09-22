"""
MediSmart AI — MongoDB Connection
----------------------------------
Single connection module. Import `db` wherever database access is needed.
All collections are exposed as module-level variables for easy access.

Usage:
    from database import db, users_col, bookings_col, prescriptions_col, orders_col
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load .env file
load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME     = "MediSmart"

# ── Connect ────────────────────────────────────────────────────
_client = None
db      = None

# Collection references (set after successful connection)
users_col         = None
orders_col        = None
bookings_col      = None
prescriptions_col = None
medicines_col     = None
doctors_col       = None

MONGO_CONNECTED = False

def connect():
    """
    Attempt to connect to MongoDB.
    Returns True if successful, False if not.
    App continues with in-memory fallback if connection fails.
    """
    global _client, db
    global users_col, orders_col, bookings_col, prescriptions_col
    global medicines_col, doctors_col, MONGO_CONNECTED

    try:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=4000)
        # Force a connection to verify it works
        _client.admin.command("ping")

        db                = _client[DB_NAME]
        users_col         = db["users"]
        orders_col        = db["orders"]
        bookings_col      = db["bookings"]
        prescriptions_col = db["prescriptions"]
        medicines_col     = db["medicines"]
        doctors_col       = db["doctors"]

        # ── Indexes for fast lookup ────────────────────────────
        users_col.create_index("email", unique=True)
        bookings_col.create_index("email")
        prescriptions_col.create_index("email")
        orders_col.create_index("email")

        MONGO_CONNECTED = True
        print(f"✅ MongoDB connected → {DB_NAME}")
        return True

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        MONGO_CONNECTED = False
        print(f"⚠️  MongoDB not available ({e}). Running with in-memory storage.")
        return False
    except Exception as e:
        MONGO_CONNECTED = False
        print(f"⚠️  MongoDB error: {e}. Running with in-memory storage.")
        return False


# Auto-connect when this module is imported
connect()
