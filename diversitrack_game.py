
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="DiversiTrack Game", layout="wide")

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
    st.session_state.num_rounds = 3
if "event" not in st.session_state:
    st.session_state.event = {}

# Sidebar Inputs
st.sidebar.markdown("🎯 **Choose number of rounds**")
st.session_state.num_rounds = st.sidebar.number_input("Rounds", min_value=1, max_value=10, value=st.session_state.num_rounds, step=1)

st.sidebar.markdown("💸 **SIP Amount (annual)**")
st.session_state.sip = st.sidebar.number_input("SIP", min_value=0, value=st.session_state.sip, step=10000)

st.title(f"Round {st.session_state.round} Asset Allocation")

total_portfolio = sum(st.session_state.portfolio.values())
st.markdown(f"💼 Total portfolio value from last round: ₹{int(total_portfolio):,}")

# Asset Allocation Input
allocation = {}
with st.form("allocation_form"):
    st.markdown("#### Enter your asset allocation for this round")
    total_input = 0
    for asset in st.session_state.portfolio.keys():
        val = st.number_input(f"{asset}", min_value=0, value=int(st.session_state.portfolio[asset]), step=10000)
        allocation[asset] = val
        total_input += val

    submitted = st.form_submit_button("Submit Allocation")

if submitted:
    if total_input != total_portfolio:
        st.error(f"⚠️ Allocation must total ₹{int(total_portfolio):,}")
    else:
        # Generate event returns randomly for each asset
        event_returns = {asset: random.randint(-10, 15) for asset in allocation}
        st.session_state.event = event_returns

        sip_amount = st.session_state.sip
        sip_allocation = {}
        for asset in allocation:
            proportion = allocation[asset] / total_input if total_input > 0 else 0
            sip_allocation[asset] = int(sip_amount * proportion)

        new_values = {}
        for asset in allocation:
            growth = allocation[asset] * (1 + event_returns[asset]/100)
            new_values[asset] = int(growth + sip_allocation[asset])

        df = pd.DataFrame({
            "Asset": list(allocation.keys()),
            "Old Value": list(allocation.values()),
            "Event Return %": list(event_returns.values()),
            "SIP Applied": list(sip_allocation.values()),
            "New Value": list(new_values.values())
        })

        st.success(f"📢 Round {st.session_state.round} Event Summary")
        st.dataframe(df, use_container_width=True)

        st.session_state.portfolio = new_values
        if st.session_state.round < st.session_state.num_rounds:
            if st.button("Next Round ➡️"):
                st.session_state.round += 1
                st.experimental_rerun()
        else:
            st.balloons()
            st.success("🎉 Game Over! You've completed all rounds.")
