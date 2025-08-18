# -*- coding: utf-8 -*-
"""
Streamlit App: Book → Matching Music Playlists (Enhanced)

📚→🎶 사용자가 책을 입력하면 분위기에 맞는 음악 플레이리스트(YouTube/Spotify)를 추천합니다.
"""

import json
import re
import requests
from typing import Dict, List, Tuple
import streamlit as st

st.set_page_config(
    page_title="Book → Music Recommender",
    page_icon="🎧",
    layout="wide",
)

# ---------- 스타일 ----------
CUSTOM_CSS = """
<style>
    .app-title {font-size: 2.0rem; font-weight: 800; margin-bottom: .25rem}
    .app-sub {color: #6b7280; margin-bottom: 1rem}
    .pill {display:inline-block;padding:6px 10px;border-radius:999px;background:#111827;color:white;font-size:.8rem;margin-right:6px}
    .card {border-radius: 16px; padding: 16px; box-shadow: 0 6px 24px rgba(0,0,0,.08); background: white;}
    .playlist-card {border-radius: 16px; padding: 16px; box-shadow: 0 8px 32px rgba(0,0,0,.08); background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);} 
    .source {font-size:.8rem; color:#6b7280}
    .footer-note {font-size:.85rem; color:#6b7280}
    .divider {height:1px;background:#e5e7eb;margin:8px 0 16px}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- 플레이리스트 카탈로그 ----------
PLAYLISTS = {
    "calm_focus": {"name": "Lo-Fi Beats for Deep Focus","platform": "youtube","url": "https://www.youtube.com/embed/jfKfPfyJRdk","tags": ["lofi","focus","calm"]},
    "epic_adventure": {"name": "Epic Orchestral Adventure","platform": "youtube","url": "https://www.youtube.com/embed/2H5z2I_LQqE","tags": ["orchestra","epic","fantasy"]},
    "cozy_romance": {"name": "Cozy Romance: Piano & Jazz","platform": "youtube","url": "https://www.youtube.com/embed/DWcJFNfaw9c","tags": ["romance","piano","jazz"]},
    "mystery_noir": {"name": "Mystery & Noir Ambience","platform": "youtube","url": "https://www.youtube.com/embed/dA1J9Z8PZQA","tags": ["mystery","noir","ambient"]},
    "sci_synthwave": {"name": "Synthwave for Sci-Fi","platform": "youtube","url": "https://www.youtube.com/embed/MqpsxFpkd9g","tags": ["synthwave","sci-fi","electronic"]},
    "historical_classical": {"name": "Baroque & Classical Study","platform": "youtube","url": "https://www.youtube.com/embed/GRxofEmo3HA","tags": ["classical","baroque","study"]},
    "selfhelp_productivity": {"name": "Productive Study Beats","platform": "spotify","url": "https://open.spotify.com/embed/playlist/37i9dQZF1DX8Uebhn9wzrS","tags": ["beats","productivity","study"]},
    "nature_ambient": {"name": "Ambient / Rain for Reading","platform": "youtube","url": "https://www.youtube.com/embed/lE6RYpe9IT0","tags": ["ambient","rain","calm"]},
    "thriller_dark": {"name": "Dark Thriller Soundtracks","platform": "youtube","url": "https://www.youtube.com/embed/I0ZpJbmrYRU","tags": ["thriller","dark","suspense"]},
    "happy_uplift": {"name": "Happy & Uplifting Pop Mix","platform": "youtube","url": "https://www.youtube.com/embed/K4DyBUG242c","tags": ["happy","pop","uplift"]},
    "philosophy_ambient": {"name": "Philosophical Ambient Soundscape","platform": "youtube","url": "https://www.youtube.com/embed/qsZlL8kV7gI","tags": ["philosophy","ambient","deep"]},
}

# ---------- 장르/키워드 ----------
MOOD_RULES = [
    ("fantasy", ["fantasy","마법","모험","용","왕좌","엘프","드래곤"], "epic_adventure"),
    ("romance", ["romance","사랑","연애","로맨스","청춘"], "cozy_romance"),
    ("mystery", ["mystery","미스터리","추리","스릴러","범죄","noir"], "mystery_noir"),
    ("science fiction", ["sf","sci-fi","공상","우주","사이버","디스토피아","로봇"], "sci_synthwave"),
    ("historical", ["역사","고전","근대","중세","왕조","삼국"], "historical_classical"),
    ("self-help", ["자기계발","습관","생산성","공부법","멘탈","성장"], "selfhelp_productivity"),
    ("calm", ["에세이","수필","명상","휴식","치유"], "nature_ambient"),
    ("thriller", ["스릴러","범죄","서스펜스","공포"], "thriller_dark"),
    ("happy", ["행복","웃음","희망","기쁨"], "happy_uplift"),
    ("philosophy", ["철학","사유","존재","의미"], "philosophy_ambient"),
]

DEFAULT_MOOD = "calm_focus"

# ---------- Open Library API ----------
OL_SEARCH = "https://openlibrary.org/search.json"
OL_COVER = "https://covers.openlibrary.org/b/id/{bid}-L.jpg"

@st.cache_data(show_spinner=False)
def fetch_openlibrary(title: str, author: str = "") -> Dict:
    try:
        params = {"title": title}
        if author: params["author"] = author
        r = requests.get(OL_SEARCH, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("docs"):
            doc = data["docs"][0]
            cover_id = doc.get("cover_i")
            cover_url = OL_COVER.format(bid=cover_id) if cover_id else ""
            subjects = doc.get("subject", [])
            return {
                "title": doc.get("title", title),
                "author": ", ".join(doc.get("author_name", [])[:3]),
                "subjects": subjects,
                "cover_url": cover_url,
                "description": doc.get("first_sentence", [""])[0] if doc.get("first_sentence") else ""
            }
    except Exception:
        pass
    return {"title": title, "author": author, "subjects": [], "cover_url": "", "description": ""}

# ---------- 매칭 로직 ----------
def infer_moods(title: str, subjects: List[str], extra_tags: List[str]) -> List[Tuple[str, str]]:
    text = " ".join([title] + subjects + extra_tags).lower()
    scores = {k: 0 for k in PLAYLISTS.keys()}
    reasons = {k: [] for k in PLAYLISTS.keys()}

    for label, keywords, mood in MOOD_RULES:
        for kw in keywords:
            if kw.lower() in text:
                scores[mood] += 2
                reasons[mood].append(f"키워드 '{kw}' → {label}")

    if all(v == 0 for v in scores.values()):
        scores[DEFAULT_MOOD] += 1
        reasons[DEFAULT_MOOD].append("기본 분위기: 집중/학습용")

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top = [(k, "; ".join(reasons[k]) or "일반 독서에 적합") for k, _ in ranked[:3]]
    return top

# ---------- UI ----------
st.title("📚→🎶 도서 기반 음악 플레이리스트 추천")

title = st.text_input("도서 제목", placeholder="예: Demian, Harry Potter")
author = st.text_input("저자 (선택)")

extra_tags = st.multiselect("추가 키워드", ["판타지","로맨스","미스터리","스릴러","SF","역사","에세이","자기계발","명상","철학","청춘","모험","고전"], default=[])

if title:
    with st.spinner("도서 정보를 불러오는 중..."):
        book = fetch_openlibrary(title, author)

    st.subheader("📖 도서 정보")
    col1, col2 = st.columns([0.3,0.7])
    with col1:
        if book["cover_url"]:
            st.image(book["cover_url"], use_column_width=True)
        else:
            st.image("https://placehold.co/400x600?text=No+Cover", use_column_width=True)
    with col2:
        st.write("**제목:**", book["title"])
        st.write("**저자:**", book["author"])
        st.write("**설명:**", book["description"] if book["description"] else "설명이 없습니다.")

    st.subheader("🎶 추천 플레이리스트")
    candidates = infer_moods(book["title"], book["subjects"], extra_tags)
    for mood_key, reason in candidates:
        pl = PLAYLISTS[mood_key]
        st.markdown(f"### {pl['name']}")
        st.caption(f"플랫폼: {pl['platform'].title()} | 이유: {reason}")
        if pl["platform"] == "youtube":
            st.video(pl["url"])
        elif pl["platform"] == "spotify":
            st.components.v1.iframe(pl["url"], height=352)
