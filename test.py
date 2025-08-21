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
    generate_btn = st.button("🪄 계획 생성/재생성")

# ---------- 데이터 전처리 ----------
subjects_df = subjects_df.dropna(subset=["Subject"]).copy()
subjects_df["Subject"] = subjects_df["Subject"].str.strip()
subjects_df = subjects_df[subjects_df["Subject"] != ""]
if subjects_df.empty:
    st.warning("사이드바에서 과목을 입력하세요.")
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
    st.error("가용 시간이 0입니다. 설정을 조정하세요(휴식 요일/주말 가중치/하루 공부 시간).")
    st.stop()

# ---------- 총 목표시간 확정 ----------
subjects = subjects_df.copy()
# 빈 TargetHours는 우선순위 비율로 자동 배분
auto_mask = ~has_target
manual_total = subjects.loc[~auto_mask, "TargetHours"].sum()
remaining_capacity = max(cal_df["AvailHours"].sum() - manual_total, 0.0)

if auto_mask.any():
    pr = subjects.loc[auto_mask, "Priority(1-5)"].astype(float)
    pr_sum = pr.sum()
    if pr_sum <= 0:
        # 우선순위가 모두 0/NaN이면 균등 분배
        alloc = np.repeat(remaining_capacity / auto_mask.sum(), auto_mask.sum())
    else:
        alloc = remaining_capacity * (pr / pr_sum).values
    subjects.loc[auto_mask, "TargetHours"] = alloc

# 최소 세션 단위 반영하여 반올림
subjects["TargetHours"] = subjects["TargetHours"].astype(float).apply(lambda x: float(round_to_step(max(x,0.0), min_step)))

# 목표가 0인 과목 제거
subjects = subjects[subjects["TargetHours"] > 0].reset_index(drop=True)
if subjects.empty:
    st.error("목표 시간이 0인 과목만 있습니다. TargetHours 또는 우선순위를 설정하세요.")
    st.stop()

# ---------- 스케줄링 알고리즘 ----------
# 남은 목표시간을 비례 배분하면서, 하루 가용시간을 채우고, 최소 세션 단위로 자름
np.random.seed(seed)
plan_rows = []
remaining = subjects[["Subject","TargetHours","MinSession(hrs)"]].set_index("Subject").to_dict(orient="index")

for _, row in cal_df.iterrows():
    day = row["Date"]
    capacity = float(row["AvailHours"])
    if capacity <= 0:
        continue

    # 남은 시간이 있는 과목만 대상으로
    def remaining_total():
        return sum(v["TargetHours"] for v in remaining.values())

    # 랜덤 셔플로 일일 다양성
    subject_order = list(remaining.keys())
    np.random.shuffle(subject_order)

    # 반복적으로 하루 용량 소진
    safety = 0
    while capacity > 0 and remaining_total() > 0 and safety < 1000:
        safety += 1
        # 비례 배분: 남은 비율대로 이번 라운드 목표량 제안
        total_rem = remaining_total()
        if total_rem == 0:
            break

        # 라운드 크기: 최소 세션 평균
        avg_min = np.mean([remaining[s]["MinSession(hrs)"] for s in subject_order if remaining[s]["TargetHours"] > 0]) if subject_order else min_step
        round_chunk = min(capacity, max(min_step, avg_min))

        for s in list(subject_order):
            rem_s = remaining[s]["TargetHours"]
            if rem_s <= 0 or capacity <= 0:
                continue

            share = round_chunk * (rem_s / total_rem)
            # 최소 세션 보장
            share = max(share, remaining[s]["MinSession(hrs)"])
            share = min(share, rem_s, capacity)
            share = float(round_to_step(share, min_step))
            if share <= 0:
                continue

            plan_rows.append({"Date": day, "Subject": s, "Hours": share})
            remaining[s]["TargetHours"] = float(round_to_step(remaining[s]["TargetHours"] - share, min_step))
            capacity = float(round_to_step(capacity - share, min_step))

        # 남은 과목 재정렬(랜덤)로 편향 방지
        np.random.shuffle(subject_order)

# 계획표 생성
plan_df = pd.DataFrame(plan_rows)
if plan_df.empty:
    st.warning("생성된 일정이 없습니다. 설정을 조정해보세요.")
    st.stop()

