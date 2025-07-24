
import streamlit as st
import pandas as pd
import numpy as np
import random
import time

st.set_page_config(page_title="DiversiTrack - The Journey", layout="wide")

st.title("🚆 DiversiTrack: The Journey to Financial Freedom")
st.markdown("A 10-round investment game simulating real-world economic events and asset class behavior.")

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

if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.history = []
    st.session_state.portfolio = {asset: 200000 for asset in asset_classes}
    st.session_state.sip = 0
    st.session_state.totals = []
    st.session_state.submitted = False
    st.session_state.last_event = None

if st.session_state.round == 1:
    st.session_state.sip = st.sidebar.number_input("💸 Monthly SIP (₹)", min_value=0, max_value=100000, step=1000, value=10000)

if st.session_state.round > 1 and not st.session_state.submitted:
    st.subheader(f"🔄 End of Round {st.session_state.round - 1} Summary")
    st.dataframe(pd.DataFrame([st.session_state.portfolio], index=["Your Portfolio"]).T.style.format("₹{:,.0f}"))

st.markdown(f"### 🧮 Allocate your funds for Round {st.session_state.round}")

allocation = {}
total_value = sum(st.session_state.portfolio.values())
col1, col2 = st.columns(2)

with col1:
    for asset in asset_classes[:3]:
        val = st.number_input(f"{asset} (₹)", min_value=0, max_value=int(total_value), value=int(st.session_state.portfolio[asset]), step=10000, key=f"alloc_{asset}")
        allocation[asset] = val

with col2:
    for asset in asset_classes[3:]:
        val = st.number_input(f"{asset} (₹)", min_value=0, max_value=int(total_value), value=int(st.session_state.portfolio[asset]), step=10000, key=f"alloc_{asset}")
        allocation[asset] = val

if st.button("🚀 Submit & Reveal Event"):
    updated_portfolio = {}
    active_assets = [a for a in asset_classes if allocation[a] > 0]
    active_total = sum(allocation[a] for a in active_assets)

    current_event = event_pool[st.session_state.round - 1]
    event_name, returns = current_event
    st.session_state.last_event = current_event

    with st.spinner("🔍 Revealing Event..."):
        time.sleep(2)

    st.markdown(f"### 📢 Event {st.session_state.round}: {event_name}")
    st.write("Impact on Assets:")
    event_impact_df = pd.DataFrame.from_dict(returns, orient="index", columns=["Return %"])
    st.dataframe(event_impact_df.style.format("{:.0%}"))

    for asset in asset_classes:
        ret = returns.get(asset, 0)
        sip_share = (allocation[asset] / active_total) if asset in active_assets and active_total > 0 else 0
        sip_amount = st.session_state.sip * sip_share
        updated_value = allocation[asset] * (1 + ret) + sip_amount
        updated_portfolio[asset] = updated_value

    st.session_state.portfolio = updated_portfolio
    st.session_state.history.append((event_name, updated_portfolio.copy()))
    total_now = sum(updated_portfolio.values())
    st.session_state.totals.append(total_now)
    st.session_state.round += 1
    st.session_state.submitted = True
    st.experimental_rerun()

if st.session_state.round > TOTAL_ROUNDS:
    st.header("🎉 Game Over — Your Financial Journey Summary")
    final_df = pd.DataFrame([p for _, p in st.session_state.history], index=[f"Round {i+1}" for i in range(TOTAL_ROUNDS)])
    st.line_chart(final_df)

    st.write("📊 Final Portfolio Value:")
    st.dataframe(pd.DataFrame(st.session_state.portfolio.items(), columns=["Asset Class", "Value"]).set_index("Asset Class").style.format("₹{:,.0f}"))

    total_final = sum(st.session_state.portfolio.values())
    std_dev = np.std(st.session_state.totals)
    penalty = std_dev * 0.1
    diversification_bonus = 20000 if sum(1 for v in st.session_state.portfolio.values() if v > 0) >= 4 else 0
    final_score = total_final - penalty + diversification_bonus

    st.markdown(f"🏁 **Final Score:** ₹{int(final_score):,}")
    st.markdown(f"📉 Volatility Penalty (Std Dev × 0.1): ₹{int(penalty):,}")
    st.markdown(f"🎁 Diversification Bonus: ₹{diversification_bonus:,}")
    st.stop()
else:
    st.session_state.submitted = False
