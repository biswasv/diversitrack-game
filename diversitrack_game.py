
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="DiversiTrack", layout="wide")

# Initialize session state
if "round" not in st.session_state:
    st.session_state.round = 1
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "Equity": 200000,
        "Debt": 200000,
        "Gold": 200000,
        "Real Estate": 200000,
        "International": 200000,
    }
if "sip" not in st.session_state:
    st.session_state.sip = 120000
if "num_rounds" not in st.session_state:
    st.session_state.num_rounds = 5
if "event_history" not in st.session_state:
    st.session_state.event_history = []

# Sidebar Inputs
st.sidebar.title("🎯 Game Setup")
st.session_state.num_rounds = st.sidebar.number_input("Number of Rounds", 1, 10, st.session_state.num_rounds)
st.session_state.sip = st.sidebar.number_input("Annual SIP Amount", 0, 500000, st.session_state.sip, step=12000)

st.title("🚂 DiversiTrack: Diversification Game")
st.header(f"Round {st.session_state.round}")

total_portfolio = sum(st.session_state.portfolio.values())
st.markdown(f"💼 **Total portfolio value:** ₹{int(total_portfolio):,}")

# Asset Allocation Input
allocation = {}
with st.form("allocation_form", clear_on_submit=False):
    st.subheader("📊 Enter Asset Allocation")
    for asset in st.session_state.portfolio.keys():
        allocation[asset] = st.number_input(asset, min_value=0, value=int(st.session_state.portfolio[asset]), step=10000, key=f"alloc_{asset}")
    submitted = st.form_submit_button("Submit Allocation")

# Process round if submitted
if submitted:
    alloc_total = sum(allocation.values())
    if alloc_total != total_portfolio:
        st.error(f"Total allocation must be ₹{int(total_portfolio):,}")
        st.stop()

    # Simulate an event
    events = [
        ("Tech Boom", {"Equity": 12, "Debt": 3, "Gold": 2, "Real Estate": 6, "International": 10}),
        ("Oil Price Crash", {"Equity": -6, "Debt": 4, "Gold": 5, "Real Estate": -2, "International": -4}),
        ("Interest Rate Hike", {"Equity": -5, "Debt": -2, "Gold": 4, "Real Estate": -3, "International": -3}),
        ("Festive Demand Surge", {"Equity": 7, "Debt": 2, "Gold": 3, "Real Estate": 5, "International": 6}),
        ("Geopolitical Risk", {"Equity": -10, "Debt": 5, "Gold": 8, "Real Estate": -4, "International": -8}),
        ("SIP Magic", {"Equity": 5, "Debt": 2, "Gold": 1, "Real Estate": 3, "International": 2}),
    ]
    event_name, returns = random.choice(events)
    st.session_state.event_history.append((event_name, returns))

    # Apply SIP proportionally
    sip_applied = {}
    for asset in allocation:
        sip_applied[asset] = (allocation[asset] / alloc_total) * st.session_state.sip if alloc_total > 0 else 0

    # Calculate new values
    new_portfolio = {}
    result_table = []
    for asset in allocation:
        old_val = allocation[asset]
        sip = sip_applied[asset]
        growth = (old_val + sip) * (1 + returns[asset] / 100)
        new_portfolio[asset] = int(growth)
        result_table.append({
            "Asset": asset,
            "Old Value": int(old_val),
            "Event Return %": returns[asset],
            "SIP Applied": int(sip),
            "New Value": int(growth)
        })

    df = pd.DataFrame(result_table)
    st.success(f"📢 Event: **{event_name}** — impact on your portfolio:")
    st.dataframe(df, use_container_width=True)

    st.session_state.portfolio = new_portfolio

    if st.session_state.round < st.session_state.num_rounds:
        if st.button("➡️ Go to Next Round"):
            st.session_state.round += 1
            st.experimental_rerun()
    else:
        st.balloons()
        st.success("🎉 Game Over!")
        st.metric("💰 Final Portfolio Value", f"₹{int(sum(st.session_state.portfolio.values())):,}")
