import requests
import sqlite3
import re
import time
import random
from bs4 import BeautifulSoup
from datetime import date
from urllib.parse import urljoin, urlparse, parse_qs

# 配置请求头（User-Agent 等）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}

# 晋江基础URL和排行榜URL模板
BASE_URL = "https://www.jjwxc.net/"
RANK_URL_TEMPLATE = (
    "https://www.jjwxc.net/bookbase.php?sortType=4&collectiontypes=ors&page={page}"
)


def extract_novelid(novel_url: str):
    """从小说链接URL中提取 novelid 参数"""
    query = parse_qs(urlparse(novel_url).query)
    if "novelid" in query and query["novelid"]:
        return int(query["novelid"][0])
    # 部分链接格式可能不同，做额外处理
    if "novelid=" in novel_url:
        return int(novel_url.split("novelid=")[-1].split("&")[0])
    return None


def crawl_rank_page(page=1, limit=None):
    """抓取排行榜列表页，返回该页上的小说概要列表"""
    url = RANK_URL_TEMPLATE.format(page=page)
    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        print(f"获取第{page}页排行失败：", e)
        return []

    # 晋江页面编码为 GBK/GB18030，需要正确解析编码
    resp.encoding = resp.apparent_encoding or "gb18030"
    soup = BeautifulSoup(resp.text, "lxml")
    rows = soup.find_all("tr")
    novels = []
    # 跳过表头，从第2行开始解析
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        author = cols[0].get_text(strip=True)  # 作者名在第一列
        title_tag = cols[1].find("a", href=True)
        if not title_tag:
            continue
        novel_name = title_tag.get_text(strip=True)  # 小说名称
        novel_url = urljoin(BASE_URL, title_tag["href"])  # 小说详情页URL
        novel_id = extract_novelid(novel_url)  # 小说ID
        if novel_id is None:
            continue

        # 尝试从<a>标签的 title 属性中提取简介和标签
        intro = None
        tags = None
        title_attr = title_tag.get("title") or ""
        if "简介：" in title_attr:
            if "标签：" in title_attr:
                left, right = title_attr.split("标签：", 1)
                intro = left.replace("简介：", "").strip()
                tags = right.strip()
            else:
                intro = title_attr.replace("简介：", "").strip()

        novels.append(
            {
                "novel_id": novel_id,
                "novel_name": novel_name,
                "author": author,
                "url": novel_url,
                "intro": intro,
                "tags": tags,
            }
        )

        if limit and len(novels) >= limit:
            break
    return novels


def fetch_first_300_text_from_first_chapter(novel_id: int, novel_soup: BeautifulSoup):
    """
    从小说主页 soup 中找到第一章的免费章节链接，
    打开章节页并提取正文前 300 字。
    """
    # 查找第一章的免费章节链接：onebook.php?novelid=xxx&chapterid=1 这类
    first_chapter_link = novel_soup.find(
        "a", href=re.compile(r"onebook\.php\?novelid=\d+&chapterid=\d+")
    )
    if not first_chapter_link:
        return None

    chapter_href = first_chapter_link.get("href")
    if not chapter_href:
        return None

    # VIP 章节一般是 onebook_vip.php 或带 vip 字样，直接跳过
    if "vip" in chapter_href.lower():
        return None

    chapter_url = urljoin(BASE_URL, chapter_href)

    try:
        resp = requests.get(chapter_url, headers=headers, timeout=15)
    except Exception as e:
        print(f"获取章节页面失败：{chapter_url}，原因：{e}")
        return None

    resp.encoding = resp.apparent_encoding or "gb18030"
    csoup = BeautifulSoup(resp.text, "lxml")

    # 一般正文在 class="novelbody" 下面，或者 style 含有 font-size:16px 的 div 中
    content_div = csoup.find("div", class_="novelbody")
    if content_div is None:
        content_div = csoup.find("div", style=re.compile(r"font-size:\s*16px"))

    if content_div is None:
        return None

    # 提取正文文本并压缩空白
    text = content_div.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    if not text:
        return None

    return text[:300]