# 일자별 총합이 가용시간을 살짝 못 채울 수 있어 보정(소수 반올림 영향)
daily_sum = plan_df.groupby("Date")["Hours"].sum().reset_index().rename(columns={"Hours":"Planned"})
merged = cal_df.merge(daily_sum, on="Date", how="left").fillna({"Planned":0.0})
# (가볍게) 남는 용량을 가장 많이 남은 과목에 추가 분배
for _, r in merged.iterrows():
    gap = float(round_to_step(r["AvailHours"] - r["Planned"], min_step))
    if gap <= 0:
        continue
    dmask = plan_df["Date"] == r["Date"]
    # 해당 날짜에 이미 등장한 과목들 중 남은 목표가 큰 순
    remain_series = pd.Series({k: v["TargetHours"] for k,v in remaining.items()})
    if remain_series.sum() <= 0:
        break
    top_subject = remain_series.sort_values(ascending=False).index[0]
    # 날짜에 그 과목이 없으면 새로 추가
    if not ((plan_df["Date"]==r["Date"]) & (plan_df["Subject"]==top_subject)).any():
        plan_df = pd.concat([plan_df, pd.DataFrame([{"Date": r["Date"], "Subject": top_subject, "Hours": float(min(gap, max(remaining[top_subject]["MinSession(hrs)"], min_step)))}])], ignore_index=True)
        remaining[top_subject]["TargetHours"] = float(round_to_step(remaining[top_subject]["TargetHours"] - plan_df.tail(1)["Hours"].iloc[0], min_step))
    else:
        # 해당 날짜 해당 과목에 추가
        idxs = plan_df.index[(plan_df["Date"]==r["Date"]) & (plan_df["Subject"]==top_subject)].tolist()
        if idxs:
            addh = float(round_to_step(min(gap, max(remaining[top_subject]["MinSession(hrs)"], min_step), remaining[top_subject]["TargetHours"]), min_step))
            if addh > 0:
                plan_df.loc[idxs[0],"Hours"] = float(round_to_step(plan_df.loc[idxs[0],"Hours"] + addh, min_step))
                remaining[top_subject]["TargetHours"] = float(round_to_step(remaining[top_subject]["TargetHours"] - addh, min_step))

plan_df = plan_df.sort_values(["Date","Subject"]).reset_index(drop=True)

# ---------- 세션 상태(체크박스) ----------
if "done" not in st.session_state:
    st.session_state.done = set()

def key_for(row):
    return f"{row['Date']}_{row['Subject']}"

# 오늘 할 일 뷰
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
            new_val = st.checkbox(f"{r['Subject']} — {r['Hours']:.2f}시간", value=checked, key=f"chk_{k}")
            if new_val and not checked:
                st.session_state.done.add(k)
            elif not new_val and checked:
                st.session_state.done.discard(k)

    # 진행률
    plan_df["Key"] = plan_df.apply(key_for, axis=1)
    completed_hours = plan_df[plan_df["Key"].isin(st.session_state.done)]["Hours"].sum()
    total_hours = plan_df["Hours"].sum()
    prog = 0.0 if total_hours == 0 else completed_hours / total_hours
    st.progress(min(prog,1.0), text=f"전체 진행률: {completed_hours:.2f} / {total_hours:.2f} 시간")

    if st.button("✅ 완료한 분량 기준으로 남은 계획 재계산(다음 실행 때 반영)"):
        # 완료된 세션을 목표시간에서 제외하고 재생성 유도
        for k in list(st.session_state.done):
            d_s = k.split("_", 1)
            if len(d_s) == 2:
                # 여기서는 단순히 버튼 안내용. 실제 재계산은 상단 '계획 생성/재생성' 눌러주세요.
                pass
        st.info("상단 사이드바의 **'계획 생성/재생성'** 버튼을 눌러 남은 분량 기준으로 다시 배분하세요.")

with right:
    st.subheader("요약")
    # 과목별 총 시간
    subj_summary = plan_df.groupby("Subject")["Hours"].sum().reset_index().sort_values("Hours", ascending=False)
    fig_pie = px.pie(subj_summary, names="Subject", values="Hours", title="과목별 총 공부시간 비율")
    st.plotly_chart(fig_pie, use_container_width=True)

    # 일자별 스택 바
    daily_subject = plan_df.pivot_table(index="Date", columns="Subject", values="Hours", aggfunc="sum").fillna(0.0)
    daily_subject = daily_subject.sort_index()
    fig_bar = px.bar(daily_subject, title="일자별 과목 스택 바(계획)", barmode="stack")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ---------- 상세 표 & 내보내기 ----------
st.subheader("📅 일자별 상세 계획표")
plan_pretty = plan_df.copy()
plan_pretty["Date"] = plan_pretty["Date"].astype(str)
st.dataframe(plan_pretty, use_container_width=True, hide_index=True)

csv = plan_pretty.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ 계획 CSV 다운로드", data=csv, file_name="study_plan.csv", mime="text/csv")

# ---------- 정보/도움말 ----------
with st.expander("ℹ️ 사용 팁"):
    st.markdown(
        """
- **TargetHours**를 비워두면 **우선순위(1-5)** 비율로 남은 전체 용량을 자동 배분합니다.  
- **MinSession(hrs)**는 해당 과목의 최소 공부 세션 단위(예: 0.5시간)입니다.  
- **주말 가중치**와 **휴식 요일**로 현실적인 스케줄을 만들 수 있어요.  
- 오늘 체크박스를 사용하면 **진행률**이 업데이트됩니다.  
- 계획을 바꾸고 싶다면 사이드바 설정을 조정한 뒤 **'계획 생성/재생성'** 버튼을 누르세요.
"""
    )

# ---------- 최종 안내 ----------
if generate_btn:
    st.experimental_rerun()
