# mbti_travel.py
# 🌏 MBTI 유형별 여행 추천 웹 (지도 + 일정 자동 생성)
# pip install streamlit folium streamlit-folium pandas

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import date, timedelta
import random
import io

st.set_page_config(page_title="MBTI 여행 추천", page_icon="🌏", layout="wide")

# -----------------------------
# 데이터: 16개 MBTI 유형별 추천
# 각 목적지는 (도시, 나라, 위도, 경도)
# -----------------------------
DATA = {
    "INTJ": {
        "style": "조용하고 깊이 있는 문화 탐방",
        "description": "깊이 있는 역사·건축·서점·박물관을 사랑하는 INTJ에게 잘 맞는 여행.",
        "destinations": [
            ("교토", "일본", 35.0116, 135.7681),
            ("프라하", "체코", 50.0755, 14.4378),
            ("피렌체", "이탈리아", 43.7696, 11.2558),
        ],
        "activities": [
            "현지 서점·전통 찻집에서 사색",
            "건축 투어 및 박물관 관람",
            "한적한 골목 사진 산책",
            "사원/성당의 아침 방문",
            "클래식 공연 감상",
        ],
    },
    "INTP": {
        "style": "지적 호기심 충족, 차분한 도시 산책",
        "description": "학문과 과학, 사색의 리듬을 유지할 수 있는 곳 위주.",
        "destinations": [
            ("탈린", "에스토니아", 59.4370, 24.7536),
            ("케임브리지", "영국", 52.2053, 0.1218),
            ("취리히", "스위스", 47.3769, 8.5417),
        ],
        "activities": [
            "대학 캠퍼스/박물관 탐방",
            "과학·기술 전시 관람",
            "강변 산책과 스케치",
            "현지 카페에서 독서",
            "현지 도서관·아카이브 체험",
        ],
    },
    "ENTJ": {
        "style": "효율적인 도시 정복, 비즈·모던 컬처",
        "description": "대도시의 속도감, 랜드마크와 미식, 깔끔한 동선.",
        "destinations": [
            ("싱가포르", "싱가포르", 1.3521, 103.8198),
            ("뉴욕", "미국", 40.7128, -74.0060),
            ("베를린", "독일", 52.5200, 13.4050),
        ],
        "activities": [
            "주요 랜드마크 전광석화 투어",
            "루프탑/미쉐린 미식",
            "현대미술관·전시 관람",
            "야경 스카이라인 감상",
            "효율 루트 지하철 마스터",
        ],
    },
    "ENTP": {
        "style": "새로움·아이디어 폭발, 트렌디 실험",
        "description": "변화를 즐기며 신박한 체험과 대화가 많은 동선.",
        "destinations": [
            ("도쿄", "일본", 35.6762, 139.6503),
            ("텔아비브", "이스라엘", 32.0853, 34.7818),
            ("샌프란시스코", "미국", 37.7749, -122.4194),
        ],
        "activities": [
            "스타트업 거리/메이커스페이스 방문",
            "이색 테마 카페 투어",
            "언더그라운드 전시/공연",
            "골목 상점 탐험",
            "현지인 토론 모임·밋업",
        ],
    },
    "INFJ": {
        "style": "영감을 주는 고요함, 풍경·사색",
        "description": "평화로운 풍경과 깊은 이야기의 여정.",
        "destinations": [
            ("산토리니", "그리스", 36.3932, 25.4615),
            ("레이캬비크", "아이슬란드", 64.1466, -21.9426),
            ("블레드호", "슬로베니아", 46.3692, 14.1136),
        ],
        "activities": [
            "일출/일몰 명소 사색",
            "자연 속 명상 산책",
            "현지 예술가 갤러리 방문",
            "온천/스파 힐링",
            "작은 마을 책방 찾기",
        ],
    },
    "INFP": {
        "style": "감성 충만 스토리 여행",
        "description": "문학·감성 카페·골목 이야기로 채우는 루트.",
        "destinations": [
            ("에든버러", "영국", 55.9533, -3.1883),
            ("류블랴나", "슬로베니아", 46.0569, 14.5058),
            ("치앙마이", "태국", 18.7883, 98.9853),
        ],
        "activities": [
            "문학 명소·중고서점 투어",
            "수공예 워크숍 체험",
            "현지 카페·디저트 성지순례",
            "골목 사진 산책",
            "자선 마켓/커뮤니티 방문",
        ],
    },
    "ENFJ": {
        "style": "사람 중심, 따뜻한 도시 경험",
        "description": "커뮤니티·공공공간·로컬 스토리가 풍부한 곳.",
        "destinations": [
            ("서울", "대한민국", 37.5665, 126.9780),
            ("밴쿠버", "캐나다", 49.2827, -123.1207),
            ("코펜하겐", "덴마크", 55.6761, 12.5683),
        ],
        "activities": [
            "로컬 마켓·플리마켓 탐방",
            "커뮤니티 센터 프로그램 참여",
            "도시 공원 피크닉",
            "사회적기업 카페 방문",
            "디자인/건축 투어",
        ],
    },
    "ENFP": {
        "style": "활발한 체험 + 다문화 교류",
        "description": "자유로운 에너지와 축제, 거리의 컬러.",
        "destinations": [
            ("바르셀로나", "스페인", 41.3851, 2.1734),
            ("방콕", "태국", 13.7563, 100.5018),
            ("리우데자네이루", "브라질", -22.9068, -43.1729),
        ],
        "activities": [
            "길거리 공연/축제 즐기기",
            "현지 요리 클래스",
            "자유 일정으로 골목 탐험",
            "비치/루프탑 라운지",
            "현지 친구 사귀기 미션",
        ],
    },
    "ISTJ": {
        "style": "질서정연한 클래식 여행",
        "description": "정확한 동선·시간표·클래식 명소 중심.",
        "destinations": [
            ("빈", "오스트리아", 48.2082, 16.3738),
            ("뮌헨", "독일", 48.1351, 11.5820),
            ("코펜하겐", "덴마크", 55.6761, 12.5683),
        ],
        "activities": [
            "정시 출발 시티투어",
            "고전 음악회 감상",
            "왕궁/궁전 견학",
            "전통 레스토랑 예약 식사",
            "유명 박물관 라인업",
        ],
    },
    "ISFJ": {
        "style": "아늑·정갈, 동화 같은 도시",
        "description": "안정감과 따뜻한 풍경, 소박한 감동.",
        "destinations": [
            ("브뤼헤", "벨기에", 51.2093, 3.2247),
            ("잘츠부르크", "오스트리아", 47.8095, 13.0550),
            ("퀘벡시티", "캐나다", 46.8139, -71.2080),
        ],
        "activities": [
            "마차/운하 보트 체험",
            "크리스마스/시즌 마켓",
            "현지 가정식/비스트로",
            "작은 박물관·공방 방문",
            "한적한 공원 산책",
        ],
    },
    "ESTJ": {
        "style": "탄탄한 랜드마크 중심 대도시",
        "description": "정리된 체크리스트로 핵심만 꽉.",
        "destinations": [
            ("런던", "영국", 51.5074, -0.1278),
            ("홍콩", "홍콩", 22.3193, 114.1694),
            ("시카고", "미국", 41.8781, -87.6298),
        ],
        "activities": [
            "필수 랜드마크 체크",
            "강력 미식 스폿 예약",
            "뮤지컬/콘서트 관람",
            "리버 크루즈",
            "스카이덱·전망대",
        ],
    },
    "ESFJ": {
        "style": "사교적·따뜻한 휴식형 도시",
        "description": "친화력 높고 편의 좋은 곳에서 여유롭게.",
        "destinations": [
            ("파리", "프랑스", 48.8566, 2.3522),
            ("시드니", "호주", -33.8688, 151.2093),
            ("타이베이", "대만", 25.0330, 121.5654),
        ],
        "activities": [
            "브런치 카페·마카롱 투어",
            "아이코닉 포토스팟",
            "강변/해변 산책",
            "플리마켓·백화점 쇼핑",
            "야간 라이트업 명소",
        ],
    },
    "ISTP": {
        "style": "자연·액티비티 중심",
        "description": "야외활동과 도전, 드라이브 루트.",
        "destinations": [
            ("퀸스타운", "뉴질랜드", -45.0312, 168.6626),
            ("인터라켄", "스위스", 46.6863, 7.8632),
            ("트롬쇠", "노르웨이", 69.6492, 18.9553),
        ],
        "activities": [
            "하이킹/패러글라이딩",
            "빙하·호수 투어",
            "오로라/별 보기",
            "자전거/카약",
            "산악 열차 타기",
        ],
    },
    "ISFP": {
        "style": "예술감성·자연 치료",
        "description": "자연과 예술이 공존하는 여유로운 코스.",
        "destinations": [
            ("우붓", "인도네시아 발리", -8.5069, 115.2625),
            ("리스본", "포르투갈", 38.7223, -9.1393),
            ("호이안", "베트남", 15.8801, 108.3380),
        ],
        "activities": [
            "요가/명상 리트릿",
            "현지 공예 워크숍",
            "해변 일몰 감상",
            "소규모 라이브 공연",
            "전통시장 미식",
        ],
    },
    "ESTP": {
        "style": "스릴·놀이·이벤트",
        "description": "짜릿한 액티비티와 야간 엔터테인먼트.",
        "destinations": [
            ("라스베이거스", "미국", 36.1699, -115.1398),
            ("두바이", "아랍에미리트", 25.2048, 55.2708),
            ("칸쿤", "멕시코", 21.1619, -86.8515),
        ],
        "activities": [
            "테마파크/쇼 관람",
            "사막 사파리/샌드보딩",
            "요트/스노클링",
            "루프탑·클럽",
            "슈퍼카 체험",
        ],
    },
    "ESFP": {
        "style": "축제·비치·포토 스팟",
        "description": "화려하고 재밌는 순간 수집가를 위한 코스.",
        "destinations": [
            ("마이애미", "미국", 25.7617, -80.1918),
            ("이비자", "스페인", 38.9067, 1.4206),
            ("푸켓", "태국", 7.8804, 98.3923),
        ],
        "activities": [
            "해변 액티비티",
            "선셋 크루즈",
            "나이트 라이프",
            "인생샷 스팟 투어",
            "해산물 미식",
        ],
    },
}

