
import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go

st.set_page_config(page_title="DiversiTrack", layout="wide")
st.title("🚂 DiversiTrack: The Journey of Diversified Investing")

# Constants
ASSETS = ['Equity', 'Debt', 'Gold', 'Real Estate', 'International Funds']
YEARS = 10
START_CAPITAL = 1000000

EVENTS = [
    {
        'name': 'COVID-19 Pandemic Outbreak (2020)',
        'effects': {'Equity': -0.25, 'Gold': 0.10, 'Debt': 0.02}
    },
    {
        'name': 'Russia-Ukraine War Escalation (2022)',
        'effects': {'Equity': -0.10, 'Gold': 0.15, 'International Funds': -0.05}
    },
    {
        'name': 'US Fed Rate Hike Cycle (2022)',
        'effects': {'Debt': 0.08, 'Equity': -0.05, 'Real Estate': -0.10}
    },
    {
        'name': 'Budget 2025: Big Capex Push',
        'effects': {'Equity': 0.12, 'Real Estate': 0.10, 'Debt': -0.02}
    },
    {
        'name': 'Global Tech Boom (AI Disruption, 2024)',
        'effects': {'International Funds': 0.20, 'Equity': 0.15, 'Debt': -0.02}
    },
    {
        'name': 'Inflation Surge in India (2013-style)',
        'effects': {'Gold': 0.15, 'Equity': -0.12, 'Debt': 0.03}
    },
    {
        'name': 'Rupee Depreciation Against USD',
        'effects': {'International Funds': 0.10, 'Gold': 0.05, 'Equity': -0.03}
    },
    {
        'name': 'Credit Crisis & Bank Default Scare',
        'effects': {'Debt': -0.10, 'Gold': 0.08, 'Real Estate': -0.15}
    },
    {
        'name': 'Real Estate Regulatory Reform',
        'effects': {'Real Estate': 0.12, 'Equity': 0.03}
    },
    {
        'name': 'SIP Magic (Habit Power + Market Uptick)',
        'effects': {'SIP': 0.12}
    },
]

# Session state initialization
if 'round' not in st.session_state:
    st.session_state.round = 0
    st.session_state.portfolio = {a: START_CAPITAL // len(ASSETS) for a in ASSETS}
    st.session_state.sip = 0
    st.session_state.history = []
    st.session_state.values_over_time = [START_CAPITAL]
    st.session_state.sip_alloc = {a: 0 for a in ASSETS}

# User SIP Input (only at first round)
if st.session_state.round == 0:
    st.sidebar.subheader("📥 Enter Annual SIP Amount")
    sip_amount = st.sidebar.number_input("SIP per year (₹)", min_value=0, value=120000, step=10000)
    st.session_state.sip = sip_amount

# Asset Allocation
st.sidebar.subheader(f"🔄 Reallocate for Round {st.session_state.round + 1}")
new_alloc = {}
total_alloc = 0
for asset in ASSETS:
    val = st.sidebar.number_input(f"{asset} (₹)", min_value=0, value=int(st.session_state.portfolio[asset]), step=10000)
    new_alloc[asset] = val
    total_alloc += val

# Allocation check
if total_alloc > st.session_state.values_over_time[-1]:
    st.sidebar.error("🚫 Total allocation exceeds available capital.")
else:
    if st.sidebar.button("▶️ Play Round"):
        st.session_state.round += 1
        st.session_state.portfolio = new_alloc

        # Select and show event
        event = random.choice(EVENTS)
        st.subheader(f"📰 Round {st.session_state.round}: {event['name']}")
        st.markdown("### 🔎 Impact:")
        for asset, change in event['effects'].items():
            impact_pct = f"{change*100:+.1f}%"
            st.markdown(f"- {asset}: {impact_pct}")

        # Apply event effects
        portfolio = st.session_state.portfolio.copy()
        for asset in portfolio:
            change = event['effects'].get(asset, random.uniform(-0.05, 0.15))
            portfolio[asset] *= (1 + change)

        # Apply SIP Magic
        sip_boost = event['effects'].get('SIP', 0)
        sip_value = st.session_state.sip * (1 + sip_boost)

        # Distribute SIP as per new allocation
        sip_distribution = {}
        total_alloc_val = sum(new_alloc.values())
        for asset in ASSETS:
            proportion = new_alloc[asset] / total_alloc_val if total_alloc_val else 0
            sip_distribution[asset] = proportion * sip_value
            portfolio[asset] += sip_distribution[asset]

        # Update and record
        total = sum(portfolio.values())
        st.session_state.portfolio = portfolio
        st.session_state.values_over_time.append(total)

        st.session_state.history.append({
            "Round": st.session_state.round,
            **portfolio,
            "SIP Used": sip_value,
            "Event": event['name'],
            "Total": total
        })

# Display Score Table
if st.session_state.round > 0:
    df = pd.DataFrame(st.session_state.history)
    st.subheader("📊 Portfolio Summary After Each Round")
    st.dataframe(df.set_index("Round"))

    # Score calculation
    returns = [st.session_state.values_over_time[i+1] / st.session_state.values_over_time[i] - 1
               for i in range(st.session_state.round)]
    volatility = np.std(returns)
    total_return = st.session_state.values_over_time[-1] - START_CAPITAL
    diversification_bonus = 10000 if len([v for v in st.session_state.portfolio.values() if v > 0]) >= 4 else 0
    score = total_return - (volatility * 2 * START_CAPITAL) + diversification_bonus

    st.subheader("🏆 Current Score")
    st.markdown(f"**Portfolio Value:** ₹{st.session_state.values_over_time[-1]:,.0f}")
    st.markdown(f"**Total Return:** ₹{total_return:,.0f}")
    st.markdown(f"**Volatility Penalty:** ₹{volatility * 2 * START_CAPITAL:,.0f}")
    st.markdown(f"**Diversification Bonus:** ₹{diversification_bonus:,}")
    st.markdown(f"**Current Score:** ₹{score:,.0f}")

    if st.session_state.round == YEARS:
        st.success("🎉 Game Over! Final Portfolio Score Displayed Above.")
        st.balloons()

        # Plot portfolio over time
        st.subheader("📈 Portfolio Growth Over Time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=st.session_state.values_over_time,
            x=list(range(YEARS + 1)),
            mode='lines+markers',
            name='Total Value'
        ))
        fig.update_layout(title="Total Portfolio Value", xaxis_title="Round", yaxis_title="₹ Value")
        st.plotly_chart(fig, use_container_width=True)
