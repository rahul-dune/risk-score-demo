import random
import streamlit as st
import pandas as pd
import plotly.express as px
from risk_calculation import calculate_risk_scores, add_user

st.title("🚀 Dynamic Risk Score Tracker 📊")

threads = {"IAM": 0.2, "DLP": 0.2, "EDR": 0.2, "Phishing": 0.4}
events = {"Critical": 0.5, "High": 0.25, "Medium": 0.15, "Low": 0.1}


def initialize_session_state():
    if "users" not in st.session_state:
        st.session_state["users"] = ["User1", "User2", "User3"]
    if "risk_scores" not in st.session_state:
        st.session_state["risk_scores"] = None
    if "total_percentages" not in st.session_state:
        st.session_state["total_percentages"] = None
    if "risk_history" not in st.session_state:
        st.session_state["risk_history"] = {user: []
                                            for user in st.session_state["users"]}
    for user in st.session_state["users"]:
        for thread in threads.keys():
            for event in events.keys():
                key = f"{user}_{thread}_{event}"
                if key not in st.session_state:
                    st.session_state[key] = 0


def reset_user_values(user):
    for thread in threads.keys():
        for event in events.keys():
            st.session_state[f"{user}_{thread}_{event}"] = 0


def calculate_and_store_results():
    users = {
        user: {
            thread: {
                event: st.session_state[f"{user}_{thread}_{event}"] for event in events.keys()}
            for thread in threads.keys()
        }
        for user in st.session_state["users"]
    }

    user_risk_scores, user_total_percentages, user_thread_percentages = calculate_risk_scores(
        users, threads, events)

    st.session_state["risk_scores"] = user_risk_scores
    st.session_state["total_percentages"] = user_total_percentages
    # ✅ NEW FIX
    st.session_state["thread_percentages"] = user_thread_percentages

    for user, score in user_risk_scores.items():
        st.session_state["risk_history"][user].append(score)


def add_new_user():
    new_user = st.text_input("👤 Enter new user name:", key="new_user_name")
    if st.button("➕ Add User") and new_user:
        if new_user not in st.session_state["users"]:
            st.session_state["users"].append(new_user)
            st.session_state["risk_history"][new_user] = []
            for thread in threads.keys():
                for event in events.keys():
                    key = f"{new_user}_{thread}_{event}"
                    if key not in st.session_state:
                        st.session_state[key] = 0
        st.rerun()


def randomize_values():
    for user in st.session_state["users"]:
        for thread in threads.keys():
            for event in events.keys():
                key = f"{user}_{thread}_{event}"
                st.session_state[key] = random.randint(0, 10)
    st.rerun()


initialize_session_state()
add_new_user()
if st.button("🎲 Randomize All Values"):
    randomize_values()
users = {}
for user in st.session_state["users"]:
    users[user] = {}
    st.subheader(f"👤 {user}")
    for thread in threads.keys():
        users[user][thread] = {}
        with st.expander(f"🔍 {user} - {thread}"):
            for event in events.keys():
                key = f"{user}_{thread}_{event}"
                users[user][thread][event] = st.slider(
                    f"⚡ {thread} - {event}", 0, 10, st.session_state[key], key=key)
    st.button(f"🔄 Reset {user}", key=f"reset_{user}",
              on_click=reset_user_values, args=(user,))

if st.button("📊 Calculate Risk Scores"):
    calculate_and_store_results()


if st.session_state["risk_scores"] and st.session_state["total_percentages"]:
    st.subheader("📌 User Risk Scores")
    for user, score in st.session_state["risk_scores"].items():
        history = st.session_state["risk_history"][user]
        if len(history) > 1:
            prev_score = history[-2]  # Second last score
            change = score - prev_score
            arrow = " 🔺🚨" if change > 0 else " 🔻✅ " if change < 0 else ""
            change_text = f" ({change:+.2f})" if change != 0 else ""
        else:
            arrow = ""
            change_text = ""

        st.write(f"{user}: {score:.2f}{arrow}{change_text} ")

    st.subheader("📌 User Total Percentages")
    for user, percentage in st.session_state["total_percentages"].items():
        st.write(f"{user}: {percentage:.2f}% 🎯")
    st.subheader("📈 Risk Score Over Time")
    history_data = []
    for user, scores in st.session_state["risk_history"].items():
        for i, score in enumerate(scores):
            history_data.append(
                {"User": user, "Time": i + 1, "Risk Score": score})
    if history_data:
        df = pd.DataFrame(history_data)
        fig = px.line(df, x="Time", y="Risk Score", color="User",
                      markers=True, title="📊 Risk Score Progression")
        st.plotly_chart(fig)

    st.subheader("📊 Risk Contribution Per Thread")
    for user in st.session_state["users"]:
        if "thread_percentages" in st.session_state and user in st.session_state["thread_percentages"]:
            thread_percentages = st.session_state["thread_percentages"][user]
            thread_data = [{"Thread": thread, "Percentage": percentage}
                           for thread, percentage in thread_percentages.items()]
            df_pie = pd.DataFrame(thread_data)
            fig_pie = px.pie(df_pie, names="Thread", values="Percentage",
                             title=f"📌 {user}'s Risk Distribution")
            st.plotly_chart(fig_pie)
