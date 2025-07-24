
# DiversiTrack Game with Sound, Animation, and Leaderboard Support
# Placeholders included for:
# - Playing sound effects (requires st.audio)
# - Showing animations (spinner + GIFs)
# - Leaderboard logic (CSV for now)

import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import base64
from pathlib import Path

st.set_page_config(page_title="DiversiTrack: The Journey", layout="wide")

st.title("🚆 DiversiTrack: The Journey to Financial Freedom")
st.markdown("A 10-round investment game simulating real-world events. Allocate smartly, diversify, and win!")

# --- Asset Setup ---
TOTAL_ROUNDS = 10
asset_classes = ["Equity", "Debt", "Gold", "Real Estate", "International"]
event_pool = [
    ("COVID-19 Pandemic Crash", {"Equity": -0.25, "Debt": 0.03, "Gold": 0.08, "Real Estate": -0.15, "International": -0.20}),
    ("Global Tech Rally", {"Equity": 0.20, "Debt": -0.01, "Gold": -0.02, "Real Estate": 0.12, "International": 0.25}),
    ("US Fed Rate Hike", {"Equity": -0.08, "Debt": -0.04, "Gold": 0.05, "Real Estate": -0.06, "International": -0.05}),
    ("Geopolitical Tension in Asia", {"Equity": -0.10, "Debt": 0.01, "Gold": 0.06, "Real Estate": -0.08, "International": -0.12}),
    ("Infrastructure Boom", {"Equity": 0.15, "Debt": 0.02, "Gold": -0.01, "Real Estate": 0.20, "International": 0.05}),
    ("Oil Price Shock", {"Equity": -0.12, "Debt": -0.01, "Gold": 0.07, "Real Estate": -0.10, "International": -0.08}),
    ("Green Energy Revolution", {"Equity": 0.18, "Debt": 0.00, "Gold": 0.02, "Real Estate": 0.14, "International": 0.10}),
    ("SIP Magic", {"Equity": 0.10, "Debt": 0.05, "Gold": 0.07, "Real Estate": 0.06, "International": 0.08}),
    ("Recession Scare", {"Equity": -0.20, "Debt": 0.04, "Gold": 0.10, "Real Estate": -0.15, "International": -0.18}),
    ("Budget Boost to Infra", {"Equity": 0.16, "Debt": 0.01, "Gold": -0.01, "Real Estate": 0.18, "International": 0.05}),
]

# --- State Init ---
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.history = []
    st.session_state.portfolio = {a: 200000 for a in asset_classes}
    st.session_state.sip = 10000
    st.session_state.totals = []
    st.session_state.submitted = False
    st.session_state.last_event = None
    st.session_state.name = ""

# --- Leaderboard Setup ---
leaderboard_file = "leaderboard.csv"
if Path(leaderboard_file).exists():
    leaderboard = pd.read_csv(leaderboard_file)
else:
    leaderboard = pd.DataFrame(columns=["Name", "Score"])

# --- Name Input for Leaderboard ---
if st.session_state.round == 1:
    st.session_state.name = st.text_input("Enter your name to track your score:", "")

# --- Allocation UI ---
st.subheader(f"Round {st.session_state.round} — Allocate Your Portfolio")
allocation = {}
total_value = sum(st.session_state.portfolio.values())
active_assets = []

for asset in asset_classes:
    val = st.number_input(f"{asset} (₹)", min_value=0, max_value=int(total_value), value=int(st.session_state.portfolio[asset]), step=10000, key=f"alloc_{asset}")
    allocation[asset] = val
    if val > 0:
        active_assets.append(asset)

# --- Submission Logic ---
if st.button("🚀 Submit Allocation and Reveal Event"):
    current_event = event_pool[st.session_state.round - 1]
    event_name, returns = current_event
    st.session_state.last_event = current_event

    # 🌀 Animation spinner
    
    with st.spinner("Revealing the event..."):
        st.audio("drumroll.mp3", format="audio/mp3", start_time=0)

        time.sleep(2)

    # 🔊 Sound (can be enabled with st.audio in hosted environment)
    
    st.success(f"📢 Round {st.session_state.round} Event: {event_name}")
    if any(r > 0 for r in returns.values()):
        st.audio("ding.mp3", format="audio/mp3", start_time=0)
    else:
        st.audio("buzz.mp3", format="audio/mp3", start_time=0)

    st.write("Market Impact:")
    st.dataframe(pd.DataFrame.from_dict(returns, orient="index", columns=["Return"]).style.format("{:.0%}"))

    updated_portfolio = {}
    active_total = sum(allocation[a] for a in active_assets)

    for asset in asset_classes:
        ret = returns.get(asset, 0)
        sip_share = (allocation[asset] / active_total) if asset in active_assets else 0
        sip_amt = st.session_state.sip * sip_share
        updated_val = allocation[asset] * (1 + ret) + sip_amt
        updated_portfolio[asset] = updated_val

    
    # Show table of old value, return, sip, new value
    breakdown_data = []
    for asset in asset_classes:
        old_val = allocation[asset]
        ret = returns.get(asset, 0)
        sip_share = (allocation[asset] / active_total) if asset in active_assets else 0
        sip_amt = st.session_state.sip * sip_share
        new_val = updated_portfolio[asset]
        breakdown_data.append({
            "Asset": asset,
            "Old Value": int(old_val),
            "Return %": f"{ret*100:.1f}%",
            "SIP Applied": int(sip_amt),
            "New Value": int(new_val)
        })

    st.subheader("📊 Portfolio Update After Event")
    st.dataframe(pd.DataFrame(breakdown_data))

    st.session_state.portfolio = updated_portfolio

    st.session_state.totals.append(sum(updated_portfolio.values()))
    st.session_state.history.append((event_name, updated_portfolio.copy()))
    st.session_state.submitted = True

# --- Next Round Trigger ---
if st.session_state.submitted:
    if st.button("➡️ Proceed to Next Round"):
        st.session_state.round += 1
        st.session_state.submitted = False
        st.rerun()

# --- Final Round ---
if st.session_state.round > TOTAL_ROUNDS:
    st.header("🎉 Game Over")
    st.subheader(f"Final Portfolio of {st.session_state.name}")
    final_df = pd.DataFrame([v for _, v in st.session_state.history], index=[f"Round {i+1}" for i in range(TOTAL_ROUNDS)])
    st.line_chart(final_df)

    total_val = sum(st.session_state.portfolio.values())
    std_dev = np.std(st.session_state.totals)
    penalty = std_dev * 0.1
    bonus = 20000 if sum(1 for v in st.session_state.portfolio.values() if v > 0) >= 4 else 0
    score = total_val - penalty + bonus

    st.metric("Final Score", f"₹{int(score):,}")
    st.metric("Diversification Bonus", f"₹{bonus:,}")
    st.metric("Volatility Penalty", f"₹{int(penalty):,}")

    if st.session_state.name:
        leaderboard = leaderboard.append({"Name": st.session_state.name, "Score": int(score)}, ignore_index=True)
        leaderboard.sort_values("Score", ascending=False, inplace=True)
        leaderboard.to_csv(leaderboard_file, index=False)

    st.subheader("🏆 Leaderboard")
    st.dataframe(leaderboard.head(10))

    st.stop()
