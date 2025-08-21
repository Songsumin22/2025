# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px

st.set_page_config(page_title="시험공부 플래너", page_icon="📘", layout="wide")

# ---------- 유틸 ----------
def daterange(start: date, end: date):
    for n in range(int((end - start).days) + 1):
        yield start + timedelta(n)

def round_to_step(x, step):
    return np.round(x / step) * step

def is_weekend(d: date):
    return d.weekday() >= 5

def make_default_subjects():
    return pd.DataFrame({
        "Subject": ["국어","영어","수학"],
        "TargetMinutes":[300,420,600],
        "Priority(1-5)":[3,4,5],
        "MinSession(min)":[30,30,30],
        "Difficulty":[3,3,3],        # 난이도 1~5
        "RecoveryTime(min)":[5,5,5], # 전환 회복시간 분 단위
    })

# ---------- 사이드바 ----------
with st.sidebar:
    st.title("⚙️ 설정")
    today = date.today()
    exam_date = st.date_input("시험 날짜", value=today+timedelta(days=14), min_value=today)
    daily_hours = st.slider("하루 공부 가능 시간(평일, 시간)",1.0,12.0,4.0,0.5)
    daily_minutes = daily_hours*60
    weekend_factor = st.slider("주말 가중치",0.0,2.0,1.2,0.1)
    min_step = st.select_slider("시간 배분 최소 단위(분)", options=[5,10,15,30], value=5)
    days_off = st.multiselect("반복 휴식 요일(매주)", options=["월","화","수","목","금","토","일"])
    
    st.markdown("---")
    st.caption("과목/목표시간 입력(빈 TargetMinutes는 우선순위로 자동 배분)")
    subjects_df = st.data_editor(
        make_default_subjects(),
        key="subjects_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Subject": st.column_config.TextColumn("과목"),
            "TargetMinutes": st.column_config.NumberColumn("목표시간(분)", step=5),
            "Priority(1-5)": st.column_config.NumberColumn("우선순위(1-5)", min_value=1,max_value=5,step=1),
            "MinSession(min)": st.column_config.NumberColumn("최소 세션(분)", step=5),
            "Difficulty": st.column_config.NumberColumn("난이도(1~5)", min_value=1,max_value=5,step=1),
            "RecoveryTime(min)": st.column_config.NumberColumn("전환 회복시간(분)", step=1),
        }
    )
    st.markdown("---")
    seed = st.number_input("무작위 분배 시드", min_value=0,value=42,step=1)
    generate_btn = st.button("🪄 계획 생성/재계산")

# ---------- 데이터 전처리 ----------
subjects_df = subjects_df.dropna(subset=["Subject"]).copy()
subjects_df["Subject"] = subjects_df["Subject"].str.strip()
subjects_df = subjects_df[subjects_df["Subject"] != ""]
if subjects_df.empty:
    st.warning("사이드바에서 과목을 입력하세요.")
    st.stop()

if "done_subjects" not in st.session_state:
    st.session_state.done_subjects = set()

subjects_df = subjects_df[~subjects_df["Subject"].isin(st.session_state.done_subjects)]
if subjects_df.empty:
    st.success("모든 과목을 완료했습니다! 🎉")
    st.stop()

has_target = subjects_df["TargetMinutes"].fillna(0) > 0

# ---------- 날짜/가용시간 테이블 ----------
weekday_map = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
days_off_idx = {k for k,v in weekday_map.items() if v in days_off}

calendar = []
for d in daterange(today,exam_date):
    if d.weekday() in days_off_idx:
        avail = 0
    else:
        base = daily_minutes
        if is_weekend(d):
            base *= weekend_factor
        avail = base
    avail = round_to_step(max(avail,0), min_step)
    calendar.append({"Date":d, "AvailMinutes":float(avail), "Weekday":weekday_map[d.weekday()]})
cal_df = pd.DataFrame(calendar)
if cal_df["AvailMinutes"].sum()==0:
    st.error("가용 시간이 0입니다. 설정을 조정하세요.")
    st.stop()

# ---------- 목표시간 확정 ----------
subjects = subjects_df.copy()
auto_mask = ~has_target
manual_total = subjects.loc[~auto_mask,"TargetMinutes"].sum()
remaining_capacity = max(cal_df["AvailMinutes"].sum() - manual_total, 0)

if auto_mask.any():
    pr = subjects.loc[auto_mask,"Priority(1-5)"].astype(float)
    pr_sum = pr.sum()
    if pr_sum <=0:
        alloc = np.repeat(remaining_capacity/auto_mask.sum(), auto_mask.sum())
    else:
        alloc = remaining_capacity * (pr/pr_sum).values
    subjects.loc[auto_mask,"TargetMinutes"] = alloc

subjects["TargetMinutes"] = subjects["TargetMinutes"].astype(float).apply(lambda x: float(round_to_step(max(x,0), min_step)))
subjects = subjects[subjects["TargetMinutes"]>0].reset_index(drop=True)
if subjects.empty:
    st.success("모든 과목을 완료했습니다! 🎉")
    st.stop()

