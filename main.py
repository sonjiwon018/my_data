import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울의 100년 기온 변화")
st.write("서울의 일별 평균기온 데이터를 이용하여 연도별 평균기온의 변화를 살펴봅니다.")

# 데이터 불러오기
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 결측값 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    return df


try:
    df = load_data()

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    # 100년 이상의 자료 중 가장 최근 100년을 기본으로 표시
    latest_year = yearly_temp["연도"].max()
    start_year = latest_year - 99

    chart_data = yearly_temp[
        (yearly_temp["연도"] >= start_year) &
        (yearly_temp["연도"] <= latest_year)
    ].copy()

    # 제목
    st.subheader(f"서울 연평균 기온 변화 ({start_year}~{latest_year})")

    # 설명
    st.info(
        "그래프의 한 점은 해당 연도의 일별 평균기온을 평균한 "
        "‘연평균 기온’을 나타냅니다."
    )

    # 선 그래프
    st.line_chart(
        chart_data.set_index("연도")["평균기온"],
        x_label="연도",
        y_label="연평균 기온 (℃)"
    )

    # 통계 정보
    col1, col2, col3 = st.columns(3)

    first_temp = chart_data.iloc[0]["평균기온"]
    last_temp = chart_data.iloc[-1]["평균기온"]
    change = last_temp - first_temp

    with col1:
        st.metric(
            "시작 연도 평균기온",
            f"{first_temp:.1f} ℃",
            f"{start_year}년"
        )

    with col2:
        st.metric(
            "최근 연도 평균기온",
            f"{last_temp:.1f} ℃",
            f"{latest_year}년"
        )

    with col3:
        st.metric(
            "두 연도의 기온 차이",
            f"{change:+.1f} ℃"
        )

    # 데이터 표
    with st.expander("연도별 평균기온 데이터 보기"):
        display_data = chart_data.copy()
        display_data["평균기온"] = display_data["평균기온"].round(1)

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    # 데이터 출처
    st.caption(
        "데이터 출처: 서울 기상 관측 데이터(seoul.csv)"
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.write(f"오류 내용: {e}")
