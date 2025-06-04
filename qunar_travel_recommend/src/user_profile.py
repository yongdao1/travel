def build_user_profile(name, preferences, budget, travel_days, travel_month, accompany):
    return {
        "name": name,
        "preferences": preferences,   # 关键词字符串, 如 "美食,古镇"
        "budget": budget,             # 预算数值
        "travel_days": travel_days,   # 旅行天数
        "travel_month": travel_month, # 旅行月份, 数字1-12
        "accompany": accompany        # 同行方式, 如 "家庭" "独自" "三五好友"
    }

if __name__ == "__main__":
    profile = build_user_profile("小明", "美食,古镇", 2000, 5, 5, "家庭")
    print(profile)