def fetch_novel_detail(novel_url: str, novel_id: int):
    """
    抓取单本小说的详情页信息，返回解析后的字段字典。
    会额外尝试抓取第一章正文前300字：字段 first_300_text
    """
    data = {}
    try:
        resp = requests.get(novel_url, headers=headers, timeout=15)
    except Exception as e:
        print(f"获取小说详情失败：{novel_url}, 原因：", e)
        return data

    # 晋江详情页通常为 GBK 编码
    resp.encoding = resp.apparent_encoding or "gb18030"
    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text()  # 页面所有文本，用于搜索特定关键字

    # 1. 小说简介（文案）
    intro_div = soup.find("div", id="novelintro", attrs={"itemprop": "description"})
    if intro_div:
        data["intro"] = intro_div.get_text("\n", strip=True)

    # 2. 主角/配角/其它信息
    idx = page_text.find("主角：")
    if idx != -1:
        snippet = page_text[idx : idx + 200]
        data["main_chars"] = None
        data["support_chars"] = None
        data["other_info"] = None
        parts = snippet.split("┃")
        for part in parts:
            part = part.strip()
            if part.startswith("主角："):
                data["main_chars"] = part.replace("主角：", "").strip()
            elif part.startswith("配角："):
                data["support_chars"] = part.replace("配角：", "").strip()
            elif part.startswith("其它："):
                data["other_info"] = part.replace("其它：", "").strip()

    # 3. 基本信息列表（类型、视角、字数、出版、签约状态等）
    info_ul = soup.find("ul", attrs={"name": "printright"})
    if info_ul:
        li_tags = info_ul.find_all("li")
        for li in li_tags:
            text = li.get_text(strip=True)
            if text.startswith("文章类型："):
                data["category"] = text.replace("文章类型：", "")
            elif text.startswith("作品视角："):
                data["perspective"] = text.replace("作品视角：", "")
            elif text.startswith("所属系列："):
                data["series"] = text.replace("所属系列：", "")
            elif text.startswith("文章进度："):
                data["status"] = text.replace("文章进度：", "")
            elif text.startswith("全文字数："):
                num_str = "".join(filter(str.isdigit, text))
                data["word_count"] = int(num_str) if num_str else None
            elif text.startswith("版权转化："):
                if "尚未出版" in text:
                    data["publish_status"] = "尚未出版"
                else:
                    data["publish_status"] = "已出版" if li.find("img") else text.replace(
                        "版权转化：", ""
                    )
            elif text.startswith("签约状态："):
                font_tag = li.find("font")
                if font_tag:
                    data["sign_status"] = font_tag.get_text(strip=True)
                else:
                    data["sign_status"] = text.replace("签约状态：", "")

    # 4. 底部统计数据（评论数、收藏数、营养液数、积分、非V点击等）
    stats_div = soup.find("div", attrs={"align": "center"})
    if stats_div:
        stats_text = stats_div.get_text()
        m = re.search(
            r"总书评数：(\d+).*?当前被收藏数：(\d+).*?营养液数：(\d+).*?文章积分：([\d,]+)",
            stats_text,
            re.S,
        )
        if m:
            data["review_count"] = int(m.group(1))
            data["favorite_count"] = int(m.group(2))
            data["nutrient_count"] = int(m.group(3))
            score_str = m.group(4).replace(",", "")
            data["score"] = int(score_str) if score_str.isdigit() else None
        m2 = re.search(r"非V章节总点击数：(\d+)", stats_text)
        if m2:
            data["total_click_count"] = int(m2.group(1))

    # 5. 最新更新时间和章节数
    if "最新更新" in page_text:
        m3 = re.search(
            r"最新更新[:：](\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", page_text
        )
        if m3:
            data["last_update_time"] = m3.group(1)

    chapter_links = soup.find_all(
        "a", href=re.compile(r"novelid=\d+&chapterid=\d+")
    )
    data["chapter_count"] = len(chapter_links)

    # 6. 章节正文前300字
    first_300_text = fetch_first_300_text_from_first_chapter(novel_id, soup)
    data["first_300_text"] = first_300_text

    return data


# ========== 数据库部分 ==========

