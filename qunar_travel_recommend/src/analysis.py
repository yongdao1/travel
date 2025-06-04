import pandas as pd

def add_features(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # 增加旅行月份
    date_col = "出发日期" if "出发日期" in df.columns else "出发时间" if "出发时间" in df.columns else None
    if date_col:
        df["旅行月份"] = pd.to_datetime(df[date_col], errors="coerce").dt.month
    # 浏览次数处理
    read_col = "阅读数" if "阅读数" in df.columns else "浏览" if "浏览" in df.columns else None
    if read_col:
        def parse_read(x):
            if pd.isna(x): return 0
            s = str(x).replace("+","").replace(",","")
            if "万" in s:
                return int(float(s.replace("万","")) * 10000)
            try:
                return int(float(s))
            except:
                return 0
        df["浏览次数"] = df[read_col].apply(parse_read)
    # 天数重命名
    if "天数" in df.columns:
        df.rename(columns={"天数": "旅行时长"}, inplace=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[分析+新特征] 保存到: {output_csv}")

if __name__ == "__main__":
    add_features("../data/cleaned_travel.csv", "../data/featured_travel.csv")