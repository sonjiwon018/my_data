import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울의 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울의 100년 기온 변화")
st.write(
    "서울의 일별 평균기온 데이터를 이용하여 "
    "연도별 평균기온의 변화를 살펴봅니다."
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온 숫자 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 결측값 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    return df


try:
    df = load_data()

    # --------------------------------
    # 1. 원본 데이터 요약통계
    # --------------------------------
    st.subheader("📊 원본 데이터 요약통계")

    summary = df["평균기온"].describe()

    summary_table = pd.DataFrame({
        "통계": [
            "개수",
            "평균",
            "표준편차",
            "최소값",
            "25%",
            "중앙값",
            "75%",
            "최대값"
        ],
        "평균기온 (℃)": [
            summary["count"],
            summary["mean"],
            summary["std"],
            summary["min"],
            summary["25%"],
            summary["50%"],
            summary["75%"],
            summary["max"]
        ]
    })

    summary_table["평균기온 (℃)"] = summary_table["평균기온 (℃)"].round(2)

    st.dataframe(
        summary_table,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "※ 요약통계는 원본 데이터의 일별 평균기온을 기준으로 계산했습니다."
    )

    # --------------------------------
    # 2. 연도별 평균기온 계산
    # --------------------------------
    df["연도"] = df["날짜"].dt.year

    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .sort_index()
    )

    # 실제 데이터가 있는 가장 최근 연도
    latest_year = yearly_temp.index.max()

    # 최근 100년
    start_year = latest_year - 99

    # 100년 범위 생성
    all_years = pd.DataFrame({
        "연도": range(start_year, latest_year + 1)
    })

    # 데이터가 없는 연도는 NaN으로 남김
    chart_data = all_years.merge(
        yearly_temp.reset_index(),
        on="연도",
        how="left"
    )

    chart_data = chart_data.set_index("연도")

    # --------------------------------
    # 3. 연평균 기온 그래프
    # --------------------------------
    st.subheader(
        f"📈 서울 연평균 기온 변화 ({start_year}~{latest_year})"
    )

    st.info(
        "실제 관측 자료가 존재하지 않는 연도는 "
        "그래프의 선을 연결하지 않고 끊어서 표시합니다."
    )

    st.line_chart(
        chart_data,
        x_label="연도",
        y_label="연평균 기온 (℃)"
    )

    # --------------------------------
    # 4. 시작 연도와 최근 연도 비교
    # --------------------------------
    valid_data = chart_data["평균기온"].dropna()

    first_temp = valid_data.iloc[0]
    last_temp = valid_data.iloc[-1]

    first_year = valid_data.index[0]
    last_year = valid_data.index[-1]

    change = last_temp - first_temp

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "첫 관측 연도 평균기온",
            f"{first_temp:.1f} ℃",
            f"{first_year}년"
        )

    with col2:
        st.metric(
            "최근 관측 연도 평균기온",
            f"{last_temp:.1f} ℃",
            f"{last_year}년"
        )

    with col3:
        st.metric(
            "두 연도의 기온 차이",
            f"{change:+.1f} ℃"
        )

    # --------------------------------
    # 5. 연도별 데이터
    # --------------------------------
    with st.expander("📋 연도별 평균기온 데이터 보기"):

        display_data = chart_data.reset_index().copy()

        display_data["평균기온"] = (
            display_data["평균기온"].round(1)
        )

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
