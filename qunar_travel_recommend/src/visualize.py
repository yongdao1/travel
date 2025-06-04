from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts

def show_recommendation_table(recommend_df):
    headers = ["目的地", "标题", "费用(元)", "天数", "玩法", "攻略链接"]
    rows = recommend_df[["目的地", "标题", "人均费用", "天数", "玩法", "链接"]].values.tolist()
    table = Table()
    table.add(headers, rows)
    table.set_global_opts(title_opts=ComponentTitleOpts(title="个性化推荐旅游攻略TOP5"))
    table.render("recommendation.html")