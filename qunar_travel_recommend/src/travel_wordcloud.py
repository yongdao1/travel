import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud(csv_path, font_path="msyh.ttc"):
    df = pd.read_csv(csv_path)
    # 自动组合标题+主题+行程
    text_columns = []
    for col in ["标题", "主题", "行程"]:
        if col in df.columns:
            text_columns.append(df[col].astype(str))
    if not text_columns:
        raise ValueError("没有可用的文本列！")
    texts = " ".join([" ".join(col) for col in text_columns])
    wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color='white').generate(texts)
    plt.figure(figsize=(12,6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    generate_wordcloud("../data/featured_travel.csv", font_path="msyh.ttc")