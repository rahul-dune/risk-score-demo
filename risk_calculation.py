def calculate_risk_scores(users, threads, events):
    user_results = {}
    total_final_value = 0

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
    user_thread_percentages = {}  # NEW: Store per-thread contributions for each user

    for user, thread_data in user_results.items():
        user_total = sum(
            final_value for thread in thread_data.values() for final_value in thread.values()
        )

        user_total_percentages[user] = (
            (user_total / total_final_value * 100) if total_final_value > 0 else 0
        )

        # Compute per-thread percentage contributions
        thread_percentages = {
            thread: (sum(event_values.values()) /
                     user_total * 100) if user_total > 0 else 0
            for thread, event_values in thread_data.items()
        }
        user_thread_percentages[user] = thread_percentages

    initial_risk_score = 50
    user_risk_scores = {
        user: initial_risk_score * (1 + total_percentage / 100)
        for user, total_percentage in user_total_percentages.items()
    }

    return user_risk_scores, user_total_percentages, user_thread_percentages


def add_user(users, user_name, threads, events):
    if user_name not in users:
        users[user_name] = {thread: {event: 0 for event in events}
                            for thread in threads}
    return users
