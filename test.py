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
# 데이터 정의
# ===============================
data = {
    "국어": {
        "상": [
            {"책": "매삼문", "설명": "평가원 기출 기반, 상위권 문제풀이 적합.", "링크": "https://search.shopping.naver.com/search/all?query=매삼문"},
            {"책": "마더텅 국어 문학", "설명": "독학 최적화, 해설 충실.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 국어 문학"},
            {"책": "빠작 고전문학", "설명": "핵심 고전문학 체계적 정리.", "링크": "https://search.shopping.naver.com/search/all?query=빠작 고전 문학"}
        ],
        "중": [
            {"책": "EBS 올림포스 국어", "설명": "내신+기출 연계, 중위권 학습에 적합.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 올림포스 국어"},
            {"책": "마더텅 국어 문학 기본편", "설명": "기본 개념 이해와 문제풀이 병행.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 국어 문학 기본편"},
            {"책": "쎈 국어 문학", "설명": "중위권 반복 학습에 좋음.", "링크": "https://search.shopping.naver.com/search/all?query=쎈 국어 문학"}
        ],
        "하": [
            {"책": "천일문 국어", "설명": "기초 다지기 및 독해 연습.", "링크": "https://search.shopping.naver.com/search/all?query=천일문 국어"},
            {"책": "EBS 수능특강 국어", "설명": "기초 개념과 유형 학습.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 수능특강 국어"},
            {"책": "빠작 국어 기초", "설명": "쉬운 문제로 문법/독해 감각 확보.", "링크": "https://search.shopping.naver.com/search/all?query=빠작 국어 기초"}
        ]
    },
    "영어": {
        "상": [
            {"책": "EBS 수능특강 영어", "설명": "상위권 독해 및 연계 대비.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 수능특강 영어"},
            {"책": "쎄듀 빈칸 실전편", "설명": "킬러 문항 집중 연습.", "링크": "https://search.shopping.naver.com/search/all?query=쎄듀 영어"},
            {"책": "어법끝 ESSENTIAL", "설명": "상위권 어법 완성.", "링크": "https://search.shopping.naver.com/search/all?query=어법끝"}
        ],
        "중": [
            {"책": "파워업 독해실전", "설명": "중위권 독해 실력 향상.", "링크": "https://search.shopping.naver.com/search/all?query=파워업 독해실전"},
            {"책": "천일문 핵심", "설명": "문장 구조+독해 병행.", "링크": "https://search.shopping.naver.com/search/all?query=천일문 핵심"},
            {"책": "어휘끝 수능", "설명": "중급 어휘 학습.", "링크": "https://search.shopping.naver.com/search/all?query=어휘끝 수능"}
        ],
        "하": [
            {"책": "어법끝 START", "설명": "기초 문법 다지기.", "링크": "https://search.shopping.naver.com/search/all?query=어법끝 START"},
            {"책": "파워업 독해유형", "설명": "쉬운 독해 문제 반복.", "링크": "https://search.shopping.naver.com/search/all?query=파워업 독해유형"},
            {"책": "어휘끝 고교기본", "설명": "기초 단어 암기.", "링크": "https://search.shopping.naver.com/search/all?query=어휘끝 고교기본"}
        ]
    },
    "수학": {
        "상": [
            {"책": "정석", "설명": "기본 개념 심화 후 응용.", "링크": "https://search.shopping.naver.com/search/all?query=정석"},
            {"책": "쎈", "설명": "상위권 유형별 연습.", "링크": "https://search.shopping.naver.com/search/all?query=쎈"},
            {"책": "블랙라벨", "설명": "킬러 문제 집중.", "링크": "https://search.shopping.naver.com/search/all?query=블랙라벨"}
        ],
        "중": [
            {"책": "개념원리", "설명": "기본 개념+유형 연습.", "링크": "https://search.shopping.naver.com/search/all?query=개념원리"},
            {"책": "자이스토리", "설명": "중위권 기출 집중.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리"},
            {"책": "마더텅 수학", "설명": "내신+기출 병행.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 수학"}
        ],
        "하": [
            {"책": "스타트업", "설명": "기초 개념 다지기.", "링크": "https://search.shopping.naver.com/search/all?query=스타트업"},
            {"책": "RPM", "설명": "쉬운 문제 반복.", "링크": "https://search.shopping.naver.com/search/all?query=RPM"},
            {"책": "체크체크", "설명": "기초 연습 강화.", "링크": "https://search.shopping.naver.com/search/all?query=체크체크"}
        ]
    },
    "과탐": {
        "상": {
            "물리학": [
                {"책": "블랙라벨 물리1", "설명": "최상위 심화 대비.", "링크": "https://search.shopping.naver.com/search/all?query=블랙라벨 물리1"},
                {"책": "자이스토리 물리1", "설명": "기출+심화 연습.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 물리1"},
                {"책": "마더텅 물리1", "설명": "기출 연습 풍부.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 물리1"}
            ],
            "화학": [
                {"책": "블랙라벨 화학1", "설명": "고난도 심화 대비.", "링크": "https://search.shopping.naver.com/search/all?query=블랙라벨 화학1"},
                {"책": "자이스토리 화학1", "설명": "기출 문제 체계 정리.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 화학1"},
                {"책": "EBS 화학1", "설명": "연계 대비 필수.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 화학1"}
            ],
            "생명과학": [
                {"책": "블랙라벨 생명1", "설명": "최상위 심화 대비.", "링크": "https://search.shopping.naver.com/search/all?query=블랙라벨 생명1"},
                {"책": "자이스토리 생명1", "설명": "출제 패턴 분석.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 생명1"},
                {"책": "EBS 생명1", "설명": "연계 대비.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 생명1"}
            ],
            "지구과학": [
                {"책": "블랙라벨 지구1", "설명": "킬러 대비 심화.", "링크": "https://search.shopping.naver.com/search/all?query=블랙라벨 지구1"},
                {"책": "자이스토리 지구1", "설명": "출제 경향 정리.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 지구1"},
                {"책": "EBS 지구1", "설명": "연계 대비.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 지구1"}
            ]
        },
        "중": {
            "물리학": [
                {"책": "자이스토리 물리1", "설명": "기출 위주 학습.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 물리1"},
                {"책": "EBS 물리1", "설명": "연계 교재 활용.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 물리1"},
                {"책": "마더텅 물리1", "설명": "기본+문제풀이 병행.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 물리1"}
            ],
            "화학": [
                {"책": "자이스토리 화학1", "설명": "기출 중심 반복.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 화학1"},
                {"책": "EBS 화학1", "설명": "연계 대비.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 화학1"},
                {"책": "마더텅 화학1", "설명": "문제 연습 병행.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 화학1"}
            ],
            "생명과학": [
                {"책": "자이스토리 생명1", "설명": "대표 기출 패턴 학습.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 생명1"},
                {"책": "EBS 생명1", "설명": "연계 대비.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 생명1"},
                {"책": "마더텅 생명1", "설명": "기출+기본 반복 학습.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 생명1"}
            ],
            "지구과학": [
                {"책": "자이스토리 지구1", "설명": "대표 기출 학습.", "링크": "https://search.shopping.naver.com/search/all?query=자이스토리 지구1"},
                {"책": "EBS 지구1", "설명": "연계 대비.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 지구1"},
                {"책": "마더텅 지구1", "설명": "기출+기본 문제 반복.", "링크": "https://search.shopping.naver.com/search/all?query=마더텅 지구1"}
            ]
        },
        "하": {
            "물리학": [
                {"책": "EBS 물리1 기초", "설명": "기초 개념 정리.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 물리1 기초"},
                {"책": "천일문 물리", "설명": "쉬운 문제 반복.", "링크": "https://search.shopping.naver.com/search/all?query=천일문 물리"},
                {"책": "체크체크 물리", "설명": "기본 문제 강화.", "링크": "https://search.shopping.naver.com/search/all?query=체크체크 물리"}
            ],
            "화학": [
                {"책": "EBS 화학1 기초", "설명": "기초 개념 정리.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 화학1 기초"},
                {"책": "천일문 화학", "설명": "쉬운 문제 반복.", "링크": "https://search.shopping.naver.com/search/all?query=천일문 화학"},
                {"책": "체크체크 화학", "설명": "기본 문제 강화.", "링크": "https://search.shopping.naver.com/search/all?query=체크체크 화학"}
            ],
            "생명과학": [
                {"책": "EBS 생명1 기초", "설명": "기초 개념 정리.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 생명1 기초"},
                {"책": "천일문 생명", "설명": "쉬운 문제 반복.", "링크": "https://search.shopping.naver.com/search/all?query=천일문 생명"},
                {"책": "체크체크 생명", "설명": "기본 문제 강화.", "링크": "https://search.shopping.naver.com/search/all?query=체크체크 생명"}
            ],
            "지구과학": [
                {"책": "EBS 지구1 기초", "설명": "기초 개념 정리.", "링크": "https://search.shopping.naver.com/search/all?query=EBS 지구1 기초"},
                {"책": "천일문 지구", "설명": "쉬운 문제 반복.", "링크": "https://search.shopping.naver.com/search/all?query=천일문 지구"},
                {"책": "체크체크 지구", "설명": "기본 문제 강화.", "링크": "https://search.shopping.naver.com/search/all?query=체크체크 지구"}
            ]
        }
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

subject = st.selectbox("과목을 선택하세요", list(data.keys()))
level = st.selectbox("등급을 선택하세요", ["상", "중", "하"])

if subject in ["국어", "영어", "수학"]:
    st.subheader(f"{subject} {level} 추천 문제집")
    show_cards(data[subject][level])
elif subject == "과탐":
    category = st.selectbox("과탐 과목을 선택하세요", list(data[subject][level].keys()))
    st.subheader(f"{level} - {category} 추천 문제집")
    show_cards(data[subject][level][category])
