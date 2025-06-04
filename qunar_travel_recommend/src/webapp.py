import streamlit as st
from recommender import TravelRecommender

st.title("去哪儿游记智能推荐🦄")

rec = TravelRecommender("data/qunar_travel.csv")

city_sel = st.text_input("目标城市（可为空，例如厦门，北京，上海...）：", "")
interests = st.text_input("你的兴趣（如美食、沙滩、古镇...）：", "")
theme = st.text_input("主题偏好（如亲子，度假，探险...）：", "")
people = st.text_input("出行人物（如情侣、家庭、朋友...）：", "")
budget = st.number_input("最高预算（元，0代表忽略）：", min_value=0, value=0)
top_n = st.slider("推荐条数", 1, 10, 5)

if st.button("推荐！"):
    recs = rec.recommend(
        interests=interests,
        theme=theme,
        people=people,
        city=city_sel,
        budget=(budget if budget > 0 else None),
        top_n=top_n
    )
    if not recs:
        st.info("未找到匹配结果，请尝试放宽条件。")
    for r in recs:
        st.markdown(f"### [{r['标题']}]({r['链接']})")
        st.write(f"主题: {r['主题']}，人物: {r['人物']}，预算: {r['费用']}，城市: {r['城市']}")
        st.write(f"推荐理由: {r['推荐理由']}")
        st.write("---")