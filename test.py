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
    .btn-link {
        display: inline-block;
        margin-top: 10px;
        padding: 8px 16px;
        border-radius: 12px;
        font-weight: bold;
        text-decoration: none;
        background: linear-gradient(90deg, #FFD93D, #6BCB77, #4D96FF);
        color: black;
    }
    .btn-link:hover {
        filter: brightness(1.2);
    }
    </style>
    """, unsafe_allow_html=True
)

# ===============================
# 데이터 정의 (문제집 + 링크 포함)
# ===============================
data = {
    "국어": {
        "문학": [
            {"책": "매삼문", "설명": "수능 국어를 처음 접하거나 평가원 기출문제를 풀어 보고 싶은 학생분들에게 추천.", "링크": "https://search.shopping.naver.com/search/all?query=매삼문"},
            {"책": "마더텅 국어 문학", "설명": "국어에 자신이 없지만 스스로 독학하고 싶은 학생에게 적합.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 국어 문학"},
            {"책": "빠작 고등 국어 고전 문학", "설명": "부담 없이 자주 나오는 고전문학 학습 가능.", "링크": "https://search.shopping.naver.com/search/all?query=빠작 고등 국어 고전문학"},
            {"책": "EBS 올림포스 고전/현대 문학", "설명": "내신과 수능을 동시에 준비할 수 있는 교재.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 올림포스 문학"}
        ],
        "학습루트": "문학 기초 → 기출문제 풀이 → 심화 작품 분석 → 모의고사 실전 연습",
        "루트이유": "기초부터 시작해 난이도를 점진적으로 높이며 문학 감각과 문제 해결력을 동시에 향상시킬 수 있습니다."
    },
    "영어": {
        "1~2등급": {
            "문제집": [
                {"책": "EBS 수능특강 영어", "설명": "수능과 내신 대비 모두 가능", "링크": "https://search.shopping.naver.com/search/all?query=EBS 수능특강 영어"},
                {"책": "쎄듀 빈칸 실전편", "설명": "기출 분석과 실전 연습에 최적화", "링크": "https://search.shopping.naver.com/search/all?query=쎄듀 영어"},
                {"책": "수능영어 절대유형 3142", "설명": "3점 문항 유형 집중 훈련", "링크": "https://search.shopping.naver.com/search/all?query=절대유형 3142"},
                {"책": "어법끝 ESSENTIAL", "설명": "수능, 내신 고난도 어법 완성", "링크": "https://search.shopping.naver.com/search/all?query=어법끝"}
            ],
            "학습루트": "문법 고난도 → 독해 고난도 지문 → 어휘 심화 암기 → 실전 문제 풀이",
            "루트이유": "상위권은 실수 최소화와 고난도 문제 완벽 해결이 목표."
        },
        "3~4등급": {
            "문제집": [
                {"책": "자이스토리 영어 독해 기본", "설명": "내신과 모의고사 독해를 동시에 대비", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 영어 독해"},
                {"책": "EBS 올림포스 영어 독해", "설명": "내신 대비에 강력 추천", "링크": "https://search.shopping.naver.com/search/all?query=올림포스 영어"},
                {"책": "능률 보카 어원편", "설명": "기본 어휘력 확충", "링크": "https://search.shopping.naver.com/search/all?query=능률 보카 어원편"}
            ],
            "학습루트": "어휘 기본 암기 → 독해 기초 훈련 → 문법 정리 → 기출 독해 풀이",
            "루트이유": "영어 독해 기본기와 어휘력을 빠르게 끌어올려야 성적 향상이 가능합니다."
        }
    },
    "수학": {
        "상위권": {
            "루트": "개념원리 심화 → 블랙라벨 → 수능 기출 N제 → 실전 모의고사",
            "설명": "상위권 학생들은 고난도 문제를 대비해야 하므로 심화문제집과 기출문제를 반복."
        },
        "중위권": {
            "루트": "개념원리 → 자이스토리 → 마더텅 기출문제집",
            "설명": "중위권 학생들은 개념을 다지고 기출을 통해 문제 접근 방식을 학습."
        }
    },
    "과탐": {
        "물리학": [
            {"책": "자이스토리 물리학1", "설명": "기출문제를 통한 개념 정리와 실전 훈련 가능", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 물리학1"},
            {"책": "EBS 수능특강 물리학1", "설명": "EBS 연계 대비 필수 교재", "링크": "https://search.shopping.naver.com/search/all?query=EBS 수능특강 물리학1"}
        ],
        "화학": [
            {"책": "마더텅 화학1", "설명": "내신과 수능 기출 동시 대비", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 화학1"},
            {"책": "자이스토리 화학1", "설명": "실전 기출 훈련 가능", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 화학1"}
        ],
        "생명과학": [
            {"책": "자이스토리 생명과학1", "설명": "개념 + 기출문제 풀이 가능", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 생명과학1"},
            {"책": "EBS 수능특강 생명과학1", "설명": "EBS 연계 교재", "링크": "https://search.shopping.naver.com/search/all?query=EBS 수능특강 생명과학1"}
        ],
        "지구과학": [
            {"책": "자이스토리 지구과학1", "설명": "방대한 기출문제를 통한 완벽 대비", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 지구과학1"},
            {"책": "EBS 수능특강 지구과학1", "설명": "EBS 연계 필수 교재", "링크": "https://search.shopping.naver.com/search/all?query=EBS 수능특강 지구과학1"}
        ]
    }
}

# ===============================
# 카드 출력 함수 (구매 링크 버튼 추가)
# ===============================
def show_cards(items):
    for item in items:
        st.markdown(f"""
        <div class="card">
            <h3>📚 {item['책']}</h3>
            <p>{item['설명']}</p>
            <a class="btn-link" href="{item['링크']}" target="_blank">🔗 구매하러 가기</a>
        </div>
        """, unsafe_allow_html=True)

# ===============================
# UI
# ===============================
st.title("🌈 고2 과목&수준별 문제집 추천 🌈")

subject = st.selectbox("과목을 선택하세요", list(data.keys()))

if subject == "국어":
    category = st.selectbox("국어 분야를 선택하세요", ["문학"])
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
    category = st.selectbox("과탐 과목을 선택하세요", list(data[subject].keys()))
    st.subheader(f"{subject} - {category} 추천 문제집")
    show_cards(data[subject][category])
