import pandas as pd

def clean_data(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # 去掉含“攻略”的标题
    if "标题" in df.columns:
        df = df[~df["标题"].str.contains("攻略", na=False)]
    # 天数限制
    if "天数" in df.columns:
        df["天数"] = df["天数"].replace("99+", 99)
        df["天数"] = pd.to_numeric(df["天数"], errors='coerce')
        df = df[df["天数"] <= 15]
    # 费用字段清洗
    for money_col in ["人均费用", "费用"]:
        if money_col in df.columns:
            df[money_col] = pd.to_numeric(df[money_col], errors='coerce').fillna(0)
    # 人数补齐
    if "人数" in df.columns:
        df["人数"] = df["人数"].fillna("独自一人")
    elif "人物" in df.columns:
        df["人物"] = df["人物"].fillna("独自一人")
    # 玩法补齐
    if "玩法" in df.columns:
        df["玩法"] = df["玩法"].fillna("无")
    elif "主题" in df.columns:
        df["主题"] = df["主题"].fillna("无")
    # 出发日期不能为空
    date_col = None
    if "出发日期" in df.columns:
        date_col = "出发日期"
    elif "出发时间" in df.columns:
        date_col = "出发时间"
    if date_col:
        df = df.dropna(subset=[date_col])
    df = df.reset_index(drop=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[数据清洗] 保存到: {output_csv}")

if __name__ == "__main__":
    clean_data("../data/qunar_travel.csv", "../data/cleaned_travel.csv")