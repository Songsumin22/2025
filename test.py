# -*- coding: utf-8 -*-
"""
Streamlit App: Book → Matching Music Playlists

📚→🎶 사용자가 책을 입력하면 분위기에 맞는 음악 플레이리스트(YouTube/Spotify)를 추천합니다.

주요 기능
- 책 제목/저자 입력 → Open Library API로 표지/설명/주제 태그 자동 탐색(옵션)
- 장르/키워드 기반 분위기(Mood) 매핑 → 플레이리스트 추천
- 즉시 재생 가능한 YouTube/Spotify 임베드 지원
- 추천 근거(키워드 매칭 로직)와 커스텀 태그 편집
- 결과 JSON 다운로드, 히스토리 저장
- 발표용을 고려한 깔끔한 UI와 카드 스타일

필요 패키지
- streamlit >= 1.24
- requests (외부 API 사용 시)

실행
$ streamlit run app.py
"""

import json
import re
import requests
from typing import Dict, List, Tuple, Optional
import streamlit as st

st.set_page_config(
    page_title="Book → Music Recommender",
    page_icon="🎧",
    layout="wide",
)

# ---------- 스타일 (발표용 깔끔 테마) ----------
CUSTOM_CSS = """
<style>
    .app-title {font-size: 2.0rem; font-weight: 800; margin-bottom: .25rem}
    .app-sub {color: #6b7280; margin-bottom: 1rem}
    .pill {display:inline-block;padding:6px 10px;border-radius:999px;background:#111827;color:white;font-size:.8rem;margin-right:6px}
    .card {border-radius: 16px; padding: 16px; box-shadow: 0 6px 24px rgba(0,0,0,.08); background: white;}
    .playlist-card {border-radius: 16px; padding: 16px; box-shadow: 0 8px 32px rgba(0,0,0,.08); background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);} 
    .source {font-size:.8rem; color:#6b7280}
    .footer-note {font-size:.85rem; color:#6b7280}
    .metric {font-weight:700}
    .divider {height:1px;background:#e5e7eb;margin:8px 0 16px}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- 유틸 ----------
def norm_text(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip().lower()

# ---------- 플레이리스트 카탈로그 (샘플) ----------
# 필요 시 자유롭게 수정/추가 가능. YouTube는 watch?v= → embed/ 로 바꿔 임베드.
PLAYLISTS = {
    "calm_focus": {
        "name": "Lo-Fi Beats for Deep Focus",
        "platform": "youtube",
        "url": "https://www.youtube.com/embed/jfKfPfyJRdk",  # Lofi Girl live
        "tags": ["lofi", "focus", "calm"]
    },
    "epic_adventure": {
        "name": "Epic Orchestral Adventure",
        "platform": "youtube",
        "url": "https://www.youtube.com/embed/2H5z2I_LQqE",
        "tags": ["orchestra", "epic", "fantasy"]
    },
    "cozy_romance": {
        "name": "Cozy Romance: Piano & Jazz",
        "platform": "youtube",
        "url": "https://www.youtube.com/embed/DWcJFNfaw9c",
        "tags": ["romance", "piano", "jazz"]
    },
    "mystery_noir": {
        "name": "Mystery & Noir Ambience",
        "platform": "youtube",
        "url": "https://www.youtube.com/embed/dA1J9Z8PZQA",
        "tags": ["mystery", "noir", "ambient"]
    },
    "sci_synthwave": {
        "name": "Synthwave for Sci‑Fi",
        "platform": "youtube",
        "url": "https://www.youtube.com/embed/MqpsxFpkd9g",
        "tags": ["synthwave", "sci-fi", "electronic"]
    },
    "historical_classical": {
        "name": "Baroque & Classical Study",
        "platform": "youtube",
        "url": "https://www.youtube.com/embed/GRxofEmo3HA",
        "tags": ["classical", "baroque", "study"]
    },
    "selfhelp_productivity": {
        "name": "Productive Study Beats",
        "platform": "spotify",
        "url": "https://open.spotify.com/embed/playlist/37i9dQZF1DX8Uebhn9wzrS",
        "tags": ["beats", "productivity", "study"]
    },
    "nature_ambient": {
        "name": "Ambient / Rain for Reading",
        "platform": "youtube",
        "url": "https://www.youtube.com/embed/lE6RYpe9IT0",
        "tags": ["ambient", "rain", "calm"]
    }
}

# ---------- 장르/키워드 → 분위기 매핑 규칙 ----------
MOOD_RULES = [
    ("fantasy", ["fantasy", "마법", "모험", "용", "왕좌", "엘프", "드래곤"], "epic_adventure"),
    ("romance", ["romance", "사랑", "연애", "로맨스", "청춘"], "cozy_romance"),
    ("mystery", ["mystery", "미스터리", "추리", "스릴러", "범죄", "noir"], "mystery_noir"),
    ("science fiction", ["sf", "sci-fi", "공상", "우주", "사이버", "디스토피아"], "sci_synthwave"),
    ("historical", ["역사", "고전", "근대", "중세", "왕조"], "historical_classical"),
    ("self-help", ["자기계발", "습관", "생산성", "공부법", "멘탈"], "selfhelp_productivity"),
    ("calm", ["에세이", "수필", "명상", "휴식", "치유"], "nature_ambient"),
]

DEFAULT_MOOD = "calm_focus"

# ---------- 외부 API: Open Library (선택) ----------
OL_SEARCH = "https://openlibrary.org/search.json"
OL_COVER = "https://covers.openlibrary.org/b/id/{bid}-L.jpg"

@st.cache_data(show_spinner=False)
def fetch_openlibrary(title: str, author: str = "") -> Dict:
    """Open Library에서 제목/저자로 검색 후 베스트 매치 1건 반환."""
    try:
        params = {"title": title}
        if author:
            params["author"] = author
        r = requests.get(OL_SEARCH, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("docs"):
            doc = data["docs"][0]
            cover_id = doc.get("cover_i")
            cover_url = OL_COVER.format(bid=cover_id) if cover_id else ""
            subjects = doc.get("subject", [])
            desc = ""
            # Open Library works API로 상세 설명을 가져오는 로직(가벼운 시도)
            work_key = doc.get("key")  # e.g., "/works/OL262758W"
            if work_key:
                try:
                    wr = requests.get(f"https://openlibrary.org{work_key}.json", timeout=10)
                    if wr.ok:
                        wj = wr.json()
                        d = wj.get("description", "")
                        if isinstance(d, dict):
                            desc = d.get("value", "")
                        elif isinstance(d, str):
                            desc = d
                except Exception:
                    pass
            return {
                "title": doc.get("title", title),
                "author": ", ".join(doc.get("author_name", [])[:3]),
                "subjects": subjects,
                "cover_url": cover_url,
                "description": desc
            }
    except Exception:
        pass
    return {"title": title, "author": author, "subjects": [], "cover_url": "", "description": ""}

# ---------- 매칭 로직 ----------
def infer_moods(title: str, subjects: List[str], extra_tags: List[str]) -> List[Tuple[str, str]]:
    """책 정보에서 분위기 후보를 점수화하여 상위 추천 반환[(mood_key, reason)]."""
    text = " ".join([title] + subjects + extra_tags).lower()
    scores = {k: 0 for k in PLAYLISTS.keys()}
    reasons = {k: [] for k in PLAYLISTS.keys()}

    # 룰 기반 점수
    for label, keywords, mood in MOOD_RULES:
        for kw in keywords:
            if kw.lower() in text:
                scores[mood] += 2
                reasons[mood].append(f"키워드 매칭: '{kw}' → {label}")

    # 기본 가산: 설명/태그가 없을 때 안정적으로 calm_focus 추천
    if all(v == 0 for v in scores.values()):
        scores[DEFAULT_MOOD] += 1
        reasons[DEFAULT_MOOD].append("기본 분위기: 집중/학습용")

    # 정렬 후 상위 3
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top = [(k, "; ".join(reasons[k]) or "일반 독서에 적합") for k, _ in ranked[:3]]
    return top

# ---------- 컴포넌트 ----------
def embed_player(platform: str, url: str, height: int = 352):
    import streamlit.components.v1 as components
    if platform == "youtube":
        # url은 반드시 https://www.youtube.com/embed/... 형태여야 함
        components.html(
            f"""
            <div style='position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:16px;'>
                <iframe src="{url}" title="YouTube player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style='position:absolute;top:0;left:0;width:100%;height:100%;border:0;border-radius:16px;'></iframe>
            </div>
            """,
            height=height,
        )
    elif platform == "spotify":
        components.html(
            f"""
            <iframe style="border-radius:16px" src="{url}" width="100%" height="{height}" frameborder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>
            """,
            height=height,
        )
    else:
        st.info("지원하지 않는 플랫폼입니다. URL을 카드에서 확인하세요.")
        st.write(url)

# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown("<div class='app-title'>📚→🎶 Book → Playlist</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-sub'>도서의 분위기에 어울리는 음악을 추천합니다.</div>", unsafe_allow_html=True)

    st.write("**입력 옵션**")
    mode = st.radio("책 정보 가져오기", ["직접 입력", "Open Library에서 자동 탐색"], index=1)
    title = st.text_input("도서 제목", placeholder="예: 해리 포터와 마법사의 돌 / Demian / The Murder of Roger Ackroyd")
    author = st.text_input("저자(선택)")

    user_genre = st.multiselect(
        "장르/키워드 추가 태그",
        ["판타지", "로맨스", "미스터리", "스릴러", "SF", "역사", "에세이", "자기계발", "명상", "철학", "청춘", "모험", "고전"],
        default=[],
        help="책의 느낌을 더 잘 반영하도록 자유롭게 태그를 추가하세요.",
    )

    st.write("**재생 옵션**")
    prefer = st.selectbox("선호 플랫폼", ["상관없음", "YouTube", "Spotify"], index=0)
    max_recs = st.slider("추천 개수", 1, 5, 3)

    st.write("**디자인**")
    accent = st.color_picker("포인트 색상", value="#111827")

# 포인트 색 적용
st.markdown(f"""
<style>
  :root {{ --accent: {accent}; }}
  .pill {{ background: var(--accent) !important; }}
  .stButton>button {{ border-radius: 999px; padding: .5rem 1rem; font-weight:700; }}
