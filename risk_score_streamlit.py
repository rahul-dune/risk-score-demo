import streamlit as st
import pandas as pd
import plotly.express as px


def calculate_risk_scores(users, threads, events):
    user_results = {}
    total_final_value = 0  # To store the sum of all final values

    for user, user_data in users.items():
        user_results[user] = {}
        for thread, thread_multiplier in threads.items():
            user_results[user][thread] = {}
            for event, event_multiplier in events.items():
                event_count = user_data[thread][event]
                multiplied_value = thread_multiplier * event_multiplier
                final_value = multiplied_value * event_count
                user_results[user][thread][event] = final_value
                total_final_value += final_value

    user_total_percentages = {}
    for user, thread_data in user_results.items():
        user_total_percentages[user] = sum(
            final_value / total_final_value * 100 if total_final_value > 0 else 0
            for thread, event_data in thread_data.items() for final_value in event_data.values()
        )

    initial_risk_score = 50
    user_risk_scores = {
        user: initial_risk_score * (1 + total_percentage / 100)
        for user, total_percentage in user_total_percentages.items()
    }

    return user_risk_scores, user_total_percentages


st.title("Dynamic Risk Score Tracker")

threads = {"IAM": 0.2, "DLP": 0.2, "EDR": 0.2, "Phishing": 0.4}
events = {"Critical": 0.5, "High": 0.25, "Medium": 0.15, "Low": 0.1}


def initialize_session_state():
    for user in ["User1", "User2", "User3"]:
        for thread in threads.keys():
            for event in events.keys():
                key = f"{user}_{thread}_{event}"
                if key not in st.session_state:
                    st.session_state[key] = 0

    if "risk_scores" not in st.session_state:
        st.session_state["risk_scores"] = None
    if "total_percentages" not in st.session_state:
        st.session_state["total_percentages"] = None
    if "risk_history" not in st.session_state:
        st.session_state["risk_history"] = {
            "User1": [], "User2": [], "User3": []}


def reset_user_values(user):
    for thread in threads.keys():
        for event in events.keys():
            st.session_state[f"{user}_{thread}_{event}"] = 0


def calculate_and_store_results():
    user_risk_scores, user_total_percentages = calculate_risk_scores(
        users, threads, events)
    st.session_state["risk_scores"] = user_risk_scores
    st.session_state["total_percentages"] = user_total_percentages

    # Store risk scores over time
    for user, score in user_risk_scores.items():
        st.session_state["risk_history"][user].append(score)


initialize_session_state()

users = {}
for user in ["User1", "User2", "User3"]:
    users[user] = {}
    st.subheader(user)
    for thread in threads.keys():
        users[user][thread] = {}
        with st.expander(f"{user} - {thread}"):
            for event in events.keys():
                key = f"{user}_{thread}_{event}"
                users[user][thread][event] = st.slider(
                    f"{thread} - {event}", 0, 10, st.session_state[key], key=key
                )

    st.button(f"Reset {user}", key=f"reset_{user}",
              on_click=reset_user_values, args=(user,))

if st.button("Calculate Risk Scores"):
    calculate_and_store_results()

if st.session_state["risk_scores"] and st.session_state["total_percentages"]:
    st.subheader("User Risk Scores")
    for user, score in st.session_state["risk_scores"].items():
        st.write(f"{user}: {score:.2f}")

    st.subheader("User Total Percentages")
    for user, percentage in st.session_state["total_percentages"].items():
        st.write(f"{user}: {percentage:.2f}%")

    # Plot risk scores over time
    st.subheader("Risk Score Over Time")
    history_data = []
    for user, scores in st.session_state["risk_history"].items():
        for i, score in enumerate(scores):
            history_data.append(
                {"User": user, "Time": i + 1, "Risk Score": score})

    if history_data:
        df = pd.DataFrame(history_data)
        fig = px.line(df, x="Time", y="Risk Score", color="User",
                      markers=True, title="Risk Score Progression")
        st.plotly_chart(fig)
