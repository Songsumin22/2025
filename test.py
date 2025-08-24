import streamlit as st
import pandas as pd
import altair as alt

st.title("📊 성적대별 추천 교재 시각화 웹앱")

# 과목 선택
subjects = ["수학", "영어", "국어"]
subject = st.selectbox("과목 선택", subjects)

# 성적대 선택
grades = ["상위권 (1~2등급)", "중위권 (3~4등급)", "하위권 (5등급 이하)"]
grade = st.selectbox("성적대 선택", grades)

# 추천 교재 데이터 (대표 교재 사용률 기반)
# 사용률은 0~100으로 임의 설정 (많이 추천될수록 높음)
recommendation_data = {
    "수학": {
        "상위권 (1~2등급)": {"정석":90, "쎈":95, "블랙라벨":80, "한완수":85},
        "중위권 (3~4등급)": {"풍산자/개념원리":85, "쎈+RPM":90, "자이스토리/마더텅":80},
        "하위권 (5등급 이하)": {"개념원리/스타트업":90, "RPM+체크체크":85}
    },
    "영어": {
        "상위권 (1~2등급)": {"천일문 핵심":95, "자이스토리 모의고사":90, "올림포스 기출":85},
        "중위권 (3~4등급)": {"해커스 중급영어":85, "자이스토리 내신편":80, "자이스토리 수능편":75},
        "하위권 (5등급 이하)": {"해커스 기초영어":90, "쉬운 독해 문제":85, "단어장":80}
    },
    "국어": {
        "상위권 (1~2등급)": {"바이블 문학":90, "자이스토리 고전 시가":85, "마더텅 기출":80},
        "중위권 (3~4등급)": {"EBS 수능특강":85, "비상 국어 유형":80, "마더텅 기출":75},
        "하위권 (5등급 이하)": {"비상 국어 기본":90, "마더텅 쉬운 문제집":85, "강의 병행":80}
    }
}

# 선택된 과목과 성적대의 추천 교재
data_dict = recommendation_data.get(subject, {}).get(grade, {})

if data_dict:
    st.subheader(f"{subject} - {grade} 추천 교재 사용률")
    
    # 테이블로 표시
    df = pd.DataFrame(list(data_dict.items()), columns=["교재", "사용률(%)"])
    st.table(df)
    
    # 막대 그래프
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('교재', sort=None),
        y='사용률(%)',
        tooltip=['교재', '사용률(%)']
    ).properties(title=f"{subject} 성적대별 추천 교재 사용률")
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("선택된 과목/성적대에 대한 데이터가 없습니다.")
