import streamlit as st
import random, time, csv, os
from datetime import datetime

# ================= CONFIG =================
LOCAL_MODE = True        # 🔁 True = local camera | False = cloud demo
BIN_ID = "BIN-01"

USERS_FILE = "users.csv"
COOLDOWN_SECONDS = 10

POINTS_PER_RUPEE = 1000
MIN_REDEEM_RUPEES = 10

ENTERTAINMENT_REWARDS = {
    "🎢 Wonderla Entry Ticket (₹200)": 200,
    "🎬 Movie Ticket Coupon (₹150)": 150,
    "🎡 Theme Park Discount (₹300)": 300
}

GIFT_CARDS = {
    "🛒 Amazon Gift Card (₹100)": 100,
    "🎮 Google Play Gift Card (₹150)": 150,
    "🍔 Zomato Gift Card (₹200)": 200
}

# ================= PAGE SETUP =================
st.set_page_config(page_title="Smart Bin System")
st.title("♻ Smart Waste Bin – Eco Rewards")
st.caption(f"🗑 Active Bin: {BIN_ID}")

# ================= AUTO LOGIN (QR) =================
query_user = st.query_params.get("user")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if query_user and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user = query_user

# ================= LOGIN PAGE =================
if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username = st.text_input("Enter your username")

    if st.button("Login"):
        if username.strip():
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.warning("Username cannot be empty")
    st.stop()

# ================= CSV HELPERS =================
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

# ================= USER INIT =================
user = st.session_state.user

if "users" not in st.session_state:
    st.session_state.users = load_users()

if user not in st.session_state.users:
    st.session_state.users[user] = {"weight": 0, "points": 0}
    save_users(st.session_state.users)

if "deposits" not in st.session_state:
    st.session_state.deposits = []

if "last_deposit_time" not in st.session_state:
    st.session_state.last_deposit_time = 0

st.success(f"Connected as {user} 🌿")

# ================= LOGOUT =================
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# ================= WASTE DETECTION =================
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

# ================= LIVE STATUS =================
st.subheader("🔍 Live Waste Detection")

current = get_detected_waste()
if current:
    st.success(f"Detected: {current}")
else:
    st.info("Waiting for waste...")

# ================= DEPOSIT ACTION =================
st.subheader("🗑 Deposit Waste")

if st.button("Deposit Waste"):
    now = time.time()
    if now - st.session_state.last_deposit_time < COOLDOWN_SECONDS:
        st.warning("⏳ Please wait before next deposit")
    else:
        st.session_state.last_deposit_time = now
        waste = get_detected_waste()

        if waste is None:
            st.warning("⚠️ No waste detected")
        else:
            weight = random.randint(100, 700)
            multiplier = 2 if waste == "Metal" else 1 if waste == "Plastic" else 0.5
            points = int(weight * multiplier)

            st.session_state.users[user]["weight"] += weight
            st.session_state.users[user]["points"] += points
            save_users(st.session_state.users)

            st.session_state.deposits.append({
                "user": user,
                "bin": BIN_ID,
                "waste": waste,
                "weight": weight,
                "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            })

            st.success(f"Waste: {waste}")
            st.success(f"Weight: {weight} g")
            st.success(f"Points Earned: {points}")

# ================= WALLET =================
points_balance = st.session_state.users[user]["points"]
rupees_balance = points_balance / POINTS_PER_RUPEE

st.subheader("💰 Wallet")
st.info(f"Points: {points_balance}")
st.info(f"Value: ₹{rupees_balance:.2f}")

# ================= USER RANK =================
sorted_users = sorted(
    st.session_state.users.items(),
    key=lambda x: x[1]["points"],
    reverse=True
)

rank = next(i + 1 for i, (u, _) in enumerate(sorted_users) if u == user)
medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""

st.subheader("🏅 Your Rank")
st.success(f"#{rank} {medal}")

# ================= HISTORY =================
st.subheader("📜 My Deposit History")

my_deposits = [d for d in reversed(st.session_state.deposits) if d["user"] == user]

if my_deposits:
    for d in my_deposits[:5]:
        st.write(f"• {d['time']} — {d['waste']} — {d['weight']} g — {d['bin']}")
else:
    st.info("No deposits yet")

# ================= REDEEM =================
st.subheader("🎁 Redeem Rewards")

redeem_type = st.radio(
    "Choose redeem option",
    ["🏦 Bank Transfer", "🎟 Entertainment Coupons", "🛒 Gift Cards"]
)

# Bank
if redeem_type == "🏦 Bank Transfer":
    amount = st.number_input("Amount (₹)", min_value=0, step=1)
    need = amount * POINTS_PER_RUPEE

    if st.button("Redeem to Bank"):
        if amount < MIN_REDEEM_RUPEES:
            st.error("Minimum redeem ₹10")
        elif points_balance < need:
            st.error("Not enough points")
        else:
            st.session_state.users[user]["points"] -= need
            save_users(st.session_state.users)
            st.success(f"₹{amount} transferred (simulated)")

# Coupons
elif redeem_type == "🎟 Entertainment Coupons":
    reward = st.selectbox("Select coupon", list(ENTERTAINMENT_REWARDS))
    need = ENTERTAINMENT_REWARDS[reward] * POINTS_PER_RUPEE

    if st.button("Redeem Coupon"):
        if points_balance < need:
            st.error("Not enough points")
        else:
            st.session_state.users[user]["points"] -= need
            save_users(st.session_state.users)
            st.success(f"{reward} issued!")

# Gift cards
else:
    reward = st.selectbox("Select gift card", list(GIFT_CARDS))
    need = GIFT_CARDS[reward] * POINTS_PER_RUPEE

    if st.button("Redeem Gift Card"):
        if points_balance < need:
            st.error("Not enough points")
        else:
            st.session_state.users[user]["points"] -= need
            save_users(st.session_state.users)
            st.success(f"{reward} issued!")

# ================= LEADERBOARD =================
st.divider()
st.subheader("🏆 Leaderboard")

for i, (u, d) in enumerate(sorted_users, 1):
    st.write(f"{i}. {u} — {d['points']} pts")
