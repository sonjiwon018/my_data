import streamlit as st
import pandas as pd

# --------------------------------
# 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="서울의 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# --------------------------------
# 제목
# --------------------------------
st.title("🌡️ 서울의 100년 기온 변화")

st.write(
    "서울의 기상 데이터를 이용하여 "
    "100년 동안 연평균 기온이 어떻게 변해 왔는지 살펴봅니다."
)

# --------------------------------
# 데이터 주소
# --------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/"
    "modudata/main/data/seoul.csv"
)


# --------------------------------
# 데이터 불러오기
# --------------------------------
@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8-sig"
    )

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 기온 데이터 숫자로 변환
    for column in ["평균기온", "최저기온", "최고기온"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


try:

    df = load_data()

    # =================================
    # 1. 원본 데이터 기본 정보
    # =================================

    st.subheader("📊 원본 데이터 요약")

    # 데이터 개수
    data_count = len(df)

    # 관측 지점
    stations = df["지점"].dropna().unique()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "전체 데이터 개수",
            f"{data_count:,}개"
        )

    with col2:
        st.metric(
            "관측 지점",
            ", ".join(map(str, stations))
        )

    # =================================
    # 2. 기온 요약통계
    # =================================

    st.subheader("📈 기온 요약통계")

    summary = df[
        ["평균기온", "최저기온", "최고기온"]
    ].describe()

    summary_table = summary.loc[
        [
            "count",
            "mean",
            "std",
            "min",
            "25%",
            "50%",
            "75%",
            "max"
        ]
    ].copy()

    # 행 이름 변경
    summary_table.index = [
        "개수",
        "평균",
        "표준편차",
        "최소값",
        "25%",
        "중앙값",
        "75%",
        "최대값"
    ]

    # 열 이름 변경
    summary_table.columns = [
        "평균기온 (℃)",
        "최저기온 (℃)",
        "최고기온 (℃)"
    ]

    summary_table = summary_table.round(2)

    st.dataframe(
        summary_table,
        use_container_width=True
    )

    # =================================
    # 3. 연도별 평균기온 계산
    # =================================

    df["연도"] = df["날짜"].dt.year

    yearly_temp = (
        df.dropna(
            subset=["날짜", "평균기온"]
        )
        .groupby("연도")["평균기온"]
        .mean()
        .sort_index()
    )

    # 가장 최근 연도
    latest_year = yearly_temp.index.max()

    # 최근 100년
    start_year = latest_year - 99

    # 100년의 모든 연도 생성
    all_years = pd.DataFrame({
        "연도": range(
            start_year,
            latest_year + 1
        )
    })

    # 실제 데이터가 없는 연도는 NaN으로 남김
    chart_data = all_years.merge(
        yearly_temp.reset_index(),
        on="연도",
        how="left"
    )

    chart_data = chart_data.set_index("연도")

    # =================================
    # 4. 연평균 기온 그래프
    # =================================

    st.subheader(
        f"📉 서울 연평균 기온 변화 "
        f"({start_year}~{latest_year})"
    )

    st.info(
        "관측 데이터가 없는 연도는 "
        "그래프의 선을 연결하지 않고 끊어서 표시합니다."
    )

    st.line_chart(
        chart_data,
        x_label="연도",
        y_label="연평균 기온 (℃)"
    )

    # =================================
    # 5. 기온 변화 비교
    # =================================

    valid_data = (
        chart_data["평균기온"]
        .dropna()
    )

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

    # =================================
    # 6. 원본 데이터 표
    # =================================

    st.subheader("📋 원본 데이터")

    # 원하는 순서대로 열 배치
    display_columns = [
        "날짜",
        "지점",
        "평균기온",
        "최저기온",
        "최고기온"
    ]

    display_data = df[
        display_columns
    ].copy()

    # 날짜 표시
    display_data["날짜"] = (
        display_data["날짜"]
        .dt.strftime("%Y-%m-%d")
    )

    # 기온 소수점 한 자리
    for column in [
        "평균기온",
        "최저기온",
        "최고기온"
    ]:
        display_data[column] = (
            display_data[column]
            .round(1)
        )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

    # =================================
    # 7. 데이터 출처
    # =================================

    st.caption(
        "데이터 출처: 서울 기상 관측 데이터(seoul.csv)"
    )


except Exception as e:

    st.error(
        "데이터를 불러오는 중 문제가 발생했습니다."
    )

    st.write(
        f"오류 내용: {e}"
    )
