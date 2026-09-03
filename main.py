# --------------------------------
# 1. 원본 데이터 요약통계
# --------------------------------
st.subheader("📊 원본 데이터 요약통계")

summary = df[
    ["평균기온", "최저기온", "최고기온"]
].describe()

# 원하는 통계만 선택
summary_table = summary.loc[
    ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
].copy()

# 행 이름을 한국어로 변경
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

# 열 이름을 보기 좋게 변경
summary_table.columns = [
    "평균기온 (℃)",
    "최저기온 (℃)",
    "최고기온 (℃)"
]

# 소수점 둘째 자리
summary_table = summary_table.round(2)

st.dataframe(
    summary_table,
    use_container_width=True
)

st.caption(
    "※ 원본 데이터의 평균기온·최저기온·최고기온을 기준으로 계산한 요약통계입니다."
)
