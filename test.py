# app.py
# 실행: streamlit run app.py

import streamlit as st
import feedparser
import requests
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
from readability import Document
from datetime import datetime, timezone
from dateutil import tz
import pandas as pd

# ---- 요약 (Sumy - LexRank) ----
from sumy.parsers.plaintext import PlainTextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# --------- 기본 설정 ----------
st.set_page_config(
    page_title="실시간 뉴스 요약 웹",
    page_icon="🗞️",
    layout="wide"
)

KST = tz.gettz("Asia/Seoul")

# --------- 유틸 ----------
def to_kst(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST)

def reltime(dt: datetime) -> str:
    dt = to_kst(dt)
    delta = datetime.now(KST) - dt
    s = int(delta.total_seconds())
    if s < 60: return f"{s}초 전"
    m = s // 60
    if m < 60: return f"{m}분 전"
    h = m // 60
    if h < 24: return f"{h}시간 전"
    d = h // 24
    return f"{d}일 전"

def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines()]
    text = "\n".join([ln for ln in lines if ln])
    return text

@st.cache_data(show_spinner=False, ttl=300)
def fetch_article_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        doc = Document(res.text)
        html = doc.summary(html_partial=True)
        text = clean_text(html)
        if len(text) < 400:
            text = clean_text(res.text)
        return text
    except Exception:
        return ""

def lexrank_summary(text: str, n_sentences: int = 3, language: str = "korean") -> list[str]:
    if not text or len(text.split()) < 30:
        return []
    parser = PlainTextParser.from_string(text, Tokenizer(language))
    summarizer = LexRankSummarizer()
    sentences = summarizer(parser.document, n_sentences)
    return [str(s) for s in sentences]

def google_news_rss_url(query: str = "", topic: str = "", lang: str = "ko", country: str = "KR") -> str:
    base = "https://news.google.com/rss"
    if query:
        return f"{base}/search?q={quote(query)}&hl={lang}&gl={country}&ceid={country}%3A{lang}"
    topic_map = {
        "헤드라인": "",
        "국제": "WORLD",
        "한국": "NATION",
        "비즈니스·경제": "BUSINESS",
        "과학": "SCIENCE",
        "기술·IT": "TECHNOLOGY",
        "엔터테인먼트": "ENTERTAINMENT",
        "스포츠": "SPORTS",
        "건강": "HEALTH",
    }
    code = topic_map.get(topic, "")
    if code:
        return f"{base}/headlines/section/topic/{code}?hl={lang}&gl={country}&ceid={country}%3A{lang}"
    else:
        return f"{base}?hl={lang}&gl={country}&ceid={country}%3A{lang}"

@st.cache_data(show_spinner=False, ttl=120)
def fetch_feed(url: str):
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries:
        title = e.get("title", "").strip()
        link = e.get("link", "")
        published_dt = None
        if "published_parsed" in e and e.published_parsed:
            published_dt = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
        elif "updated_parsed" in e and e.updated_parsed:
            published_dt = datetime(*e.updated_parsed[:6], tzinfo=timezone.utc)
        summary = BeautifulSoup(e.get("summary", ""), "html.parser").get_text(" ")
        source = ""
        if "source" in e and e.source and e.source.get("title"):
            source = e.source.title
        elif link:
            source = urlparse(link).netloc.replace("www.", "")
        items.append({
            "title": title,
            "link": link,
            "summary": summary.strip(),
            "source": source,
            "published": published_dt or datetime.now(timezone.utc),
        })
    items.sort(key=lambda x: x["published"], reverse=True)
    return items

# --------- 사이드바 ----------
with st.sidebar:
    st.title("🗞️ 실시간 뉴스 요약")
    mode = st.radio("모드", ["토픽 탐색", "키워드 검색"], horizontal=True)
    if mode == "토픽 탐색":
        topic = st.selectbox("카테고리",
            ["헤드라인","한국","국제","비즈니스·경제","기술·IT","과학","스포츠","엔터테인먼트","건강"],
            index=0
        )
        rss = google_news_rss_url(topic=topic)
    else:
        query = st.text_input("검색어", value="AI")
        rss = google_news_rss_url(query=query)

    n_show = st.slider("표시할 기사 개수", 3, 30, 10)
    n_sum = st.slider("요약 문장 수", 2, 7, 3)
    bullet_mode = st.checkbox("불릿 형식 요약", value=True)

# --------- 메인 ----------
st.markdown("## 🗞️ 실시간 뉴스 요약 웹")

with st.spinner("뉴스 불러오는 중..."):
    items = fetch_feed(rss)
    cards = items[:n_show]

export_rows = []
for it in cards:
    with st.container(border=True):
        st.markdown(f"### [{it['title']}]({it['link']})")
        st.caption(f"{it['source']} • {reltime(it['published'])}")

        with st.spinner("본문 요약 중..."):
            article_text = fetch_article_text(it["link"])
            summary_sents = lexrank_summary(article_text, n_sum, language="korean")

        if summary_sents:
            if bullet_mode:
                st.markdown("\n".join([f"- {s}" for s in summary_sents]))
            else:
                st.write(" ".join(summary_sents))
        else:
            st.info(it["summary"] or "요약 불가")

        export_rows.append({
            "title": it["title"],
            "link": it["link"],
            "source": it["source"],
            "published": to_kst(it["published"]).strftime("%Y-%m-%d %H:%M"),
            "summary": " ".join(summary_sents) if summary_sents else it["summary"],
        })

df = pd.DataFrame(export_rows)
csv = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("📥 CSV 다운로드", csv, "news_summary.csv", "text/csv")

st.caption("⚠️ 교육용 데모. 일부 뉴스 사이트는 본문 추출이 안 될 수 있습니다.")
