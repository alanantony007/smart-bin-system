import streamlit as st
import random, time, csv, os
from datetime import datetime

# ---------------- CONFIG ----------------
LOCAL_MODE = False   # True = local/bin demo | False = cloud demo
USERS_FILE = "users.csv"

st.set_page_config(page_title="Smart Bin System")
st.title("♻ Smart Waste Bin – Eco Rewards")

# ---------------- AUTO LOGIN VIA QR ----------------
query_user = st.query_params.get("user", None)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if query_user and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user = query_user

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:
    st.subheader("🔐 Login to Continue")
    st.markdown("📱 *Scan the QR code on the bin to open this page*")

    username = st.text_input("Enter your username")

    if st.button("Login"):
        if username.strip() == "":
            st.warning("Username cannot be empty")
        else:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Welcome {username} 🌱")
            st.rerun()

    st.stop()  # ⛔ Stop everything before login

# ---------------- CSV HELPERS ----------------
def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row["user"]] = {
                    "weight": int(row["weight"]),
                    "points": int(row["points"])
                }
    return users


def save_users(users):
    with open(USERS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["user", "weight", "points"])
        writer.writeheader()
        for u, d in users.items():
            writer.writerow({
                "user": u,
                "weight": d["weight"],
                "points": int(d["points"])
            })

# ---------------- USER INIT ----------------
user = st.session_state.user

if "users" not in st.session_state:
    st.session_state.users = load_users()

if user not in st.session_state.users:
    st.session_state.users[user] = {"weight": 0, "points": 0}
    save_users(st.session_state.users)

if "deposits" not in st.session_state:
    st.session_state.deposits = []

st.success(f"Connected as {user} 🌿")

# ---------------- WASTE DETECTION ----------------
def get_detected_waste():
    if LOCAL_MODE:
        try:
            with open("detected_waste.txt", "r") as f:
                waste = f.read().strip()
                if waste in ["Plastic", "Metal", "Paper"]:
                    return waste
        except:
            return None
    else:
        return random.choice(["Plastic", "Metal", "Paper"])

# ---------------- LIVE DETECTION ----------------
st.subheader("🔍 Live Waste Detection")

current_waste = get_detected_waste()
if current_waste:
    st.success(f"Detected: {current_waste}")
else:
    st.info("Waiting for waste...")

# ---------------- BIN ACTION ----------------
if st.button("🗑 Waste Deposited"):
    time.sleep(1)
    waste = get_detected_waste()

    if waste is None:
        st.warning("No waste detected")
    else:
        weight = random.randint(100, 700)

        if waste == "Plastic":
            points = weight * 1
        elif waste == "Metal":
            points = weight * 2
        else:
            points = weight * 0.5

        st.session_state.users[user]["weight"] += weight
        st.session_state.users[user]["points"] += points

        save_users(st.session_state.users)

        st.session_state.deposits.append({
            "user": user,
            "waste": waste,
            "weight": weight,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

        st.success(f"Waste: {waste}")
        st.success(f"Weight: {weight} g")
        st.success(f"Points Earned: {int(points)}")

# ---------------- USER STATS ----------------
st.info(f"♻ Total Waste: {st.session_state.users[user]['weight']} g")
st.info(f"⭐ Total Points: {int(st.session_state.users[user]['points'])}")

# ---------------- LAST DEPOSIT ----------------
st.subheader("🧾 Last Deposit")

if st.session_state.deposits:
    last = st.session_state.deposits[-1]
    st.success(
        f"{last['user']} deposited {last['weight']} g of {last['waste']} at {last['time']}"
    )
else:
    st.info("No deposits yet.")

# ---------------- ECO IMPACT ----------------
st.divider()

total_weight = sum(u["weight"] for u in st.session_state.users.values())
total_kg = total_weight / 1000

st.subheader("🌱 Eco Impact Dashboard")
st.metric("Total Waste Recycled", f"{total_kg:.2f} kg")
st.metric("CO₂ Saved", f"{total_kg * 1.5:.2f} kg")
st.metric("Trees Saved", f"{total_kg * 0.02:.2f}")

# ---------------- LEADERBOARD ----------------
st.subheader("🏆 Leaderboard (Top Recyclers)")

for i, (u, d) in enumerate(
    sorted(
        st.session_state.users.items(),
        key=lambda x: x[1]["points"],
        reverse=True
    ),
    1
):
    st.write(f"{i}. {u} — {int(d['points'])} pts")