# 대표 이미지 (저작권 안전을 위해 위키미디어/도시 아이콘 느낌의 공개 이미지 URL 사용 권장)
DEFAULT_IMAGES = {
    "교토": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Kiyomizu-dera_in_Kyoto.jpg",
    "프라하": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Prague_old_town_square_panorama.jpg",
    "피렌체": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Florence_Duomo_III.jpg",
    "바르셀로나": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Sagrada_Familia_01.jpg",
    "방콕": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Bangkok_Montage_2021.jpg",
    "리우데자네이루": "https://upload.wikimedia.org/wikipedia/commons/1/19/Rio_de_Janeiro_-_Rafael_Defavari.jpg",
    # 필요 시 더 추가 가능
}

# -----------------------------
# 유틸 함수
# -----------------------------
def get_all_mbti():
    return sorted(DATA.keys())

def build_map(destinations):
    # 중심을 첫 목적지로
    center_lat = destinations[0][2]
    center_lon = destinations[0][3]
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=4, tiles="CartoDB positron")
    coords = []
    for city, country, lat, lon in destinations:
        folium.Marker(
            [lat, lon],
            popup=f"{city}, {country}",
            tooltip=f"{city}",
        ).add_to(fmap)
        coords.append((lat, lon))
    # 경로 폴리라인
    if len(coords) > 1:
        folium.PolyLine(coords, weight=3, opacity=0.7).add_to(fmap)
    return fmap