</style>
""", unsafe_allow_html=True)

# ---------- 본문 헤더 ----------
left, right = st.columns([.65, .35])
with left:
    st.markdown("<div class='app-title'>도서 기반 음악 플레이리스트 추천</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-sub'>책의 장르/분위기를 파악해 집중과 몰입에 도움되는 음악을 큐레이션합니다.</div>", unsafe_allow_html=True)
with right:
    st.metric("버전", "v1.0")
    st.metric("플레이리스트 수", len(PLAYLISTS))

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- 입력 처리 ----------
if not title:
    st.info("⬅️ 왼쪽 사이드바에 도서 제목을 입력한 뒤 시작하세요.")
    st.stop()

# 책 정보 가져오기
book = {"title": title, "author": author, "subjects": [], "cover_url": "", "description": ""}
source_note = "사용자 입력"

if mode == "Open Library에서 자동 탐색":
    with st.spinner("Open Library에서 책 정보를 가져오는 중..."):
        fetched = fetch_openlibrary(title, author)
        # 가져온 값이 의미 있으면 대체
        if fetched.get("title"):
            book.update(fetched)
            source_note = "Open Library"

# 사용자 태그 반영
extra_tags = [g for g in user_genre]
book_subjects = [s for s in book.get("subjects", [])]

# 분위기 추론
candidates = infer_moods(book.get("title", ""), book_subjects, extra_tags)

# 플랫폼 선호 필터
def filter_by_platform(cands: List[Tuple[str, str]], prefer: str) -> List[Tuple[str, str]]:
    if prefer == "상관없음":
        return cands
    want = "youtube" if prefer.lower().startswith("you") else "spotify"
    kept = [(k, r) for k, r in cands if PLAYLISTS.get(k, {}).get("platform") == want]
    return kept or cands  # 없으면 원본 유지

candidates = filter_by_platform(candidates, prefer)

# 상단: 책 카드
c1, c2 = st.columns([.25, .75])
with c1:
    cover = book.get("cover_url")
    if cover:
        st.image(cover, caption="Book Cover", use_column_width=True)
    else:
        st.image("https://placehold.co/400x600?text=No+Cover", caption="Book Cover", use_column_width=True)

with c2:
    st.markdown(
        f"""
        <div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
              <div>
                <div style='font-size:1.25rem;font-weight:800;margin-bottom:4px'>{book.get('title','')}</div>
                <div style='color:#6b7280;margin-bottom:8px'>{book.get('author','')}</div>
                <span class='pill'>{source_note}</span>
            </div>
            </div>
            <div style='margin-top:12px;color:#111827'>{book.get('description','')[:360] + ('…' if len(book.get('description',''))>360 else '')}</div>
            <div style='margin-top:10px'>
                {''.join([f"<span class='pill' style='background:#e5e7eb;color:#111827'>{s}</span>" for s in (book_subjects[:6])])}
                {''.join([f"<span class='pill'>{t}</span>" for t in extra_tags])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# 추천 결과
st.subheader("추천 플레이리스트")

if not candidates:
    st.warning("플레이리스트 후보를 찾지 못했습니다. 태그를 추가해보세요.")
    st.stop()

# 최대 max_recs까지 출력
reasons_out = []
for idx, (mood_key, reason) in enumerate(candidates[:max_recs], start=1):
    pl = PLAYLISTS[mood_key]
    col1, col2 = st.columns([.45, .55])
    with col1:
        st.markdown(
            f"""
            <div class='playlist-card'>
              <div style='font-size:1.1rem;font-weight:800;margin-bottom:6px'>{idx}. {pl['name']}</div>
              <div class='source'>플랫폼: {pl['platform'].title()} · 태그: {', '.join(pl['tags'])}</div>
              <div style='margin-top:8px'><code>{pl['url']}</code></div>
              <div style='margin-top:8px;color:#111827'>{reason or '일반 독서에 적합'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        embed_player(pl["platform"], pl["url"], height=352)
    reasons_out.append({"playlist": pl["name"], "mood_key": mood_key, "reason": reason})

# 설명/근거 박스
with st.expander("🔎 추천 근거 자세히 보기"):
    st.write("키워드 매칭과 규칙 기반으로 분위기를 판별했습니다.")
    st.json(reasons_out)

# 결과 내보내기 & 히스토리
result_payload = {
    "book": book,
    "tags": extra_tags,
    "recommendations": [
        {
            "name": PLAYLISTS[k]["name"],
            "platform": PLAYLISTS[k]["platform"],
            "url": PLAYLISTS[k]["url"],
            "reason": r,
        }
        for k, r in candidates[:max_recs]
    ],
}

st.download_button(
    label="결과 JSON 다운로드",
    data=json.dumps(result_payload, ensure_ascii=False, indent=2),
    file_name="book_music_recommendation.json",
    mime="application/json",
)

if "history" not in st.session_state:
    st.session_state["history"] = []

if st.button("이번 추천을 히스토리에 저장"):
    st.session_state["history"].append(result_payload)
    st.success("히스토리에 저장되었습니다.")

if st.session_state["history"]:
    with st.expander("🗂️ 히스토리 보기"):
        for i, item in enumerate(reversed(st.session_state["history"])):
            st.write(f"**{i+1}.** {item['book'].get('title','')} → {', '.join([rec['name'] for rec in item['recommendations']])}")

# 푸터
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='footer-note'>Tip: 결과가 마음에 들지 않으면 사이드바에서 '장르/키워드 추가 태그'를 바꿔보세요. 직접 플레이리스트 카탈로그를 편집해도 됩니다. (코드 상단 PLAYLISTS 변수)</div>",
    unsafe_allow_html=True,
)
