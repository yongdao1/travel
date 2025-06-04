import pandas as pd

def show_recommendation_table(recommend_df, save_html=True, show_topn=5):
    try:
        from pyecharts.components import Table
        from pyecharts.options import ComponentTitleOpts
        headers = ["目的地", "标题", "费用(元)", "天数", "玩法", "攻略链接"]
        usecols = []
        for col in ["目的地", "标题", "人均费用", "旅行时长", "玩法", "链接"]:
            if col in recommend_df.columns:
                usecols.append(col)
        rows = recommend_df[usecols].head(show_topn).values.tolist()
        table = Table()
        table.add(headers[:len(usecols)], rows)
        table.set_global_opts(title_opts=ComponentTitleOpts(title="个性化推荐旅游攻略TOP5"))
        if save_html:
            table.render("../data/recommendation.html")
            print("推荐已保存到 ../data/recommendation.html")
    except Exception as e:
        print(f"[美化失败] 用pandas展示：\n{e}")
        print(recommend_df.head(show_topn))

if __name__ == "__main__":
    df = pd.read_csv("../data/featured_travel.csv")
    show_recommendation_table(df, save_html=False, show_topn=5)