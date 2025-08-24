import streamlit as st
import pandas as pd
import datetime

st.title("📚 스터디 플래너 생성기")

# 시험 기간 입력
st.subheader("시험 기간 설정")
start_date = st.date_input("시험 시작일")
end_date = st.date_input("시험 종료일")

# 기본 과목
st.subheader("과목 및 시험 범위 입력")
subjects = {"국어": "", "영어": "", "수학": ""}

# 사용자 과목 추가
extra_subjects = st.text_area("추가 과목 입력 (콤마로 구분, 예: 역사, 과학, 기술가정)")
if extra_subjects:
    for sub in [s.strip() for s in extra_subjects.split(",") if s.strip()]:
        subjects[sub] = ""

# 과목별 시험 범위 입력
for subject in subjects.keys():
    subjects[subject] = st.text_input(f"{subject} 시험 범위 입력 (예: 1~3단원)")

# 평일/주말 순공시간 입력
st.subheader("공부 가능 시간 입력")
weekday_hours = st.number_input("평일 순공 시간 (시간)", min_value=1, max_value=12, value=3)
weekend_hours = st.number_input("주말 순공 시간 (시간)", min_value=1, max_value=12, value=6)

# 계획 생성 버튼
if st.button("스터디 플래너 생성하기"):
    if start_date >= end_date:
        st.error("⚠️ 시험 시작일은 종료일보다 앞서야 합니다.")
    else:
        # 기간 생성
        dates = pd.date_range(start_date, end_date)
        plan = []

        # 과목 리스트
        subject_list = list(subjects.keys())
        total_days = len(dates)
        total_subjects = len(subject_list)

        # 날짜별 계획 배분
        for i, d in enumerate(dates):
            day_name = d.strftime("%A")
            # 평일/주말 공부시간 구분
            study_hours = weekend_hours if day_name in ["Saturday", "Sunday"] else weekday_hours

            # 과목 분배
            today_subjects = []
            for j in range(total_subjects):
                subj = subject_list[(i + j) % total_subjects]
                today_subjects.append(subj)

            # 오늘 계획 저장
            plan.append({
                "날짜": d.strftime("%Y-%m-%d (%a)"),
                "총 공부시간": f"{study_hours}시간",
                "공부할 과목": ", ".join(today_subjects)
            })

        df = pd.DataFrame(plan)
        st.subheader("📅 생성된 스터디 플래너")
        st.dataframe(df)

        # 다운로드 버튼
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("CSV 파일 다운로드", data=csv, file_name="study_plan.csv", mime="text/csv")
