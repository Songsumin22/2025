import streamlit as st
import pandas as pd
import datetime
import re

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
    subjects[subject] = st.text_input(f"{subject} 시험 범위 입력 (예: 1~3단원, 5~7과)")

# 평일/주말 순공시간 입력
st.subheader("공부 가능 시간 입력")
weekday_time = st.time_input("평일 순공 시간", datetime.time(3, 0))  # 기본 3시간
weekend_time = st.time_input("주말 순공 시간", datetime.time(6, 0))  # 기본 6시간

def time_to_minutes(t: datetime.time) -> int:
    """시간 -> 분 단위 변환"""
    return t.hour * 60 + t.minute

weekday_minutes = time_to_minutes(weekday_time)
weekend_minutes = time_to_minutes(weekend_time)

# 시험 범위 파싱 함수
def parse_range(range_str):
    """
    시험 범위를 숫자 범위로 변환
    예: "5~7단원" -> [5,6,7]
        "1~3과"   -> [1,2,3]
    """
    numbers = re.findall(r"\d+", range_str)
    if len(numbers) == 2:
        start, end = map(int, numbers)
        return list(range(start, end+1))
    elif len(numbers) == 1:
        return [int(numbers[0])]
    else:
        return []

# 계획 생성 버튼
if st.button("스터디 플래너 생성하기"):
    if start_date >= end_date:
        st.error("⚠️ 시험 시작일은 종료일보다 앞서야 합니다.")
    else:
        # 날짜 생성
        dates = pd.date_range(start_date, end_date)
        total_days = len(dates)

        # 과목별 단원 분해
        subject_units = {}
        for subj, rng in subjects.items():
            units = parse_range(rng)
            if units:
                subject_units[subj] = units
            else:
                subject_units[subj] = []

        # 전체 단원 개수
        all_units = sum(len(u) for u in subject_units.values())

        if all_units == 0:
            st.error("⚠️ 과목별 시험 범위를 올바르게 입력해주세요. (예: 1~3단원)")
        else:
            # 날짜별 계획 분배
            plan = []
            unit_list = []
            for subj, units in subject_units.items():
                for u in units:
                    unit_list.append(f"{subj} {u}단원")

            # 날짜별 단원 배정
            idx = 0
            for d in dates:
                day_name = d.strftime("%A")
                study_minutes = weekend_minutes if day_name in ["Saturday", "Sunday"] else weekday_minutes
                today_units = []

                # 하루 공부 시간에 따라 몇 개 단원 배정할지 계산 (단순 균등 분배)
                units_per_day = max(1, round(len(unit_list) / total_days))

                for _ in range(units_per_day):
                    if idx < len(unit_list):
                        today_units.append(unit_list[idx])
                        idx += 1

                plan.append({
                    "날짜": d.strftime("%Y-%m-%d (%a)"),
                    "총 공부시간": f"{study_minutes//60}시간 {study_minutes%60}분",
                    "공부할 내용": ", ".join(today_units) if today_units else "-"
                })

            df = pd.DataFrame(plan)

            st.subheader("📅 생성된 스터디 플래너")
            st.dataframe(df)

            # 다운로드 버튼
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 파일 다운로드", data=csv, file_name="study_plan.csv", mime="text/csv")
