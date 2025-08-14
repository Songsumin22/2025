import streamlit as st
import pandas as pd
from datetime import date, timedelta
import random

# folium이 없으면 pydeck으로 대체
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ModuleNotFoundError:
    import pydeck as pdk
    FOLIUM_AVAILABLE = False

# ---------------- 스타일 ----------------
st.set_page_config(page_title="🌏 MBTI 여행 추천", page_icon="✈️", layout="wide")

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
        color: white;
    }
    .stApp {
        background: transparent;
    }
    .travel-card {
        padding: 20px;
        border-radius: 15px;
        background-color: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        box-shadow: 0px 4px 20px rgba(0,0,0,0.2);
    }
    h1, h2, h3 {
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- 여행 추천 데이터 ----------------
travel_recommendations = {
    "INTJ": {
        "style": "조용하고 깊이 있는 문화 탐방",
        "destinations": [("교토", "일본", 35.0116, 135.7681),
                         ("프라하", "체코", 50.0755, 14.4378),
                         ("피렌체", "이탈리아", 43.7699, 11.2556)],
        "description": "역사와 건축물, 조용한 골목길을 좋아하는 INTJ에게 어울립니다.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/6/6e/Kiyomizu-dera_in_Kyoto.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/c/c6/Prague_skyline.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/f/f1/Florence_duomo.jpg"
        ]
    },
    "ENFP": {
        "style": "활발하고 다양한 체험 중심",
        "destinations": [("바르셀로나", "스페인", 41.3851, 2.1734),
                         ("방콕", "태국", 13.7563, 100.5018),
                         ("리우데자네이루", "브라질", -22.9068, -43.1729)],
        "description": "다양한 사람과 문화를 경험하며 자유롭게 즐길 수 있는 여행지입니다.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/4/4e/Barcelona_skyline.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/4/4b/Wat_Arun_Bangkok.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/4/44/Rio_de_Janeiro_view.jpg"
        ]
    },
    # 나머지 MBTI 유형도 같은 형식으로 16개 채움...
}

# ---------------- 지도 생성 함수 ----------------
def build_map_folium(destinations):
    center_lat, center_lon = destinations[0][2], destinations[0][3]
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=4, tiles="CartoDB positron")
    coords = []
    for city, country, lat, lon in destinations:
        folium.Marker([lat, lon], popup=f"{city}, {country}", tooltip=city).add_to(fmap)
        coords.append((lat, lon))
    if len(coords) > 1:
        folium.PolyLine(coords, weight=3, opacity=0.7).add_to(fmap)
    return fmap

def build_map_pydeck(destinations):
    points = [{"lat": lat, "lon": lon, "name": city, "country": country}
              for (city, country, lat, lon) in destinations]
    path = [{"path": [[d[3], d[2]] for d in destinations]}] if len(destinations) > 1 else []
    view_state = pdk.ViewState(latitude=destinations[0][2], longitude=destinations[0][3], zoom=4)

    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=points,
            get_position="[lon, lat]",
            get_radius=40000,
            pickable=True,
        )
    ]
    if path:
        layers.append(
            pdk.Layer(
                "PathLayer",
                data=path,
                get_path="path",
                width_scale=2,
                width_min_pixels=2,
            )
        )

    deck = pdk.Deck(layers=layers, initial_view_state=view_state, tooltip={"text": "{name}, {country}"})
    return deck

# ---------------- 일정 생성 함수 ----------------
def generate_itinerary(destinations):
    start_date = date.today()
    itinerary = []
    for i, (city, country, lat, lon) in enumerate(destinations, start=1):
        day = start_date + timedelta(days=i-1)
        activities = random.sample([
            "현지 시장 탐방", "유명 관광지 방문", "전통 음식 체험", "자연 경관 감상",
            "사진 촬영", "현지 박물관 방문", "해변에서 휴식", "트래킹 또는 하이킹"
        ], 3)
        itinerary.append({"날짜": day.strftime("%Y-%m-%d"),
                          "도시": city,
                          "나라": country,
                          "활동": ", ".join(activities)})
    return pd.DataFrame(itinerary)

# ---------------- 메인 UI ----------------
st.title("🌏 MBTI 여행 추천")
st.markdown("당신의 MBTI에 맞는 완벽한 여행지를 찾아드립니다! ✈️")

mbti_choice = st.selectbox("MBTI를 선택하세요", list(travel_recommendations.keys()))

if mbti_choice:
    rec = travel_recommendations[mbti_choice]
    st.markdown(f"<div class='travel-card'><h2>✨ 여행 스타일: {rec['style']}</h2><p>{rec['description']}</p></div>", unsafe_allow_html=True)

    # 이미지 갤러리
    st.image(rec["images"], use_column_width=True, caption=[f"{d[0]}, {d[1]}" for d in rec["destinations"]])

    # 지도 출력
    if FOLIUM_AVAILABLE:
        fmap = build_map_folium(rec["destinations"])
        st_folium(fmap, height=500, use_container_width=True)
    else:
        deck = build_map_pydeck(rec["destinations"])
        st.pydeck_chart(deck, use_container_width=True)

    # 여행 일정
    st.subheader("📅 추천 여행 일정")
    st.dataframe(generate_itinerary(rec["destinations"]))
