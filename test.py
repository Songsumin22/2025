import streamlit as st

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="🌈 고2 과목&수준별 문제집 추천",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# CSS 스타일 (무지개+화려한 카드 디자인)
# ===============================
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #FF6B6B, #FFD93D, #6BCB77, #4D96FF, #9D4EDD);
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
        color: white;
    }
    h1, h2, h3, h4 {
        text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
    }
    .card {
        background: rgba(0,0,0,0.5);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .card:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 12px 36px rgba(0,0,0,0.6);
    }
    div.stButton > button {
        background: linear-gradient(90deg, #FF6B6B, #FFD93D, #6BCB77, #4D96FF, #9D4EDD);
        color: black;
        font-weight: bold;
        border-radius: 15px;
        height: 50px;
        width: 100%;
        font-size: 16px;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        filter: brightness(1.2);
    }
    </style>
    """, unsafe_allow_html=True
)

# ===============================
# 데이터 정의
# ===============================
data = {
    "국어": {
        "문학": [
            {"책": "매삼문", "설명": "수능 국어를 처음 접하거나 평가원 기출문제를 풀어 보고 싶은 학생분들에게 추천드려요. 매일매일 3개의 문학 지문을 풀도록 되어 있어요. 많은 시간이 들이지 않고 꾸준히 좋은 지문들을 연습할 수 있어요. 문학 때문에 골치 아픈 분들에게 큰 도움이 될 것이에요."},
            {"책": "마더텅 국어 문학", "설명": "국어에 자신이 없지만 스스로 독학으로 공부하고 싶은 학생분에게 적합한 책이에요. 해설지의 퀄리티가 좋아서 혼자 학습하기 충분해요. 모든 지문이 해설지에 실려있고 첨삭해설에서 모르는 단어나 뜻이 친절하게 설명이 되어있어서 모르는 부분에 대한 첨삭을 받을 수 있어요."},
            {"책": "빠작 고등 국어 고전 문학", "설명": "부담스럽지 않게 자주 나오는 핵심 고전문학을 효율적이게 학습하고 싶은 학생들을 위한 문제집이에요. 고전 시가, 고전 소설, 고전 산문까지 유형별로 체계적으로 정리가 되어 있어요. 자주 나오는 중요 작품들이 수록되어 있고 빈출 어휘도 따로 학습할 수 있어요. 고전 문학에서 담고 있는 내용은 크게 차이 나는 부분이 없어서 생각보다 쉬워요. 엄선된 작품으로 고전 문학에 대한 감을 잡아보세요."},
            {"책": "EBS 올림포스 고전/현대 문학", "설명": "고전 문학 내신과 수능을 동시에 준비할 수 있는 문제집으로, 수능에 어떤 유형들일지 미리 체감할 수 있어요. 고려 가요와 향가부터 고려 시대와 조선 시대 문학까지 시대별로 내용이 구성되어 있어 기본 개념을 정리하기에 좋아요. 설명이 상세하고 예시가 많아서 이해가 잘 되서 혼자 공부하기에 적당해요. 이해하지 못한 부분은 인강을 통해 반복해서 학습할 수 있어요."},
        ],
        "학습루트": "문학 기초 → 기출문제 풀이 → 심화 작품 분석 → 모의고사 실전 연습",
        "루트이유": "기초부터 시작해 난이도를 점진적으로 높이며 문학 감각과 문제 해결력을 동시에 향상시킬 수 있습니다."
    },
    "영어": {
        "1~2등급": {
            "문제집": [
                {"책": "EBS 수능특강 영어", "설명": "수능과 내신 대비 모두 가능"},
                {"책": "쎄듀 빈순삽함 실전편", "설명": "기출 분석과 실전 연습에 최적화"},
                {"책": "수능영어 절대유형 3142", "설명": "3점 문항 유형 집중 훈련"},
                {"책": "어법끝 ESSENTIAL", "설명": "수능, 내신 고난도 어법 완성"}
            ],
            "학습루트": "문법 고난도 → 독해 고난도 지문 → 어휘 심화 암기 → 실전 문제 풀이",
            "루트이유": "1~2등급 학생은 실수 최소화와 고난도 문제 완벽 해결이 목표이므로, 기초 점검 후 실전 대비 집중이 중요합니다."
        },
        "3~4등급": {
            "문제집": [
                {"책": "파워업 독해실전편", "설명": "실전 독해 훈련에 적합"},
                {"책": "천일문 핵심 (Essential)", "설명": "문장 구조와 독해 훈련 병행 가능"},
                {"책": "어법끝 ESSENTIAL", "설명": "수능, 내신 필수 문법 완성"},
                {"책": "어휘끝 수능", "설명": "중급 수준의 필수 어휘 학습"}
            ],
            "학습루트": "문법 기본 점검 → 독해 중급 지문 → 어휘 암기 → 기출 문제 풀이",
            "루트이유": "기초 부족 부분을 보완하고 중급 독해 실력을 완성하며, 반복 학습으로 점차 난이도 올리기."
        },
        "5~6등급": {
            "문제집": [
                {"책": "어법끝 START", "설명": "수능 내신 어법 기본기 다지기"},
                {"책": "파워업 독해유형편", "설명": "독해 유형별 해결 전략과 문제풀이"},
                {"책": "어휘끝 고교기본", "설명": "기본 어휘력 강화"}
            ],
            "학습루트": "문법 기초 → 짧은 독해 → 기초 어휘 암기 → 쉬운 문제 반복",
            "루트이유": "영어 기초 다지기가 우선이며, 정확한 문장 이해와 기본 단어 활용 능력 확보가 목표입니다."
        },
        "7~9등급": {
            "문제집": [
                {"책": "어휘끝 중학 마스터", "설명": "중학 영단어 마스터 및 기초 어휘력 보강"},
                {"책": "첫단추 독해유형편", "설명": "수능 유형별 해결 전략과 꼼꼼한 해설 제공"},
                {"책": "Grammar in Use Basic", "설명": "기초 문법 학습"},
                {"책": "2025 중학영문법 3800제", "설명": "중학영문법 마스터 및 기초 실력 보강"}
            ],
            "학습루트": "문법 기초 학습 → 단어 기초 암기 → 쉬운 지문 반복 독해 → 문장 구조 이해",
            "루트이유": "영어에 대한 자신감 회복과 기초 실력 확보가 최우선 목표입니다."
        }
    },
    # ===============================
    # 수학, 과탐 데이터 (위와 동일, 생략 가능)
    # ===============================
}

# ===============================
# 카드 출력 함수
# ===============================
def show_cards(items):
    for item in items:
        st.markdown(f'<div class="card"><h3>📚 {item["책"]}</h3><p>{item["설명"]}</p></div>', unsafe_allow_html=True)

# ===============================
# UI
# ===============================
st.title("🌈 고2 과목&수준별 문제집 추천 🌈")

subject = st.selectbox("과목을 선택하세요", list(data.keys()))

if subject == "국어":
    category = st.selectbox("국어 분야를 선택하세요", list(data[subject].keys())[:-2])
    st.subheader(f"{subject} - {category} 추천 문제집")
    show_cards(data[subject][category])
    if st.button("학습 루트 보기"):
        st.success(f"📌 학습 루트: {data[subject]['학습루트']}\n\n💡 루트 이유: {data[subject]['루트이유']}")

elif subject == "영어":
    grade = st.selectbox("영어 등급을 선택하세요", list(data[subject].keys()))
    st.subheader(f"{subject} {grade} 추천 문제집")
    show_cards(data[subject][grade]["문제집"])
    if st.button("학습 루트 보기"):
        st.success(f"📌 학습 루트: {data[subject][grade]['학습루트']}\n\n💡 루트 이유: {data[subject][grade]['루트이유']}")

elif subject == "수학":
    grade = st.selectbox("수학 수준을 선택하세요", list(data[subject].keys()))
    st.subheader(f"{subject} {grade} 학습 루트")
    st.success(f"📌 루트: {data[subject][grade]['루트']}\n\n💡 설명: {data[subject][grade]['설명']}")

elif subject == "과탐":
    category = st.selectbox("과탐 분야를 선택하세요", list(data[subject].keys()))
    st.subheader(f"{subject} - {category} 추천 문제집")
    show_cards(data[subject][category])
