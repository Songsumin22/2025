import streamlit as st

# MBTI별 여행 추천 데이터
travel_recommendations = {
    "INTJ": {
        "style": "조용하고 깊이 있는 문화 탐방",
        "destinations": ["교토, 일본", "프라하, 체코", "피렌체, 이탈리아"],
        "description": "깊이 있는 역사와 건축물, 조용한 골목길을 좋아하는 INTJ에게 딱 맞는 여행지입니다.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Kiyomizu-dera_in_Kyoto.jpg"
    },
    "ENFP": {
        "style": "활발하고 다양한 체험 중심",
        "destinations": ["바르셀로나, 스페인", "방콕, 태국", "리우데자네이루, 브라질"],
        "description": "다양한 사람과 문화를 경험하며 자유롭게 즐길 수 있는 여행지를 추천합니다.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Barcelona_skyline.jpg"
    },
    "ISTP": {
        "style": "자연과 액티비티",
        "destinations": ["퀸스타운, 뉴질랜드", "스위스 알프스", "아이슬란드"],
        "description": "아웃도어 활동과 자연 속에서의 자유로움을 즐기는 ISTP에게 어울립니다.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/4/44/Queenstown_New_Zealand.jpg"
    },
    "INFJ": {
        "style": "영감을 주는 조용한 여행",
        "destinations": ["산토리니, 그리스", "레이캬비크, 아이슬란드", "슬로베니아 블레드호"],
        "description": "평화롭고 아름다운 풍경 속에서 사색할 수 있는 여행지를 추천합니다.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/5/56/Santorini_sunset.jpg"
    }
}

# Streamlit 앱 시작
st.title("🌏 MBTI 여행 추천 웹")
st.write("당신의 MBTI에 맞는 완벽한 여행지를 찾아드립니다!")

# MBTI 입력
mbti_list = list(travel_recommendations.keys())
selected_mbti = st.selectbox("당신의 MBTI를 선택하세요", mbti_list)

# 결과 출력
if selected_mbti:
    rec = travel_recommendations[selected_mbti]
    st.subheader(f"✨ 여행 스타일: {rec['style']}")
    st.image(rec["image"], use_column_width=True)
    st.write(f"**추천 도시:** {', '.join(rec['destinations'])}")
    st.write(rec["description"])
