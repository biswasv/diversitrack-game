
# diversitrack_player.py
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import json
import random

# Load Firebase credentials
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_credentials.json")
    initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

st.title("🚂 DiversiTrack: Investment Game")

name = st.text_input("Enter your name:")
if not name:
    st.stop()

# Get current round
round_doc = db.collection("game_state").document("round_control").get()
current_round = round_doc.to_dict().get("round", 1)
st.subheader(f"🎯 Round {current_round}")

# Get previous data or initialize
player_ref = db.collection("players").document(name)
player_data = player_ref.get().to_dict() or {
    "portfolio": {
        "Equity": 200000,
        "Debt": 200000,
        "Gold": 200000,
        "Real Estate": 200000,
        "International": 200000,
    },
    "score": 0
}
portfolio = player_data["portfolio"]

st.markdown("### 💼 Your Asset Allocation")
total_value = sum(portfolio.values())
new_alloc = {}
for asset, val in portfolio.items():
    new_alloc[asset] = st.number_input(asset, min_value=0, value=val, step=10000)

if sum(new_alloc.values()) != total_value:
    st.error(f"Total allocation must be ₹{total_value:,}")
    st.stop()

if st.button("Submit Allocation"):
    # Simulate basic impact
    impact_factors = {
        "Equity": random.uniform(-0.1, 0.15),
        "Debt": random.uniform(-0.02, 0.05),
        "Gold": random.uniform(-0.05, 0.1),
        "Real Estate": random.uniform(-0.03, 0.08),
        "International": random.uniform(-0.08, 0.12),
    }

    for asset in new_alloc:
        new_alloc[asset] = round(new_alloc[asset] * (1 + impact_factors[asset]))

    score = sum(new_alloc.values())
    st.success(f"✅ Round complete! New Portfolio Value: ₹{score:,}")

    player_ref.set({
        "portfolio": new_alloc,
        "score": int(score),
        "round": current_round
    }, merge=True)
