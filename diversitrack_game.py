
import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# --- Setup ---
st.set_page_config("DiversiTrack", layout="wide")
st.title("🚂 DiversiTrack: The Journey to Financial Freedom")

# --- Initialize session state ---
if "round" not in st.session_state:
    st.session_state.round = 1
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "Equity": 200000,
        "Debt": 200000,
        "Gold": 200000,
        "Real Estate": 200000,
        "International": 200000
    }
if "history" not in st.session_state:
    st.session_state.history = []

# --- Inputs ---
col1, col2 = st.sidebar.columns(1)
num_rounds = st.sidebar.number_input("🎯 Choose number of rounds", 1, 10, 3, key="num_rounds")
sip_amount = st.sidebar.number_input("💸 SIP Amount (annual)", 0, 500000, 120000, step=12000, key="sip")

# --- Simulate Event (hidden until allocation submitted) ---
def get_event():
    events = [
        ("Oil Price Crash", {"Equity": 6, "Debt": 2, "Gold": -5, "Real Estate": 4, "International": -2}),
        ("Geopolitical Tensions", {"Equity": -8, "Debt": 5, "Gold": 6, "Real Estate": -3, "International": -7}),
        ("Tech Boom", {"Equity": 14, "Debt": 2, "Gold": 1, "Real Estate": 5, "International": 10}),
        ("Interest Rate Hike", {"Equity": -5, "Debt": -2, "Gold": 4, "Real Estate": -6, "International": -4}),
        ("Festive Consumption Surge", {"Equity": 10, "Debt": 3, "Gold": 2, "Real Estate": 6, "International": 4}),
        ("SIP Magic", {"Equity": 4, "Debt": 2, "Gold": 1, "Real Estate": 3, "International": 3}),
    ]
    return random.choice(events)

# --- Asset Allocation ---
st.subheader(f"📊 Round {st.session_state.round}: Enter Your Asset Allocation")

prev_total = sum(st.session_state.portfolio.values())
st.info(f"Allocate your portfolio worth ₹{int(prev_total):,}")

alloc = {}
for asset in st.session_state.portfolio:
    alloc[asset] = st.number_input(asset, min_value=0, value=int(st.session_state.portfolio[asset] // 1), step=1000)

# Validate total allocation
alloc_total = sum(alloc.values())
if alloc_total != int(prev_total):
    st.warning(f"Total allocation must be ₹{int(prev_total):,} to proceed.")
    st.stop()

# Submit button
if st.button("Submit Allocation"):
    # Trigger round event
    event_name, returns = get_event()
    st.success(f"📢 Round {st.session_state.round} Event: {event_name}")
    time.sleep(1)

    # Apply SIP proportionally
    sip_distribution = {}
    for asset in alloc:
        if alloc_total > 0:
            sip_distribution[asset] = (alloc[asset] / alloc_total) * sip_amount
        else:
            sip_distribution[asset] = 0

    new_portfolio = {}
    round_data = []
    for asset in alloc:
        applied_sip = sip_distribution[asset]
        ret_pct = returns.get(asset, 0)
        old = alloc[asset]
        new = (old + applied_sip) * (1 + ret_pct / 100)
        new_portfolio[asset] = round(new)
        round_data.append({
            "Asset": asset,
            "Old Value": int(old),
            "Event Return %": ret_pct,
            "SIP Applied": int(applied_sip),
            "New Value": int(new)
        })

    st.session_state.history.append(round_data)
    st.session_state.portfolio = new_portfolio

    df = pd.DataFrame(round_data)
    st.markdown("### Round Summary")
    st.dataframe(df, use_container_width=True)

    # Show next round button
    if st.session_state.round < num_rounds:
        if st.button("➡️ Go to Next Round"):
            st.session_state.round += 1
            st.experimental_rerun()
    else:
        st.markdown("🎉 Game Over! You've completed all rounds.")
        total_value = sum(st.session_state.portfolio.values())
        st.metric("💰 Final Portfolio Value", f"₹{int(total_value):,}")
