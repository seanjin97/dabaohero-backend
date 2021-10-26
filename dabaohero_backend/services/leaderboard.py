from dao import users


def leaderboard_top_10():
    all_users = users.get_all_users().items
    sorted_users = sorted(all_users, key=lambda d: (
        d["rating"] * d["completed_orders"]), reverse=True)
    return sorted_users[:10]
