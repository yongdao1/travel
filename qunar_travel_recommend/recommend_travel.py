import pandas as pd
import jieba
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. 自动读取数据并适配列名/分隔符 ---
file_path = "data/featured_travel.csv"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"找不到文件: {file_path}")

# 先查分隔符和字段
with open(file_path, encoding="utf-8") as f:
    header = f.readline()
sep = "\t" if "\t" in header else ","

df = pd.read_csv(file_path, sep=sep, encoding="utf-8")
print("字段名:", df.columns.tolist())
print("数据行数:", df.shape[0])

# 处理首列BOM头
if '\ufeff标题' in df.columns:
    title_field = '\ufeff标题'
else:
    title_field = '标题'

# 检查所有内容
print(df.head(2).to_dict())

# --- 2. 合成内容特征字段 ---
def preprocess(row):
    fields = []
    # 兼容可能出现的'标题'和'\ufeff标题'
    for k in [title_field, '人物', '主题']:
        val = row.get(k)
        if pd.notnull(val):
            val_str = str(val).strip()
            if val_str:
                fields.append(val_str)
    return " ".join(fields)

df['内容'] = df.apply(preprocess, axis=1)
df = df[df['内容'].str.strip() != '']   # 去除内容为空的行

print("内容前5条:", df['内容'].head().tolist())

# --- 3. 中文分词 ---
def chinese_tokenizer(text):
    try:
        return list(jieba.cut(str(text)))
    except Exception as e:
        print("分词异常:", text, e)
        return []

content_list = df['内容'].tolist()

print("分词前5条:", [chinese_tokenizer(t) for t in content_list[:5]])

if not content_list:
    raise ValueError("没有任何可用内容行，请检查 featured_travel.csv 内容！")

# --- 4. TF-IDF向量化 ---
vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer, max_features=500)
X = vectorizer.fit_transform(content_list)

# --- 5. 推荐主体函数 ---
def recommend(user_interest, top_n=5, budget=-1):
    # 向量化用户输入
    user_vec = vectorizer.transform([user_interest])
    df_ = df.copy()
    if budget > 0 and "费用" in df_.columns:
        df_['费用'] = pd.to_numeric(df_['费用'], errors='coerce')
        df_ = df_.loc[df_['费用'] <= budget]
        if df_.empty:
            print("没有符合预算的游记！")
            return []
        X_ = vectorizer.transform(df_['内容'])
    else:
        X_ = X
    if X_.shape[0]==0:
        return []
    sims = cosine_similarity(user_vec, X_)[0]
    idx = sims.argsort()[::-1][:top_n]
    results = []
    df_reset = df_.reset_index(drop=True) if X_ is X else df_.reset_index(drop=True)
    for i in idx:
        if i>=df_.shape[0]:  # 异常保护
            continue
        row = df_.iloc[i]
        strategy = {
            '标题': row.get(title_field, ''),
            '人物': row.get('人物', ''),
            '主题': row.get('主题', ''),
            '费用': row.get('费用', ''),
            '浏览': row.get('浏览', ''),
            '点赞': row.get('点赞', ''),
            '链接': row.get('链接', ''),
            '推荐理由': get_recommend_reason(user_interest, row.get('内容', ''))
        }
        results.append(strategy)
    return results

def get_recommend_reason(user_interest, content):
    keywords = set(chinese_tokenizer(user_interest))
    docwords = set(chinese_tokenizer(content))
    hit = keywords & docwords
    if hit:
        return f"匹配兴趣词：{'、'.join(hit)}"
    else:
        return "为您推荐热门游记"

# --- DEMO ---
if __name__ == '__main__':
    print("请输入旅游兴趣关键词（如亲子、沙滩、美食）：")
    user_input = input()
    print("请输入最高预算（元，如无预算回车跳过）：")
    budget = input()
    try:
        budget = float(budget) if budget else -1
    except:
        budget = -1
    recs = recommend(user_input, top_n=5, budget=budget)
    print("\n【为你推荐游记】")
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec['标题']}（人物: {rec['人物']}, 主题: {rec['主题']}, 费用: {rec['费用']}） 浏览:{rec['浏览']}  点赞:{rec['点赞']}  链接: {rec['链接']}")
        print(f"  推荐理由: {rec['推荐理由']}")