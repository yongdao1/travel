import pandas as pd
import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud

# ----------- 全局中文支持设置，绝对路径 -----------
# Windows 下用微软雅黑
CHINESE_FONT = 'C:/Windows/Fonts/msyh.ttc'
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# ----------- 数据载入（兼容tab/逗号分隔和 BOM） -----------
def load_df(path="data/featured_travel.csv"):
    with open(path, 'r', encoding='utf-8') as f:
        header = f.readline()
    sep = '\t' if '\t' in header else ','
    df = pd.read_csv(path, sep=sep, encoding='utf-8')
    col_names = [c.replace('\ufeff', '') for c in df.columns]
    df.columns = col_names
    return df

# -- 加载数据
df = load_df()

# -- 推荐系统建模预处理
def preprocess(row):
    fields = []
    for k in ['标题', '人物', '主题']:
        val = row.get(k)
        if pd.notnull(val):
            val_str = str(val).strip()
            if val_str and val_str != '无':
                fields.append(val_str)
    return " ".join(fields)
df['内容'] = df.apply(preprocess, axis=1)
df = df[df['内容'].str.strip() != '']

# -- 分词向量化
def chinese_tokenizer(text):
    try:
        return list(jieba.cut(str(text)))
    except:
        return []
vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer, max_features=500)
X = vectorizer.fit_transform(df['内容'])

# ===================== Streamlit 前端 =====================
st.set_page_config(page_title="去哪儿游记推荐与数据洞察", layout="wide")
st.title("去哪儿游记智能推荐与数据可视化平台")

tab1, tab2 = st.tabs(['🌟 智能推荐', '📊 数据分析'])

# ========== Tab1：智能推荐 ==========
with tab1:
    st.header("🌟 个性化游记推荐")
    user_interest = st.text_input("请输入你的旅游兴趣（如：美食、沙滩、亲子）", value="美食")
    budget = st.text_input("最大预算（单位元，可留空）", "")
    def get_recommend_reason(user_interest, content):
        keywords = set(chinese_tokenizer(user_interest))
        docwords = set(chinese_tokenizer(content))
        hit = keywords & docwords
        if hit:
            return f"匹配兴趣词：{'、'.join(hit)}"
        else:
            return "为您推荐热门游记"
    def recommend(user_interest, top_n=5, budget=-1):
        user_interest = user_interest.strip()
        if not user_interest:
            return []
        user_vec = vectorizer.transform([user_interest])
        df_ = df.copy()
        if budget > 0:
            df_['费用'] = pd.to_numeric(df_['费用'], errors='coerce')
            df_ = df_[df_['费用'].notnull() & (df_['费用'] <= budget)]
            if df_.empty:
                return []
            X_ = vectorizer.transform(df_['内容'])
        else:
            X_ = X
        if X_.shape[0] == 0:
            return []
        sims = cosine_similarity(user_vec, X_)[0]
        idx = sims.argsort()[::-1][:top_n]
        results = []
        for i in idx:
            row = df_.iloc[df_.index[i]]
            results.append({
                '标题': row.get('标题', ''),
                '人物': row.get('人物', ''),
                '主题': row.get('主题', ''),
                '费用': row.get('费用', ''),
                '浏览': row.get('浏览', ''),
                '点赞': row.get('点赞', ''),
                '链接': row.get('链接', ''),
                '推荐理由': get_recommend_reason(user_interest, row.get('内容',''))
            })
        return results

    if st.button("我要推荐"):
        try:
            budget_num = float(budget) if budget.strip() else -1
        except:
            budget_num = -1
        recs = recommend(user_interest, top_n=5, budget=budget_num)
        if not recs:
            st.warning("未找到符合条件的游记！")
        else:
            for i, rec in enumerate(recs, 1):
                st.markdown(f"**{i}. [{rec['标题']}]({rec['链接'] if pd.notnull(rec['链接']) else '#'})**")
                st.markdown(
                    f"- 人物: {rec['人物']}  \n"
                    f"- 主题: {rec['主题']}  \n"
                    f"- 费用: {rec['费用']}  \n"
                    f"- 推荐理由: {rec['推荐理由']}  \n"
                )
                st.markdown("---")
    else:
        st.info("请填写兴趣词与预算后，点击推荐按钮。")

