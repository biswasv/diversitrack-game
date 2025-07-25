
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
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = []
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# Game setup form
if not st.session_state.game_started:
    with st.form("setup_form"):
        st.title("🚂 Welcome to DiversiTrack")
        st.subheader("Set up your game:")
        name = st.text_input("Enter your name")
        num_rounds = st.number_input("Number of Rounds", 1, 10, 5)
        sip_amt = st.number_input("Annual SIP Amount", 0, 500000, 120000, step=12000)
        submitted = st.form_submit_button("Start Game")
        if submitted and name:
            st.session_state.player_name = name
            st.session_state.num_rounds = num_rounds
            st.session_state.sip = sip_amt
            st.session_state.game_started = True
            st.experimental_rerun()

elif st.session_state.round <= st.session_state.num_rounds:
    st.title(f"📈 DiversiTrack - Round {st.session_state.round} of {st.session_state.num_rounds}")
    total_portfolio = sum(st.session_state.portfolio.values())
    st.markdown(f"💼 **Total Portfolio Value:** ₹{int(total_portfolio):,}")

    allocation = {}
    with st.form("allocation_form"):
        st.subheader("🔀 Allocate your portfolio:")
        for asset in st.session_state.portfolio.keys():
            allocation[asset] = st.number_input(asset, min_value=0, value=int(st.session_state.portfolio[asset]), step=10000, key=f"alloc_{asset}_{st.session_state.round}")
        submitted = st.form_submit_button("Submit Allocation")

    if submitted:
        if sum(allocation.values()) != total_portfolio:
            st.error(f"Total must be ₹{int(total_portfolio):,}")
            st.stop()

        # Generate random event
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

        # Proportional SIP
        sip_applied = {a: (allocation[a] / total_portfolio) * st.session_state.sip for a in allocation}
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
        st.success(f"📢 Event: **{event_name}**")
        st.dataframe(df, use_container_width=True)

        st.session_state.portfolio = new_portfolio
        st.session_state.round += 1
        st.experimental_rerun()

else:
    st.balloons()
    final_value = sum(st.session_state.portfolio.values())
    st.success(f"🎉 Game Over, {st.session_state.player_name}!")
    st.metric("🏁 Final Portfolio Value", f"₹{int(final_value):,}")

    # Add to leaderboard
    st.session_state.leaderboard.append({"Name": st.session_state.player_name, "Value": int(final_value)})
    lb_df = pd.DataFrame(st.session_state.leaderboard).sort_values(by="Value", ascending=False).reset_index(drop=True)
    st.subheader("🏆 Leaderboard")
    st.dataframe(lb_df)

    if st.button("🔄 Play Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
