# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="시험공부 플래너", page_icon="📘", layout="wide")

# ---------- 유틸 ----------
def daterange(start: date, end: date):
    for n in range(int((end - start).days) + 1):
        yield start + timedelta(n)

def round_to_step(x, step):
    return np.round(x / step) * step

def is_weekend(d: date):
    return d.weekday() >= 5  # 5=토, 6=일

def make_default_subjects():
    return pd.DataFrame({
        "Subject": ["국어", "영어", "수학"],
        "TargetHours": [5.0, 7.0, 10.0],
        "Priority(1-5)": [3, 4, 5],
        "MinSession(hrs)": [0.5, 0.5, 0.5],
    })

# ---------- 사이드바 입력 ----------
with st.sidebar:
    st.title("⚙️ 설정")
    today = date.today()
    exam_date = st.date_input("시험 날짜", value=today + timedelta(days=14), min_value=today)
    daily_hours = st.slider("하루 공부 가능 시간(평일)", min_value=1.0, max_value=12.0, value=4.0, step=0.5)
    weekend_factor = st.slider("주말 가중치 (ex. 1.5면 주말에 1.5배 공부)", 0.0, 2.0, 1.2, 0.1)
    min_step = st.select_slider("시간 배분 최소 단위(세션)", options=[0.25, 0.5, 1.0], value=0.5)
    days_off = st.multiselect(
        "반복 휴식 요일(매주)", options=["월","화","수","목","금","토","일"],
        help="선택한 요일은 매주 공부 제외"
    )

    st.markdown("---")
    st.caption("과목/목표시간 입력(빈 TargetHours는 우선순위로 자동 배분)")
    subjects_df = st.data_editor(
        make_default_subjects(),
        key="subjects_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Subject": st.column_config.TextColumn("과목"),
            "TargetHours": st.column_config.NumberColumn("목표시간(시간)", step=0.5, format="%.2f"),
            "Priority(1-5)": st.column_config.NumberColumn("우선순위(1-5)", min_value=1, max_value=5, step=1),
            "MinSession(hrs)": st.column_config.NumberColumn("최소 세션(시간)", step=0.25, format="%.2f"),
        }
    )
    st.markdown("---")
    seed = st.number_input("무작위 분배 시드(재현성)", min_value=0, value=42, step=1)
    generate_btn = st.button("🪄 계획 생성/재계산")

# ---------- 데이터 전처리 ----------
subjects_df = subjects_df.dropna(subset=["Subject"]).copy()
subjects_df["Subject"] = subjects_df["Subject"].str.strip()
subjects_df = subjects_df[subjects_df["Subject"] != ""]
if subjects_df.empty:
    st.warning("사이드바에서 과목을 입력하세요.")
    st.stop()

# 완료한 과목 제외 처리
if "done_subjects" not in st.session_state:
    st.session_state.done_subjects = set()

subjects_df = subjects_df[~subjects_df["Subject"].isin(st.session_state.done_subjects)]

if subjects_df.empty:
    st.success("모든 과목을 완료했습니다! 🎉")
    st.stop()

# 목표시간이 비어있으면 나중에 우선순위로 배분
has_target = subjects_df["TargetHours"].fillna(0) > 0

# ---------- 날짜/가용시간 테이블 ----------
weekday_map = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
days_off_idx = {k for k,v in weekday_map.items() if v in days_off}

calendar = []
for d in daterange(today, exam_date):
    if d.weekday() in days_off_idx:
        avail = 0.0
    else:
        base = daily_hours
        if is_weekend(d):
            base *= weekend_factor
        avail = base
    avail = round_to_step(max(avail, 0.0), min_step)
    calendar.append({"Date": d, "AvailHours": float(avail), "Weekday": weekday_map[d.weekday()]})
cal_df = pd.DataFrame(calendar)
if cal_df["AvailHours"].sum() == 0:
    st.error("가용 시간이 0입니다. 설정을 조정하세요.")
    st.stop()

# ---------- 총 목표시간 확정 ----------
subjects = subjects_df.copy()
auto_mask = ~has_target
manual_total = subjects.loc[~auto_mask, "TargetHours"].sum()
remaining_capacity = max(cal_df["AvailHours"].sum() - manual_total, 0.0)

if auto_mask.any():
    pr = subjects.loc[auto_mask, "Priority(1-5)"].astype(float)
    pr_sum = pr.sum()
    if pr_sum <= 0:
        alloc = np.repeat(remaining_capacity / auto_mask.sum(), auto_mask.sum())
    else:
        alloc = remaining_capacity * (pr / pr_sum).values
    subjects.loc[auto_mask, "TargetHours"] = alloc

subjects["TargetHours"] = subjects["TargetHours"].astype(float).apply(lambda x: float(round_to_step(max(x,0.0), min_step)))
subjects = subjects[subjects["TargetHours"] > 0].reset_index(drop=True)
if subjects.empty:
    st.success("모든 과목을 완료했습니다! 🎉")
    st.stop()