# 连接SQLite数据库（文件不存在会自动创建）
conn = sqlite3.connect("jinjiang_novels.db")
cur = conn.cursor()

# 创建主要数据表（书籍基本信息表 和 统计信息表）
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS book (
        book_id          INTEGER PRIMARY KEY,
        title            TEXT,
        author           TEXT,
        intro            TEXT,
        tags             TEXT,
        main_chars       TEXT,
        support_chars    TEXT,
        other_info       TEXT,
        category         TEXT,
        perspective      TEXT,
        series           TEXT,
        status           TEXT,
        word_count       INTEGER,
        publish_status   TEXT,
        sign_status      TEXT,
        last_update_time TEXT,
        chapter_count    INTEGER,
        first_300_text   TEXT
    )
"""
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS stats (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id           INTEGER,
        date              TEXT,
        review_count      INTEGER,
        favorite_count    INTEGER,
        nutrient_count    INTEGER,
        total_click_count INTEGER,
        score             INTEGER,
        chapter_count     INTEGER,
        FOREIGN KEY(book_id) REFERENCES book(book_id)
    )
"""
)
conn.commit()

# 如果之前已经创建过 book 表但没有 first_300_text 字段，这里尝试补上
cur.execute("PRAGMA table_info(book)")
cols = [row[1] for row in cur.fetchall()]
if "first_300_text" not in cols:
    cur.execute("ALTER TABLE book ADD COLUMN first_300_text TEXT")
    conn.commit()

# ========== 爬取排行榜并写入数据库 ==========

target_count = 150  # 目标采集小说数量
all_novel_list = []
page = 1

while len(all_novel_list) < target_count:
    novels = crawl_rank_page(page=page)
    if not novels:
        break
    all_novel_list.extend(novels)
    if len(all_novel_list) >= target_count:
        break
    page += 1
    time.sleep(random.uniform(1.0, 2.0))

all_novel_list = all_novel_list[:target_count]

for novel in all_novel_list:
    novel_id = novel["novel_id"]
    novel_name = novel["novel_name"]
    author = novel["author"]
    novel_url = novel["url"]

    detail = fetch_novel_detail(novel_url, novel_id)
    if not detail:
        continue

    # 优先使用详情页获取的完整简介；如详情页无简介，则用列表页摘要
    intro_text = detail.get("intro") or novel.get("intro") or ""
    tags_text = novel.get("tags") or ""

    main_chars = detail.get("main_chars")
    support_chars = detail.get("support_chars")
    other_info = detail.get("other_info")
    category = detail.get("category")
    perspective = detail.get("perspective")
    series = detail.get("series")
    status = detail.get("status")
    word_count = detail.get("word_count")
    publish_status = detail.get("publish_status")
    sign_status = detail.get("sign_status")
    last_update = detail.get("last_update_time")
    chapter_count = detail.get("chapter_count")
    first_300_text = detail.get("first_300_text")

    # 将基本信息插入或更新到 book 表
    cur.execute(
        """
        INSERT OR REPLACE INTO book 
        (book_id, title, author, intro, tags, main_chars, support_chars, other_info,
         category, perspective, series, status, word_count,
         publish_status, sign_status, last_update_time, chapter_count, first_300_text)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            novel_id,
            novel_name,
            author,
            intro_text,
            tags_text,
            main_chars,
            support_chars,
            other_info,
            category,
            perspective,
            series,
            status,
            word_count,
            publish_status,
            sign_status,
            last_update,
            chapter_count,
            first_300_text,
        ),
    )

    # 将当前爬取日期的动态数据插入到 stats 表
    cur.execute(
        """
        INSERT INTO stats 
        (book_id, date, review_count, favorite_count, nutrient_count, total_click_count, score, chapter_count)
        VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            novel_id,
            date.today().isoformat(),
            detail.get("review_count"),
            detail.get("favorite_count"),
            detail.get("nutrient_count"),
            detail.get("total_click_count"),
            detail.get("score"),
            chapter_count,
        ),
    )

    conn.commit()
    time.sleep(random.uniform(0.5, 1.0))

conn.close()
print(f"共采集{len(all_novel_list)}本小说的数据，已保存到数据库。")