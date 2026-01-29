
import streamlit as st
import random, time

st.set_page_config(page_title="Smart Bin System")


st.title("♻ Smart Waste Bin – Eco Rewards")

# 🔴 CHANGE THIS IP if needed
APP_URL = "https://smart-bin-system.streamlit.app"



st.subheader("📱 Scan QR Code on the Bin")
st.qr_code(APP_URL)

# --------- Waste detection reader ----------
def get_detected_waste():
    try:
        with open("detected_waste.txt", "r") as f:
            waste = f.read().strip()
            if waste in ["Plastic", "Metal", "Paper"]:
                return waste
            else:
                return None
    except:
        return None

# --------- User system ----------
if "users" not in st.session_state:
    st.session_state.users = {}

user = st.query_params.get("user", "EcoUser")

if user not in st.session_state.users:
    st.session_state.users[user] = {"weight": 0, "points": 0}

st.success(f"Connected as {user} 🌱")
current_waste = get_detected_waste()

st.subheader("🔍 Live Waste Detection")
if current_waste:
    st.success(f"Detected: {current_waste}")
else:
    st.info("Waiting for waste...")


# --------- Smart bin automation ----------
if st.button("🗑 Waste Deposited"):

    st.write("Detecting waste...")
    time.sleep(1)

    waste = get_detected_waste()

    if waste is None:
        st.warning("⚠️ No waste detected yet. Please insert waste.")
    else:
        st.write("Measuring weight...")
        time.sleep(1)

        weight = random.randint(100, 700)

        if waste == "Plastic":
            points = weight * 1
        elif waste == "Metal":
            points = weight * 2
        else:
            points = weight * 0.5

        st.session_state.users[user]["weight"] += weight
        st.session_state.users[user]["points"] += points

        st.success(f"Detected: {waste}")
        st.success(f"Weight: {weight} g")
        st.warning(f"Points earned: {int(points)}")

# --------- User stats ----------
st.info(f"♻ Total Waste: {int(st.session_state.users[user]['weight'])} g")
st.info(f"⭐ Total Points: {int(st.session_state.users[user]['points'])}")

st.divider()

# --------- Eco Impact ----------
total_weight = sum(u["weight"] for u in st.session_state.users.values())
total_kg = total_weight / 1000

co2_saved = total_kg * 1.5
trees_saved = total_kg * 0.02

st.subheader("🌱 Eco Impact Dashboard")
st.metric("♻ Total Waste Recycled", f"{total_kg:.2f} kg")
st.metric("🌍 CO₂ Saved", f"{co2_saved:.2f} kg")
st.metric("🌳 Trees Saved", f"{trees_saved:.2f}")

# --------- Leaderboard ----------
st.subheader("🏆 Leaderboard")
for i, (u, d) in enumerate(
    sorted(st.session_state.users.items(),
           key=lambda x: x[1]["points"], reverse=True), 1):
    st.write(f"{i}. {u} — {int(d['points'])} pts")