# ---------- 스케줄링 ----------
np.random.seed(seed)
plan_rows = []
remaining = subjects[["Subject","TargetHours","MinSession(hrs)"]].set_index("Subject").to_dict(orient="index")

for _, row in cal_df.iterrows():
    day = row["Date"]
    capacity = float(row["AvailHours"])
    if capacity <= 0:
        continue

    def remaining_total():
        return sum(v["TargetHours"] for v in remaining.values())

    subject_order = list(remaining.keys())
    np.random.shuffle(subject_order)

    safety = 0
    while capacity > 0 and remaining_total() > 0 and safety < 1000:
        safety += 1
        total_rem = remaining_total()
        if total_rem == 0:
            break

        avg_min = np.mean([remaining[s]["MinSession(hrs)"] for s in subject_order if remaining[s]["TargetHours"] > 0]) if subject_order else min_step
        round_chunk = min(capacity, max(min_step, avg_min))

        for s in list(subject_order):
            rem_s = remaining[s]["TargetHours"]
            if rem_s <= 0 or capacity <= 0:
                continue

            share = round_chunk * (rem_s / total_rem)
            share = max(share, remaining[s]["MinSession(hrs)"])
            share = min(share, rem_s, capacity)
            share = float(round_to_step(share, min_step))
            if share <= 0:
                continue

            plan_rows.append({"Date": day, "Subject": s, "Hours": share})
            remaining[s]["TargetHours"] = float(round_to_step(remaining[s]["TargetHours"] - share, min_step))
            capacity = float(round_to_step(capacity - share, min_step))

        np.random.shuffle(subject_order)

plan_df = pd.DataFrame(plan_rows)
if plan_df.empty:
    st.warning("생성된 일정이 없습니다. 설정을 조정해보세요.")
    st.stop()

plan_df = plan_df.sort_values(["Date","Subject"]).reset_index(drop=True)

# ---------- 상태 관리 ----------
if "done" not in st.session_state:
    st.session_state.done = set()

def key_for(row):
    return f"{row['Date']}_{row['Subject']}"

# ---------- 오늘 할 일 ----------
st.title("📘 시험공부 플래너")
left, right = st.columns([1.1, 1])

with left:
    st.subheader("오늘 할 일")
    today_plan = plan_df[plan_df["Date"] == today]
    if today_plan.empty:
        st.info("오늘은 계획이 없어요. (휴식일이거나 시험일까지 남은 시간이 적을 수 있어요)")
    else:
        for i, r in today_plan.iterrows():
            k = key_for(r)
            checked = k in st.session_state.done
            new_val = st.checkbox(
                f"{r['Subject']} — {r['Hours']:.2f}시간",
                value=checked,
                key=f"chk_{k}_{i}"
            )
            if new_val and not checked:
                st.session_state.done.add(k)
            elif not new_val and checked:
                st.session_state.done.discard(k)

    plan_df["Key"] = plan_df.apply(key_for, axis=1)
    completed_hours = plan_df[plan_df["Key"].isin(st.session_state.done)]["Hours"].sum()
    total_hours = plan_df["Hours"].sum()
    prog = 0.0 if total_hours == 0 else completed_hours / total_hours
    st.progress(min(prog,1.0), text=f"전체 진행률: {completed_hours:.2f} / {total_hours:.2f} 시간")

    # ✅ 완료 과목 제외하고 다시 계획 세우기
    done_subjects_today = set(today_plan[today_plan["Key"].isin(st.session_state.done)]["Subject"].unique())
    if st.button("✅ 완료 과목 제외 후 남은 계획 재계산"):
        st.session_state.done_subjects.update(done_subjects_today)
        st.experimental_rerun()

with right:
    st.subheader("요약")
    subj_summary = plan_df.groupby("Subject")["Hours"].sum().reset_index().sort_values("Hours", ascending=False)
    fig_pie = px.pie(subj_summary, names="Subject", values="Hours", title="과목별 총 공부시간 비율")
    st.plotly_chart(fig_pie, use_container_width=True)

    daily_subject = plan_df.pivot_table(index="Date", columns="Subject", values="Hours", aggfunc="sum").fillna(0.0)
    daily_subject = daily_subject.sort_index()
    fig_bar = px.bar(daily_subject, title="일자별 과목 스택 바(계획)", barmode="stack")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ---------- 상세 표 ----------
st.subheader("📅 일자별 상세 계획표")
pivot_table = plan_df.pivot_table(index="Date", columns="Subject", values="Hours", aggfunc="sum").fillna(0.0)
pivot_table["Total"] = pivot_table.sum(axis=1)
pivot_table = pivot_table.sort_index()
pivot_table.index = pivot_table.index.astype(str)

st.dataframe(pivot_table, use_container_width=True)

csv = pivot_table.to_csv(index=True).encode("utf-8-sig")
st.download_button("⬇️ 계획 CSV 다운로드", data=csv, file_name="study_plan.csv", mime="text/csv")

if generate_btn:
    st.experimental_rerun()
