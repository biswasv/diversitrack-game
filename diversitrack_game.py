
import streamlit as st
import pandas as pd
import random
import time
import os

# --- Sidebar setup ---
st.set_page_config(page_title="DiversiTrack", layout="wide")

# Number of rounds selector
TOTAL_ROUNDS = st.sidebar.number_input("🎯 Choose number of rounds", min_value=1, max_value=20, value=10)

# Initial setup
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.history = []
    st.session_state.portfolio = {"Equity": 200000, "Debt": 200000, "Gold": 200000, "Real Estate": 200000, "International": 200000}
    st.session_state.sip = 100000
    st.session_state.name = ""
    st.session_state.scores = []
    st.session_state.game_over = False

# Events database
events = [
    {"name": "US Fed Rate Hike", "impact": {"Equity": -0.15, "Debt": 0.05, "Gold": 0.03, "Real Estate": -0.05, "International": -0.10}},
    {"name": "India Election Results – Stable Govt", "impact": {"Equity": 0.12, "Debt": 0.01, "Gold": -0.02, "Real Estate": 0.05, "International": 0.03}},
    {"name": "Recession in Europe", "impact": {"Equity": -0.10, "Debt": 0.06, "Gold": 0.04, "Real Estate": -0.08, "International": -0.12}},
    {"name": "Bull Market in US Tech", "impact": {"Equity": 0.08, "Debt": 0.01, "Gold": -0.01, "Real Estate": 0.03, "International": 0.12}},
    {"name": "Oil Price Crash", "impact": {"Equity": 0.06, "Debt": 0.02, "Gold": -0.05, "Real Estate": 0.04, "International": -0.02}},
    {"name": "Geopolitical Tensions", "impact": {"Equity": -0.12, "Debt": 0.04, "Gold": 0.08, "Real Estate": -0.06, "International": -0.05}},
    {"name": "SIP Magic", "impact": {"Equity": 0.15, "Debt": 0.15, "Gold": 0.15, "Real Estate": 0.15, "International": 0.15}},
    {"name": "China Manufacturing Boom", "impact": {"Equity": 0.05, "Debt": 0, "Gold": -0.02, "Real Estate": 0.03, "International": 0.10}},
    {"name": "RBI Unexpected Rate Cut", "impact": {"Equity": 0.07, "Debt": -0.03, "Gold": 0.01, "Real Estate": 0.05, "International": 0.02}},
    {"name": "Global Pandemic Fear", "impact": {"Equity": -0.20, "Debt": 0.10, "Gold": 0.12, "Real Estate": -0.15, "International": -0.18}}
]

st.title("🚂 DiversiTrack: The Journey to Financial Freedom")

if "name" not in st.session_state or st.session_state.name == "":
    st.subheader("🧑 Enter Player Name to Start")
    name_input = st.text_input("Enter your name:")
    if st.button("Start Game") and name_input.strip():
        st.session_state.name = name_input.strip()
        st.experimental_rerun()
    st.stop()

# Show current round and portfolio
st.subheader(f"Round {st.session_state.round} of {TOTAL_ROUNDS}")
st.markdown("### Current Portfolio Allocation")
st.write(pd.DataFrame(st.session_state.portfolio.items(), columns=["Asset", "Value"]))

# Asset Allocation Input
st.markdown("### Enter your asset allocation for this round (total should be ₹10,00,000)")
total_cap = 1000000
alloc = {}
cols = st.columns(5)
for i, asset in enumerate(st.session_state.portfolio):
    with cols[i]:
        default_val = int(st.session_state.portfolio[asset])
        val = st.number_input(asset, 0, total_cap, default_val, step=10000, key=f"alloc_{asset}")
        alloc[asset] = val

# SIP input
st.session_state.sip = st.sidebar.number_input("💸 SIP Amount (annual)", min_value=0, max_value=1000000, value=st.session_state.sip, step=10000)

if sum(alloc.values()) != 1000000:
    st.error("Total allocation must be ₹10,00,000 to proceed.")
    st.stop()

if st.button("Submit Allocation"):
    with st.spinner("Revealing the event..."):
        st.audio("drumroll.mp3", format="audio/mp3", start_time=0)
        time.sleep(2)

    event = random.choice(events)
    event_name = event["name"]
    returns = event["impact"]

    st.success(f"📢 Round {st.session_state.round} Event: {event_name}")
    if any(r > 0 for r in returns.values()):
        st.audio("ding.mp3", format="audio/mp3")
    else:
        st.audio("buzz.mp3", format="audio/mp3")

    # Apply returns and SIP
    old = {}
    new = {}
    for asset in alloc:
        old_val = alloc[asset]
        sip_val = st.session_state.sip * (old_val / 1000000)
        ret = returns[asset]
        new_val = (old_val + sip_val) * (1 + ret)
        old[asset] = old_val
        new[asset] = new_val

    st.session_state.portfolio = new
    st.session_state.history.append({
        "round": st.session_state.round,
        "event": event_name,
        "returns": returns,
        "old": old,
        "sip": st.session_state.sip,
        "new": new
    })

    # Show table
    df = pd.DataFrame({
        "Asset": list(new.keys()),
        "Old Value": [old[a] for a in new],
        "Event Return %": [returns[a]*100 for a in new],
        "SIP Applied": [st.session_state.sip * (old[a] / 1000000) for a in new],
        "New Value": [new[a] for a in new]
    })
    st.write("### Round Summary")
    st.dataframe(df)

    # Score calculation
    total = sum(new.values())
    volatility_penalty = (max(returns.values()) - min(returns.values())) * 100
    diversification_bonus = 200 if len([v for v in alloc.values() if v > 0]) >= 4 else 0
    score = total - volatility_penalty * 1000 + diversification_bonus
    st.session_state.scores.append(score)

    st.session_state.round += 1

# Show leaderboard and final score
if st.session_state.get("round", 1) > TOTAL_ROUNDS and not st.session_state.get("game_over", False):
    st.subheader("🏁 Game Over! Final Score")
    score = st.session_state.scores[-1]
    st.write(f"Name: {st.session_state.name}")
    st.write(f"Final Score: {score:.0f}")

    if os.path.exists("leaderboard.csv"):
        leaderboard = pd.read_csv("leaderboard.csv")
    else:
        leaderboard = pd.DataFrame(columns=["Name", "Score"])

    new_row = pd.DataFrame([{"Name": st.session_state.name, "Score": int(score)}])
    leaderboard = pd.concat([leaderboard, new_row], ignore_index=True)
    leaderboard.sort_values("Score", ascending=False, inplace=True)
    leaderboard.to_csv("leaderboard.csv", index=False)

    st.subheader("🏆 Leaderboard")
    st.dataframe(leaderboard.head(10))
    st.session_state.game_over = True
    st.stop()
