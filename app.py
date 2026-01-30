import streamlit as st
import random, time
from datetime import datetime

st.set_page_config(page_title="Smart Bin System")

st.title("♻ Smart Waste Bin – Eco Rewards")

# ---------------- LOGIN CONTROL ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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

    st.stop()  # ⛔ Do NOT show dashboard before login

# ---------------- USER INITIALIZATION ----------------
user = st.session_state.user

if "users" not in st.session_state:
    st.session_state.users = {}

if user not in st.session_state.users:
    st.session_state.users[user] = {"weight": 0, "points": 0}

# ---------------- DEPOSIT LOG ----------------
if "deposits" not in st.session_state:
    st.session_state.deposits = []

st.success(f"Connected as {user} 🌿")

# ---------------- WASTE DETECTION (SIMULATED) ----------------
def get_detected_waste():
    # In real deployment: camera + sensors
    return random.choice(["Plastic", "Metal", "Paper"])

st.subheader("🔍 Live Waste Detection")
st.info("Waiting for waste...")

# ---------------- BIN ACTION ----------------
if st.button("🗑 Waste Deposited"):

    st.write("Detecting waste...")
    time.sleep(1)

    waste = get_detected_waste()
    weight = random.randint(100, 700)

    if waste == "Plastic":
        points = weight * 1
    elif waste == "Metal":
        points = weight * 2
    else:
        points = weight * 0.5

    # Update user stats
    st.session_state.users[user]["weight"] += weight
    st.session_state.users[user]["points"] += points

    # Log deposit
    st.session_state.deposits.append({
        "user": user,
        "waste": waste,
        "weight": weight,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })

    st.success(f"Detected Waste: {waste}")
    st.success(f"Weight: {weight} g")
    st.warning(f"Points Earned: {int(points)}")

# ---------------- USER STATS ----------------
st.info(f"♻ Total Waste Deposited: {st.session_state.users[user]['weight']} g")
st.info(f"⭐ Total Points: {int(st.session_state.users[user]['points'])}")

# ---------------- LAST DEPOSIT ----------------
st.subheader("🧾 Last Deposit")

if st.session_state.deposits:
    last = st.session_state.deposits[-1]
    st.success(
        f"{last['user']} deposited {last['weight']} g of {last['waste']} waste at {last['time']}"
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
st.subheader("🏆 Leaderboard")

for i, (u, d) in enumerate(
    sorted(st.session_state.users.items(),
           key=lambda x: x[1]["points"],
           reverse=True),
    1
):
    st.write(f"{i}. {u} — {int(d['points'])} pts")