# ========== Tab2：数据可视化分析 ==========
with tab2:
    st.header("📊 真实游记数据分析洞察")

    # 1. 热门目的地Top10及人均费用（柱状图）
    st.subheader("1. 热门目的地Top10与人均费用")
    # 这里用标题字段简单提取目的地（可根据你实际情况微调提取正则）
    df['目的地'] = df['标题'].str.extract(r'([\u4e00-\u9fa5]{2,8})[游行]', expand=False)
    top_dest = df['目的地'].value_counts().head(10).index.tolist()
    top_dest_df = df[df['目的地'].isin(top_dest)]
    avg_fee = top_dest_df.groupby('目的地')['费用'].mean()
    fig1, ax1 = plt.subplots(figsize=(10,4))
    ax1.bar(top_dest, avg_fee.loc[top_dest], color=sns.color_palette("Blues_r", n_colors=10))
    ax1.set_ylabel('人均费用（元）')
    ax1.set_xlabel('热门目的地')
    ax1.set_title('Top10 热门目的地及平均人均费用')
    mean_fee = avg_fee.mean()
    min_fee, max_fee = avg_fee.min(), avg_fee.max()
    ax1.axhline(mean_fee, color='red', linestyle='--', label='均值')
    ax1.axhline(min_fee, color='green', linestyle=':', label='最小值')
    ax1.axhline(max_fee, color='blue', linestyle=':', label='最大值')
    for spine in ['top','right']:
        ax1.spines[spine].set_visible(False)
    ax1.legend()
    st.pyplot(fig1)

    # 2. 出游结伴方式（饼图）
    st.subheader("2. 出游结伴方式分析")
    if '人物' in df.columns:
        partner_count = df['人物'].value_counts().head(10)
        fig2, ax2 = plt.subplots()
        colors = sns.color_palette('Pastel1', n_colors=partner_count.size)
        patches, texts, autotexts = ax2.pie(partner_count, labels=partner_count.index, autopct='%1.1f%%',
                                            startangle=140, colors=colors, textprops={'fontsize':12})
        ax2.set_title('出游结伴方式')
        st.pyplot(fig2)
    else:
        st.info('未找到人物字段，无法展示结伴方式。')

    # 3. 出游时间（折线图）
    st.subheader("3. 不同时间段出游情况")
    date_col = None
    for col in ['出发日期','时间','日期','年份','出']:
        if col in df.columns:
            date_col = col
            break
    if date_col is not None:
        df['year'] = df[date_col].astype(str).str.extract(r'(20\d{2})')
        df_years = df['year'].value_counts().sort_index()
        fig3, ax3 = plt.subplots()
        sns.lineplot(x=df_years.index, y=df_years.values, marker='o', ax=ax3)
        ax3.set_xlabel("年份")
        ax3.set_ylabel("数量")
        ax3.set_title("各年份出游数量变化趋势")
        st.pyplot(fig3)
    else:
        st.info('未找到日期相关字段，无法展示出游时间分布')

    # 4. 出游主题、旅行时长分布（条形图）
    st.subheader("4. 出游玩法/旅行时长分布")
    play_col = None
    for c in ['主题','玩法','方式']:
        if c in df.columns:
            play_col = c
            break
    dur_col = None
    for c in ['天数','旅行时长','行程天数']:
        if c in df.columns:
            dur_col = c
            break
    fig4, ax4 = plt.subplots(1,2,figsize=(14,4))
    if play_col:
        play_top = df[play_col].value_counts().head(10)
        sns.barplot(y=play_top.index, x=play_top.values, ax=ax4[0], palette='coolwarm')
        ax4[0].set_title('热门出游主题Top10')
        ax4[0].set_xlabel('数量')
    else:
        ax4[0].set_visible(False)
    if dur_col:
        dur_top = df[dur_col].value_counts().sort_index()
        sns.barplot(y=dur_top.index.astype(str), x=dur_top.values, ax=ax4[1], palette='mako')
        ax4[1].set_title('不同旅行时长分布')
        ax4[1].set_xlabel('数量')
    else:
        ax4[1].set_visible(False)
    st.pyplot(fig4)

    # 5. 词云
    st.subheader("5. 高频词词云")
    if '内容' in df.columns:
        texts = ' '.join(df['内容'].astype(str).tolist())
        seg_list = jieba.cut(texts)
        words = [w for w in seg_list if len(w) > 1]
        text_join = ' '.join(words)
        wc = WordCloud(
            font_path=CHINESE_FONT,
            background_color='white', width=800, height=400,
            max_words=120, contour_width=1, contour_color='steelblue'
        ).generate(text_join)
        fig5, ax5 = plt.subplots(figsize=(8,4))
        ax5.imshow(wc, interpolation='bilinear')
        ax5.axis('off')
        ax5.set_title('短评/内容 关键词词云')
        st.pyplot(fig5)
    else:
        st.info('数据中未找到“内容”字段，无法绘制词云')

    st.markdown("""
    **如何为“选择困难症”用户提供推荐？**

    - 热门目的地与人均费用，帮你迅速锁定高性价比旅行地  
    - 出游结伴分析，找适合你的模式（亲子/情侣/独行等）  
    - 时间分布，合理避峰  
    - 主题/天数分布，匹配你的兴趣与假期长度  
    - 词云总结高频体验与热点

    *你可在此分析辅助下，切换到“智能推荐”页获得个性化Top5游记推荐！*
    """)