# app.py
# 실시간 뉴스 요약 웹 (K-버전)
# 실행: streamlit run app.py

import streamlit as st
import feedparser
import requests
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
from readability import Document
from datetime import datetime, timezone
from dateutil import tz
from typing import List, Dict
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
    # 기사 본문에서 스크립트/스타일 제거
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines()]
    text = "\n".join([ln for ln in lines if ln])
    return text

@st.cache_data(show_spinner=False, ttl=300)
def fetch_article_text(url: str) -> str:
    """기사 URL에서 본문 추출(readability -> bs4 클린업)"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/118.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        doc = Document(res.text)
        html = doc.summary(html_partial=True)
        text = clean_text(html)
        # 만약 뽑힌 본문이 너무 짧으면 전체 페이지에서 추출
        if len(text) < 400:
            text = clean_text(res.text)
        return text
    except Exception:
        return ""

def lexrank_summary(text: str, n_sentences: int = 3, language: str = "korean") -> List[str]:
    """언어에 상관없이 대체로 동작(한국어도 OK)하는 LexRank 기반 문장 추출 요약"""
    if not text or len(text.split()) < 30:
        return []
    parser = PlainTextParser.from_string(text, Tokenizer(language))
    summarizer = LexRankSummarizer()
    sentences = summarizer(parser.document, n_sentences)
    return [str(s) for s in sentences]

def google_news_rss_url(
    query: str = "",
    topic: str = "",
    lang: str = "ko",
    country: str = "KR"
) -> str:
    base = "https://news.google.com/rss"
    if query:
        # 검색 모드
        return f"{base}/search?q={quote(query)}&hl={lang}&gl={country}&ceid={country}%3A{lang}"
    # 토픽 모드
    topic_map = {
        "헤드라인": "",            # 기본
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
def fetch_feed(url: str) -> List[Dict]:
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
    # 최신순 정렬
    items.sort(key=lambda x: x["published"], reverse=True)
    return items

def make_cards(items: List[Dict], max_items: int) -> List[Dict]:
    return items[:max_items]

# --------- 사이드바 ----------
with st.sidebar:
    st.title("🗞️ 실시간 뉴스 요약")
    mode = st.radio("모드", ["토픽 탐색", "키워드 검색"], horizontal=True)
    if mode == "토픽 탐색":
        topic = st.selectbox(
            "카테고리",
            ["헤드라인", "한국", "국제", "비즈니스·경제", "기술·IT", "과학", "스포츠", "엔터테인먼트", "건강"],
            index=0
        )
        rss = google_news_rss_url(topic=topic)
    else:
        query = st.text_input("검색어 (예: 반도체, 총선, AI 반도체)", value="AI")
        rss = google_news_rss_url(query=query)

    n_show = st.slider("표시할 기사 개수", min_value=3, max_value=30, value=10, step=1)
    n_sum = st.slider("요약 문장 수", min_value=2, max_value=7, value=3, step=1)

    st.markdown("---")
    st.subheader("요약 옵션")
    bullet_mode = st.checkbox("키 문장 불릿으로 표시", value=True)
    include_source_snippet = st.checkbox("RSS 요약문도 함께 표시", value=False)

    st.markdown("---")
    st.caption("⏱️ 데이터는 2~5분 간 캐시됩니다.")

# --------- 헤더 ----------
st.markdown("## 🗞️ 실시간 뉴스 요약 웹")
if mode == "토픽 탐색":
    st.caption(f"카테고리: **{topic}** • 소스: Google News RSS • 타임존: KST")
else:
    st.caption(f"검색어: **{query}** • 소스: Google News RSS • 타임존: KST")

# --------- 데이터 로드 ----------
with st.spinner("뉴스 불러오는 중..."):
    items = fetch_feed(rss)
    cards = make_cards(items, n_show)

# --------- TOP 3 하이라이트 ----------
top3 = cards[:3]
if top3:
    st.markdown("### ⭐ 오늘의 TOP 3")
    cols = st.columns(len(top3))
    for c, it in zip(cols, top3):
        with c:
            st.markdown(f"**[{it['title']}]({it['link']})**")
            st.caption(f"{it['source']} • {reltime(it['published'])}")

st.markdown("---")

# --------- 본문 & 요약 렌더링 ----------
export_rows = []
for it in cards:
    with st.container(border=True):
        left, right = st.columns([0.72, 0.28], vertical_alignment="start")
        with left:
            st.markdown(f"#### [{it['title']}]({it['link']})")
            st.caption(f"{it['source']} • {reltime(it['published'])}")
            # 기사 본문 추출 & 요약
            with st.spinner("요약 생성 중..."):
                article_text = fetch_article_text(it["link"])
                summary_sents = lexrank_summary(article_text, n_sum, language="korean")
            if summary_sents:
                if bullet_mode:
                    st.markdown("\n".join([f"- {s}" for s in summary_sents]))
                else:
                    st.write(" ".join(summary_sents))
            else:
                st.info("본문을 안정적으로 추출하지 못해 RSS 요약문을 대신 표시합니다.")
            if include_source_snippet and it["summary"]:
                with st.expander("원문 RSS 요약 보기"):
                    st.write(it["summary"])
        with right:
            st.write("**핵심 정보**")
            st.write(f"- 출처: {it['source'] or '알수없음'}")
            st.write(f"- 게시: {to_kst(it['published']).strftime('%Y-%m-%d %H:%M')}")
            st.link_button("기사 열기", it["link"])

        # 다운로드용 레코드 축적
        export_rows.append({
            "title": it["title"],
            "link": it["link"],
            "source": it["source"],
            "published_kst": to_kst(it["published"]).strftime('%Y-%m-%d %H:%M'),
            "summary": " ".join(summary_sents) if summary_sents else it["summary"],
        })

st.markdown("---")

# --------- 내보내기 ----------
df_export = pd.DataFrame(export_rows)
col1, col2 = st.columns([0.5, 0.5])
with col1:
    st.write("### 📤 요약 결과 내보내기")
with col2:
    csv = df_export.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSV 다운로드",
        data=csv,
        file_name="news_summaries.csv",
        mime="text/csv"
    )

with st.expander("데이터 미리보기"):
    st.dataframe(df_export, use_container_width=True)

# --------- 푸터 ----------
st.caption(
    "※ 교육용 데모입니다. 일부 사이트는 본문 추출이 제한될 수 있어 RSS 요약으로 대체될 수 있습니다. "
    "요약은 LexRank(추출 요약)으로 생성됩니다."
)
