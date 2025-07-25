# DiversiTrack Game Script
# (truncated intro...)

# leaderboard logic fixed
if st.session_state.get("round", 1) > TOTAL_ROUNDS and not st.session_state.get("game_over", False):
    st.subheader("🏁 Game Over! Final Score")
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
