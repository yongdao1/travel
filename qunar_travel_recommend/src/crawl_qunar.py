import requests
from bs4 import BeautifulSoup
import pandas as pd
import time, re

def parse_num(s):
    """
    解析数字，如“3.4万”转成34000
    """
    if not s: return None
    s = s.replace(',','').replace(' ', '')
    if '万' in s:
        try:
            return int(float(s.replace('万', '')) * 10000)
        except:
            return 0
    try:
        return int(re.sub(r'\D', '', s))
    except:
        return 0

def crawl_qunar_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/123.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = "utf-8"
    if resp.status_code != 200:
        print("请求失败", url)
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    result = []
    ul = soup.find("ul", class_="b_strategy_list")
    if not ul:
        print("未找到攻略列表")
        return []
    for li in ul.find_all("li", class_="list_item"):
        # 标题
        title_tag = li.find("h2", class_="tit")
        title = title_tag.a.get_text(strip=True) if title_tag and title_tag.a else ""
        link = title_tag.a['href'] if title_tag and title_tag.a and title_tag.a.has_attr('href') else ""
        if link and not link.startswith("http"):
            link = "https://travel.qunar.com" + link
        # 作者
        author_a = li.find("span", class_="user_name")
        author = author_a.get_text(strip=True) if author_a else ""
        # 出发时间、天数、费用、人物、主题（玩法）
        intro = li.find("span", class_="intro")
        date, days, fee, people, trip = "", "", "", "", ""
        if intro:
            intro_text = intro.text.replace('\xa0', ' ')
            # 出发时间
            date_match = re.search(r"(\d{4}-\d{2}-\d{2}) 出发", intro_text)
            date = date_match.group(1) if date_match else ""
            # 天数
            days_match = re.search(r"共(\d+)天", intro_text)
            days = days_match.group(1) if days_match else ""
            # 费用
            fee_match = re.search(r"人均(\d+)元", intro_text)
            fee = fee_match.group(1) if fee_match else ""
            # 人物
            people_match = re.search(r"(独自一人|三五好友|亲子|家庭|情侣|闺蜜|学生)", intro_text)
            people = people_match.group(1) if people_match else ""
            # 主题
            trip_find = intro.find("span", class_="trip")
            if trip_find:
                trip = trip_find.get_text(strip=True).replace('\xa0', ' ').replace(' ', ' ')
        # 浏览数
        num_view = li.find("span", class_="icon_view")
        view = parse_num(num_view.find_all("span")[1].text if num_view and len(num_view.find_all("span"))>1 else "") if num_view else 0
        # 点赞
        num_love = li.find("span", class_="icon_love")
        like = parse_num(num_love.find_all("span")[1].text if num_love and len(num_love.find_all("span"))>1 else "") if num_love else 0
        # 评论
        num_comment = li.find("span", class_="icon_comment")
        comment = parse_num(num_comment.find_all("span")[1].text if num_comment and len(num_comment.find_all("span"))>1 else "") if num_comment else 0
        # 途经城市（目的地）
        p_places = li.find_all("p", class_="places")
        dest = ""
        if p_places:
            for p in p_places:
                if "途经" in p.get_text():
                    dest = p.get_text(strip=True).replace('途经：','')
                    break
        # 行程
        itinerary = ""
        if p_places:
            for p in p_places:
                if "行程" in p.get_text():
                    itinerary = p.get_text(strip=True).replace('行程：','')
                    break
        result.append({
            "标题": title,
            "链接": link,
            "作者": author,
            "出发时间": date,
            "天数": days,
            "费用": fee,
            "人物": people,
            "主题": trip,
            "浏览": view,
            "点赞": like,
            "评论": comment,
            "目的地": dest,
            "行程": itinerary,
        })
    return result

def crawl_qunar_travelbooks(max_pages=200, sleep_sec=1):
    base_url = "https://travel.qunar.com/travelbook/list.htm?page={}&order=hot_heat"
    all_data = []
    for page in range(1, max_pages+1):
        url = base_url.format(page)
        print(f"抓取第{page}页: {url}")
        data = crawl_qunar_page(url)
        print(f"本页抓到{len(data)}条")
        all_data.extend(data)
        time.sleep(sleep_sec)
    return pd.DataFrame(all_data)

if __name__ == "__main__":
    df = crawl_qunar_travelbooks(max_pages=200)
    print("共抓取", len(df), "条数据")
    df.to_csv("qunar_travel.csv", index=False, encoding="utf-8-sig")
    print("已保存为qunar_travel.csv")