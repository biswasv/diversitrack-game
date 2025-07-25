
# diversitrack_admin.py
import streamlit as st
from firebase_admin import credentials, firestore, initialize_app
import json

# Load Firebase credentials
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_credentials.json")
    initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

st.title("🎮 DiversiTrack Admin Panel")
st.markdown("Use this to control the round and monitor the leaderboard.")

# Control round
round_doc = db.collection("game_state").document("round_control")
event_doc = db.collection("game_state").document("event_list")

round_info = round_doc.get().to_dict() or {"round": 1}
current_round = round_info["round"]
st.subheader(f"📢 Current Round: {current_round}")

new_round = st.number_input("Set Round Number", min_value=1, value=current_round, step=1)
if st.button("Update Round"):
    round_doc.set({"round": int(new_round)})
    st.success(f"Round updated to {new_round}")

# Show leaderboard
st.subheader("🏆 Leaderboard")
players_ref = db.collection("players")
players = [(doc.id, doc.to_dict().get("score", 0)) for doc in players_ref.stream()]
sorted_players = sorted(players, key=lambda x: -x[1])

for i, (name, score) in enumerate(sorted_players, 1):
    st.write(f"{i}. **{name}** — Score: {score}")