def sample_destinations(mbti, count=2):
    lst = DATA[mbti]["destinations"]
    if count >= len(lst):
        return lst
    return random.sample(lst, count)

def generate_itinerary(mbti, days, base_date, selected_destinations):
    acts = DATA[mbti]["activities"]
    style = DATA[mbti]["style"]
    rows = []
    for i in range(days):
        day_date = base_date + timedelta(days=i)
        # 목적지는 순환 배정
        city, country, lat, lon = selected_destinations[i % len(selected_destinations)]
        # 활동은 랜덤 3개 뽑기 (아침/낮/저녁)
        day_acts = random.sample(acts, k=min(3, len(acts)))
        morning = f"[아침] {day_acts[0]}"
        afternoon = f"[오후] {day_acts[1] if len(day_acts)>1 else '자유 일정'}"
        evening = f"[저녁] {day_acts[2] if len(day_acts)>2 else '야경 산책'}"
        meals = "현지 음식 맛보기(로컬 식당/마켓)"
        rows.append({
            "일자": day_date.strftime("%Y-%m-%d"),
            "MBTI 스타일": style,
            "도시": city,
            "국가": country,
            "아침": morning,
            "오후": afternoon,
            "저녁": evening,
            "식사": meals
        })
    return pd.DataFrame(rows)

