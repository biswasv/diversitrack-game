
import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go

st.set_page_config(page_title="DiversiTrack", layout="wide")
st.title("🚂 DiversiTrack: Your Investment Journey")

# Constants
ASSETS = ['Equity', 'Debt', 'Gold', 'Real Estate', 'International Funds', 'SIP']
START_CAPITAL = 1000000
YEARS = 10

EVENTS = [
    {'name': 'Stock Market Crash', 'effects': {'Equity': -0.25}},
    {'name': 'Inflation Spike', 'effects': {'Gold': 0.15}},
    {'name': 'Rate Cut', 'effects': {'Debt': 0.10}},
    {'name': 'Recession', 'effects': {'Real Estate': -0.20, 'Equity': -0.10}},
    {'name': 'Tech Boom', 'effects': {'International Funds': 0.20}},
    {'name': 'SIP Magic', 'effects': {'SIP': 0.12}},
    {'name': 'Currency Depreciation', 'effects': {'International Funds': 0.10}},
]

# Sidebar: Allocation
st.sidebar.header("💸 Allocate ₹10 Lakhs")
allocations = {}
remaining = START_CAPITAL

for asset in ASSETS:
    if remaining <= 0:
        allocations[asset] = 0
        continue
    default_value = int(min(remaining, START_CAPITAL // len(ASSETS)))
    val = st.sidebar.slider(
        label=asset,
        min_value=0,
        max_value=int(remaining),
        value=default_value,
        step=10000
    )
    allocations[asset] = val
    remaining -= val

if remaining > 0:
    st.sidebar.markdown(f"**Unallocated:** ₹{remaining:,}")

# Toggle for upfront event visibility
show_events = st.sidebar.checkbox("Show all future events upfront", value=True)

# Generate all events at once
all_events = [random.choice(EVENTS) for _ in range(YEARS)]

if show_events:
    st.subheader("📋 Upcoming Economic Events")
    for i, event in enumerate(all_events, 1):
        st.markdown(f"**Year {i}**: {event['name']}")

# Simulate button
if st.sidebar.button("Start Simulation"):
    history = []
    portfolio = allocations.copy()
    portfolio_value = sum(portfolio.values())
    values_over_time = [portfolio_value]
    event_log = []

    for year in range(1, YEARS + 1):
        event = all_events[year - 1]
        event_log.append(event['name'])
        year_return = {}

        for asset, value in portfolio.items():
            change = event['effects'].get(asset, random.uniform(-0.05, 0.15))
            updated = value * (1 + change)
            portfolio[asset] = updated
            year_return[asset] = updated

        total = sum(portfolio.values())
        values_over_time.append(total)
        history.append({"Year": year, **year_return, "Total": total})

    df = pd.DataFrame(history)

    # Visuals
    st.subheader("📈 Portfolio Growth Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=values_over_time, x=list(range(YEARS + 1)), mode='lines+markers', name='Total Value'))
    fig.update_layout(title="Total Portfolio Value", xaxis_title="Year", yaxis_title="₹ Value", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Portfolio Summary Table")
    st.dataframe(df.set_index("Year"))

    st.subheader("⚠️ Economic Events Each Year")
    for i, e in enumerate(event_log):
        st.write(f"Year {i + 1}: {e}")

    # Score calculation
    returns = [values_over_time[i+1] / values_over_time[i] - 1 for i in range(YEARS)]
    volatility = np.std(returns)
    total_return = values_over_time[-1] - START_CAPITAL
    diversification_bonus = 10000 if len([v for v in allocations.values() if v > 0]) >= 4 else 0
    score = total_return - (volatility * 2 * START_CAPITAL) + diversification_bonus

    st.subheader("🏆 Final Score")
    st.markdown(f"**Final Portfolio Value:** ₹{values_over_time[-1]:,.0f}")
    st.markdown(f"**Total Return:** ₹{total_return:,.0f}")
    st.markdown(f"**Volatility Penalty:** ₹{volatility * 2 * START_CAPITAL:,.0f}")
    st.markdown(f"**Diversification Bonus:** ₹{diversification_bonus:,}")
    st.markdown(f"**Final Score:** ₹{score:,.0f}")

    # Medal
    st.subheader("🎖 Achievement")
    if diversification_bonus > 0:
        st.markdown("🥇 **Diversification Champion**")
    if total_return > 500000:
        st.markdown("🥈 **Return Sprinter**")
    if volatility < 0.05:
        st.markdown("🥉 **Risk Navigator**")
else:
    st.info("Set your asset allocation and click 'Start Simulation' from the sidebar to begin your journey!")
