# -*- coding: utf-8 -*-
"""
Streamlit App: Book → Song Recommender (개별 곡 추천)
"""

import streamlit as st

st.set_page_config(
    page_title="Book → Song Recommender",
    page_icon="🎧",
    layout="wide",
)

# ---------- 스타일 ----------
CUSTOM_CSS = """
<style>
    .app-title {font-size: 2.0rem; font-weight: 800; margin-bottom: .25rem}
    .song-card {border-radius: 12px; padding: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.08); margin-bottom: 16px; background: #ffffff;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- 노래 데이터 ----------
SONGS = {
    "fantasy": [
        ("Ed Sheeran - I See Fire", "https://www.youtube.com/watch?v=2fngvQS_PmQ"),
        ("Imagine Dragons - Warriors", "https://www.youtube.com/watch?v=fmI_Ndrxy14"),
        ("Florence + The Machine - Spectrum", "https://www.youtube.com/watch?v=iC-_lVzdiFE"),
    ],
    "romance": [
        ("Adele - Make You Feel My Love", "https://www.youtube.com/watch?v=0put0_a--Ng"),
        ("Lauv - I Like Me Better", "https://www.youtube.com/watch?v=BcqxLCWn-CE"),
        ("Bruno Mars - Just The Way You Are", "https://www.youtube.com/watch?v=LjhCEhWiKXk"),
    ],
    "mystery": [
        ("Billie Eilish - bury a friend", "https://www.youtube.com/watch?v=HUHC9tYz8ik"),
        ("Radiohead - Climbing Up The Walls", "https://www.youtube.com/watch?v=snJt_cY0S5Y"),
        ("Arctic Monkeys - Do I Wanna Know?", "https://www.youtube.com/watch?v=bpOSxM0rNPM"),
    ],
    "sci-fi": [
        ("Muse - Starlight", "https://www.youtube.com/watch?v=Pgum6OT_VH8"),
        ("Daft Punk - Harder, Better, Faster, Stronger", "https://www.youtube.com/watch?v=gAjR4_CbPpQ"),
        ("The Weeknd - Blinding Lights", "https://www.youtube.com/watch?v=4NRXx6U8ABQ"),
    ],
    "thriller": [
        ("Michael Jackson - Thriller", "https://www.youtube.com/watch?v=sOnqjkJTMaA"),
        ("Imagine Dragons - Believer", "https://www.youtube.com/watch?v=7wtfhZwyrcc"),
        ("Kanye West - Black Skinhead", "https://www.youtube.com/watch?v=q604eed4ad0"),
    ],
    "philosophy": [
        ("Pink Floyd - Time", "https://www.youtube.com/watch?v=JwYX52BP2Sk"),
        ("Coldplay - Fix You", "https://www.youtube.com/watch?v=k4V3Mo61fJM"),
        ("The Beatles - Let It Be", "https://www.youtube.com/watch?v=QDYfEBY9NM4"),
    ],
    "happy": [
        ("Pharrell Williams - Happy", "https://www.youtube.com/watch?v=ZbZSe6N_BXs"),
        ("Katrina & The Waves - Walking On Sunshine", "https://www.youtube.com/watch?v=iPUmE-tne5U"),
        ("Justin Timberlake - Can't Stop The Feeling!", "https://www.youtube.com/watch?v=ru0K8uYEZWw"),
    ],
    "calm": [
        ("Lo-Fi Beats - Study Session", "https://www.youtube.com/watch?v=jfKfPfyJRdk"),
        ("Ludovico Einaudi - Nuvole Bianche", "https://www.youtube.com/watch?v=kcihcYEOeic"),
        ("Yiruma - River Flows In You", "https://www.youtube.com/watch?v=7maJOI3QMu0"),
    ],
}

# ---------- 키워드 매핑 ----------
MOOD_RULES = [
    ("fantasy", ["fantasy","마법","모험","용","드래곤"]),
    ("romance", ["사랑","연애","로맨스","청춘"]),
    ("mystery", ["미스터리","추리","범죄"]),
    ("sci-fi", ["sf","sci-fi","공상","우주","사이버"]),
    ("thriller", ["스릴러","서스펜스","공포"]),
    ("philosophy", ["철학","존재","의미"]),
    ("happy", ["행복","희망","기쁨"]),
    ("calm", ["에세이","명상","휴식","치유"]),
]

DEFAULT_MOOD = "calm"

# ---------- 추천 로직 ----------
def infer_mood(text: str) -> str:
    text = text.lower()
    for mood, keywords in MOOD_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return mood
    return DEFAULT_MOOD

# ---------- UI ----------
st.title("📚→🎶 도서 기반 노래 추천")

# 사이드바 설정
st.sidebar.header("⚙️ 설정")
num_songs = st.sidebar.slider("추천할 노래 개수", 1, 5, 3)

title = st.text_input("도서 제목", placeholder="예: Harry Potter, 데미안")
extra_tags = st.text_area("추가 키워드 (쉼표로 구분)", placeholder="예: 마법, 모험, 청춘")

if title:
    text = title + " " + extra_tags
    mood = infer_mood(text)
    song_list = SONGS[mood][:num_songs]

    st.subheader("🎶 추천 노래")
    for song, url in song_list:
        st.markdown(f"<div class='song-card'><b>{song}</b><br><a href='{url}' target='_blank'>[듣기]</a></div>", unsafe_allow_html=True)