def df_to_markdown(df: pd.DataFrame) -> str:
    # 간단한 마크다운 일정표
    lines = ["# 여행 일정표", ""]
    for _, r in df.iterrows():
        lines += [
            f"## {r['일자']} · {r['도시']} ({r['국가']})",
            f"- {r['아침']}",
            f"- {r['오후']}",
            f"- {r['저녁']}",
            f"- 🍽 {r['식사']}",
            ""
        ]
    return "\n".join(lines)

# -----------------------------
# 사이드바: 입력
# -----------------------------
with st.sidebar:
    st.header("✈️ 여행 설정")
    mbti = st.selectbox("MBTI 선택", get_all_mbti(), index=get_all_mbti().index("ENFP") if "ENFP" in get_all_mbti() else 0)
    st.caption(DATA[mbti]["description"])
    day_count = st.slider("여행 일수", min_value=3, max_value=10, value=5, step=1)
    dest_count = st.slider("추천 도시 수(경로 표시)", min_value=1, max_value=3, value=2, step=1)
    start_date = st.date_input("여행 시작일", value=date.today())
    random_seed = st.number_input("랜덤 시드(재현용)", min_value=0, value=42, step=1)
    st.markdown("---")
    st.write("💡 팁: 시드를 바꾸면 활동 구성이 바뀌어요!")

random.seed(int(random_seed))

# -----------------------------
# 메인: 헤더
# -----------------------------
st.title("🌏 MBTI 유형별 여행 추천")
st.subheader(f"{mbti} · {DATA[mbti]['style']}")

# 추천 도시 선택 & 지도
sel_dests = sample_destinations(mbti, dest_count)

cols = st.columns([1.2, 1])
with cols[0]:
    fmap = build_map(sel_dests)
    st_folium(fmap, height=520, use_container_width=True)
with cols[1]:
    st.markdown("### 📍 추천 도시")
    for (city, country, lat, lon) in sel_dests:
        st.markdown(f"- **{city}**, {country}")
        if city in DEFAULT_IMAGES:
            st.image(DEFAULT_IMAGES[city], use_column_width=True)
    st.info(DATA[mbti]["description"])

# 일정 생성
st.markdown("## 🗓 자동 생성 여행 일정")
it_df = generate_itinerary(mbti, day_count, start_date, sel_dests)
st.dataframe(it_df, use_container_width=True)

# 다운로드 버튼 (CSV / Markdown)
csv_buf = it_df.to_csv(index=False).encode("utf-8-sig")
md_text = df_to_markdown(it_df).encode("utf-8")

dl_cols = st.columns(2)
with dl_cols[0]:
    st.download_button(
        label="⬇️ CSV로 다운로드",
        data=csv_buf,
        file_name=f"{mbti}_여행일정.csv",
        mime="text/csv",
        help="엑셀에서 열 수 있어요"
    )
with dl_cols[1]:
    st.download_button(
        label="⬇️ Markdown으로 다운로드",
        data=md_text,
        file_name=f"{mbti}_여행일정.md",
        mime="text/markdown",
        help="노션/깃허브 등에 붙여넣기 좋아요"
    )

# 추가 안내
with st.expander("🔧 커스터마이즈 가이드"):
    st.markdown("""
- **도시/활동**을 더 추가하려면 `DATA` 딕셔너리의 `destinations`, `activities`를 수정하세요.
- **지도의 스타일**은 `build_map()`의 `tiles` 값으로 변경할 수 있어요. (예: "OpenStreetMap", "Stamen Terrain")
- **일정 로직**은 `generate_itinerary()`에서 아침/오후/저녁 블록을 커스터마이즈하면 됩니다.
- **이미지**는 `DEFAULT_IMAGES`에 도시명 키로 URL을 추가하세요.
""")