# ---------- 스케줄링 with 난이도 & 회복시간 ----------
np.random.seed(seed)
plan_rows = []
remaining = subjects[["Subject","TargetMinutes","MinSession(min)","Difficulty","RecoveryTime(min)"]].set_index("Subject").to_dict(orient="index")

# 계수
alpha = 0.05  # 난이도 영향
beta = 0.05   # 회복시간 영향
base_eff = 1.0

for _, row in cal_df.iterrows():
    day = row["Date"]
    capacity = float(row["AvailMinutes"])
    if capacity<=0:
        continue

    def remaining_total():
        return sum(v["TargetMinutes"] for v in remaining.values())

    daily_plan = []
    safety = 0
    while capacity>0 and remaining_total()>0 and safety<1000:
        safety+=1
        total_rem = remaining_total()
        if total_rem==0: break
        avg_min = np.mean([remaining[s]["MinSession(min)"] for s in remaining if remaining[s]["TargetMinutes"]>0])
        round_chunk = min(capacity, max(min_step, avg_min))

        # 효율 계산
        best_eff = -1
        best_s = None
        for s in remaining:
            if remaining[s]["TargetMinutes"]<=0: continue
            prev_s = daily_plan[-1]["Subject"] if daily_plan else s
            diff = remaining[prev_s]["Difficulty"]
            recov = remaining[prev_s]["RecoveryTime(min)"]
            eff = base_eff*(1-alpha*(diff-3))*(1-beta*(recov/10))  # 단순 예시
            if eff>best_eff:
                best_eff = eff
                best_s = s
        if best_s is None: break

        share = min(round_chunk, remaining[best_s]["TargetMinutes"], capacity)
        share = float(round_to_step(share, min_step))
        if share<=0: break

        plan_rows.append({"Date":day, "Subject":best_s, "Minutes":share})
        daily_plan.append({"Subject":best_s})
        remaining[best_s]["TargetMinutes"] = float(round_to_step(remaining[best_s]["TargetMinutes"]-share, min_step))
        capacity = float(round_to_step(capacity-share, min_step))

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
st.title("📘 시험공부 플래너 (난이도/회복시간 기반 순서 최적화)")
left,right = st.columns([1.1,1])

with left:
    st.subheader("오늘 할 일")
    today_plan = plan_df[plan_df["Date"]==today].copy()
    today_plan["Key"] = today_plan.apply(key_for, axis=1)
    if today_plan.empty:
        st.info("오늘은 계획이 없어요.")
    else:
        for i,r in today_plan.iterrows():
            k = r["Key"]
            checked = k in st.session_state.done
            new_val = st.checkbox(f"{r['Subject']} — {r['Minutes']:.0f}분", value=checked, key=f"chk_{k}_{i}")
            if new_val and not checked: st.session_state.done.add(k)
            elif not new_val and checked: st.session_state.done.discard(k)
    completed = plan_df[plan_df.apply(key_for,axis=1).isin(st.session_state.done)]["Minutes"].sum()
    total = plan_df["Minutes"].sum()
    prog = 0 if total==0 else completed/total
    st.progress(min(prog,1.0), text=f"전체 진행률: {completed:.0f}/{total:.0f}분")

    done_subjects_today = set(today_plan[today_plan["Key"].isin(st.session_state.done)]["Subject"].unique())
    if st.button("✅ 완료 과목 제외 후 재계산"):
        st.session_state.done_subjects.update(done_subjects_today)
        st.experimental_rerun()

with right:
    st.subheader("요약")
    subj_summary = plan_df.groupby("Subject")["Minutes"].sum().reset_index().sort_values("Minutes",ascending=False)
    fig_pie = px.pie(subj_summary,names="Subject",values="Minutes",title="과목별 총 공부시간 비율(분)")
    st.plotly_chart(fig_pie,use_container_width=True)
    daily_subject = plan_df.pivot_table(index="Date",columns="Subject",values="Minutes",aggfunc="sum").fillna(0)
    daily_subject = daily_subject.sort_index()
    fig_bar = px.bar(daily_subject,title="일자별 과목 스택 바(계획)",barmode="stack")
    st.plotly_chart(fig_bar,use_container_width=True)

st.markdown("---")
st.subheader("📅 일자별 상세 계획표")
pivot_table = plan_df.pivot_table(index="Date",columns="Subject",values="Minutes",aggfunc="sum").fillna(0)
pivot_table["Total"] = pivot_table.sum(axis=1)
pivot_table.index = pivot_table.index.astype(str)
st.dataframe(pivot_table,use_container_width=True)
csv = pivot_table.to_csv(index=True).encode("utf-8-sig")
st.download_button("⬇️ 계획 CSV 다운로드", data=csv, file_name="study_plan.csv", mime="text/csv")

if generate_btn:
    st.experimental_rerun()
