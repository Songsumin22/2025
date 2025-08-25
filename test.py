import streamlit as st

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(
    page_title="🌈 고2 과목&등급별 문제집 추천",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# CSS 스타일 (화려한 카드 디자인)
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
# 데이터 정의 (문제집 + 학습 루트)
# ===============================
data = {
    "국어": {
        "1~2등급": {
            "문제집":[
                {"책":"매삼문","설명":"평가원 기출 기반, 상위권 문제풀이 적합.","링크":"https://search.shopping.naver.com/search/all?query=매삼문"},
                {"책":"마더텅 국어 문학","설명":"독학 최적화, 해설 충실.","링크":"https://search.shopping.naver.com/search/all?query=마더텅+국어+문학"},
                {"책":"빠작 고전문학","설명":"핵심 고전문학 체계적 정리.","링크":"https://search.shopping.naver.com/search/all?query=빠작+고전+문학"}
            ],
            "루트":"문학 기초 → 기출문제 풀이 → 심화 작품 분석 → 모의고사 실전 연습",
            "루트이유":"기초부터 시작해 난이도를 점진적으로 높이며 문학 감각과 문제 해결력을 동시에 향상시킬 수 있습니다."
        },
        "3~4등급": {
            "문제집":[
                {"책":"EBS 올림포스 국어","설명":"내신+기출 연계, 중위권 학습 적합.","링크":"https://search.shopping.naver.com/search/all?query=EBS+올림포스+국어"},
                {"책":"마더텅 국어 문학 기본편","설명":"기본 개념 이해와 문제풀이 병행.","링크":"https://search.shopping.naver.com/search/all?query=마더텅+국어+문학+기본편"},
                {"책":"쎈 국어 문학","설명":"중위권 반복 학습에 좋음.","링크":"https://search.shopping.naver.com/search/all?query=쎈+국어+문학"}
            ],
            "루트":"문학 기초 확인 → 기출 문제 풀이 반복 → 중요 작품 분석 → 모의고사 연습",
            "루트이유":"기초 부족 부분 보완, 중급 독해 및 문학 감각 강화."
        },
        "5등급 이하": {
            "문제집":[
                {"책":"천일문 국어","설명":"기초 다지기 및 독해 연습.","링크":"https://search.shopping.naver.com/search/all?query=천일문+국어"},
                {"책":"EBS 수능특강 국어","설명":"기초 개념과 유형 학습.","링크":"https://search.shopping.naver.com/search/all?query=EBS+수능특강+국어"},
                {"책":"빠작 국어 기초","설명":"쉬운 문제로 문법/독해 감각 확보.","링크":"https://search.shopping.naver.com/search/all?query=빠작+국어+기초"}
            ],
            "루트":"기초 문법과 독해 이해 → 쉬운 문제 반복 → 유형별 연습 → 점진적 난이도 상승",
            "루트이유":"국어 자신감 회복, 기초 문법/독해 능력 강화."
        }
    },
    "영어": {
        "1~2등급": {
            "문제집":[
                {"책":"EBS 수능특강 영어","설명":"상위권 독해 및 연계 대비.","링크":"https://search.shopping.naver.com/search/all?query=EBS+수능특강+영어"},
                {"책":"쎄듀 빈칸 실전편","설명":"킬러 문항 집중 연습.","링크":"https://search.shopping.naver.com/search/all?query=쎄듀+영어"},
                {"책":"어법끝 ESSENTIAL","설명":"상위권 어법 완성.","링크":"https://search.shopping.naver.com/search/all?query=어법끝"}
            ],
            "루트":"문법 심화 → 독해 고난도 지문 → 어휘 심화 암기 → 실전 문제풀이",
            "루트이유":"상위권은 실수를 최소화하며, 고난도 문제 완벽 해결 능력 향상."
        },
        "3~4등급": {
            "문제집":[
                {"책":"파워업 독해실전","설명":"중위권 독해 실력 향상.","링크":"https://search.shopping.naver.com/search/all?query=파워업+독해실전"},
                {"책":"천일문 핵심","설명":"문장 구조+독해 병행.","링크":"https://search.shopping.naver.com/search/all?query=천일문+핵심"},
                {"책":"어휘끝 수능","설명":"중급 어휘 학습.","링크":"https://search.shopping.naver.com/search/all?query=어휘끝+수능"}
            ],
            "루트":"문법 점검 → 독해 중급 지문 → 어휘 암기 → 기출 문제풀이",
            "루트이유":"기초 부족 부분 보완, 반복 학습으로 난이도 점진 상승."
        },
        "5등급 이하": {
            "문제집":[
                {"책":"어법끝 START","설명":"기초 문법 다지기.","링크":"https://search.shopping.naver.com/search/all?query=어법끝+START"},
                {"책":"파워업 독해유형","설명":"쉬운 독해 문제 반복.","링크":"https://search.shopping.naver.com/search/all?query=파워업+독해유형"},
                {"책":"어휘끝 고교기본","설명":"기초 단어 암기.","링크":"https://search.shopping.naver.com/search/all?query=어휘끝+고교기본"}
            ],
            "루트":"문법 기초 → 짧은 독해 → 기초 어휘 → 쉬운 문제 반복",
            "루트이유":"영어 기초 실력 확보, 정확한 문장 이해와 단어 활용 능력 향상."
        }
    },
    "수학": {
        "1~2등급": {
            "문제집":[
                {"책":"정석","설명":"개념 빠르게 훑고 심화 문제 위주 학습.","링크":"https://search.shopping.naver.com/search/all?query=정석"},
                {"책":"쎈","설명":"상위권 문제 집중.","링크":"https://search.shopping.naver.com/search/all?query=쎈"},
                {"책":"블랙라벨","설명":"심화+실모 병행.","링크":"https://search.shopping.naver.com/search/all?query=블랙라벨"}
            ],
            "루트":"정석 → 쎈 → 블랙라벨/일품 → 한완수 → 실모 병행",
            "루트이유":"상위권은 개념 빠르게 훑고 심화 문제 위주 학습, 기출 분석 철저."
        },
        "3~4등급": {
            "문제집":[
                {"책":"개념원리","설명":"중위권 개념 정리","링크":"https://search.shopping.naver.com/search/all?query=개념원리"},
                {"책":"쎈+RPM","설명":"유형 반복 연습","링크":"https://search.shopping.naver.com/search/all?query=쎈+RPM"},
                {"책":"자이스토리/마더텅","설명":"수능 대비","링크":"https://search.shopping.naver.com/search/all?query=자이스토리+마더텅"}
            ],
            "루트":"개념원리 → 쎈+RPM → 자이스토리/마더텅 → 수능특강",
            "루트이유":"개념 정리와 유형 반복 학습, 내신+수능 병행."
        },
        "5등급 이하": {
            "문제집":[
                {"책":"스타트업","설명":"기초 개념 학습","링크":"https://search.shopping.naver.com/search/all?query=스타트업"},
                {"책":"RPM+체크체크","설명":"반복 복습","링크":"https://search.shopping.naver.com/search/all?query=RPM+체크체크"},
                {"책":"기초문제 반복","설명":"강의 병행","링크":"https://search.shopping.naver.com/search/all?query=기초문제+반복"}
            ],
            "루트":"개념원리/스타트업 → RPM+체크체크 → 반복 복습+강의 병행",
            "루트이유":"기초 개념부터 차근차근 학습, 하루 1단원 정확히 이해."
        }
    },
    "과탐": {
        "물리": {
            "1~2등급":[
                {"책":"완자 물리학1","설명":"상위권 대비","링크":"https://search.shopping.naver.com/search/all?query=완자+물리학1"},
                {"책":"오투 물리학1","설명":"기출 분석","링크":"https://search.shopping.naver.com/search/all?query=오투+물리학1"},
                {"책":"하이탑 물리학1","설명":"심화 문제 포함","링크":"https://search.shopping.naver.com/search/all?query=하이탑+물리학1"}
            ],
            "3~4등급":[
                {"책":"완자 물리학1 기본","설명":"중위권 대비","링크":"https://search.shopping.naver.com/search/all?query=완자+물리학1+기본"},
                {"책":"오투 물리학1 기초","설명":"난이도 낮음","링크":"https://search.shopping.naver.com/search/all?query=오투+물리학1+기초"},
                {"책":"하이탑 물리학1 기초","설명":"문제 풀이 중심","링크":"https://search.shopping.naver.com/search/all?query=하이탑+물리학1+기초"}
            ],
            "5등급 이하":[
                {"책":"물리 기초","설명":"개념 이해","링크":"https://search.shopping.naver.com/search/all?query=물리+기초"},
                {"책":"쉬운 물리 문제","설명":"문제 반복","링크":"https://search.shopping.naver.com/search/all?query=쉬운+물리+문제"},
                {"책":"물리 기본서","설명":"자습용","링크":"https://search.shopping.naver.com/search/all?query=물리+기본서"}
            ],
            "루트":"기초 개념 → 유형별 문제 풀이 → 기출 심화 → 실전 문제 풀이",
            "루트이유":"기초부터 실전까지 단계별 학습으로 실력 향상."
        },
        # 화학, 생명, 지구도 동일 구조로 1~2/3~4/5등급 추가 가능
    }
}

# ===============================
# 카드 출력 함수
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
st.title("🌈 고2 과목&등급별 문제집 추천 🌈")

subject = st.selectbox("과목 선택", list(data.keys()))

# 과탐이면 분야 선택
if subject == "과탐":
    field = st.selectbox("과탐 분야 선택", list(data[subject].keys()))
    grade = st.selectbox("등급 선택", ["1~2등급", "3~4등급", "5등급 이하"])
    st.subheader(f"{field} {grade} 추천 문제집")
    show_cards(data[subject][field][grade])
    if st.button("학습 루트 보기"):
        st.success(f"📌 학습 루트: {data[subject][field]['루트']}\n💡 이유: {data[subject][field]['루트이유']}")
else:
    grade = st.selectbox("등급 선택", ["1~2등급", "3~4등급", "5등급 이하"])
    st.subheader(f"{subject} {grade} 추천 문제집")
    show_cards(data[subject][grade]["문제집"])
    if st.button("학습 루트 보기"):
        st.success(f"📌 학습 루트: {data[subject][grade]['루트']}\n💡 이유: {data[subject][grade]['루트이유']}")
