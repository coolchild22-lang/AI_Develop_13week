from pathlib import Path  # 파일 경로를 다루는 파이썬 기본 도구 (따로 설치 필요 없음)

import pandas as pd  # 표 형태 데이터를 다루는 라이브러리
import streamlit as st  # 웹 대시보드를 만드는 라이브러리

# 이 .py 파일이 있는 폴더 기준으로 CSV 위치를 정함 → 어느 폴더에서 실행해도 파일을 찾을 수 있음
CSV_PATH = Path(__file__).parent / "sales_sample.csv"
REQUIRED_COLUMNS = ["date", "region", "category", "sales", "quantity"]  # 화면에 꼭 필요한 열

# 페이지 기본 설정 (브라우저 탭 제목, 넓은 화면 사용)
st.set_page_config(page_title="영업팀 매출 현황", layout="wide")


@st.cache_data  # 처음 한 번만 파일을 읽고 결과를 저장 → 필터를 바꿔도 파일을 다시 읽지 않음
def load_data(file_time):  # file_time(파일 수정 시각)이 바뀌면 = 파일을 고치면 → 캐시를 버리고 새로 읽음
    # utf-8-sig: 파일 맨 앞의 보이지 않는 문자(BOM)를 자동으로 제거
    return pd.read_csv(CSV_PATH, encoding="utf-8-sig")


st.title("📊 영업팀 매출 현황")

# ---------------- 안전장치 1: 데이터 파일이 있는지 확인 ----------------
if not CSV_PATH.exists():
    st.error(
        f"데이터 파일 '{CSV_PATH.name}'을(를) 찾을 수 없습니다.\n\n"
        f"찾은 위치: {CSV_PATH.parent}\n\n"
        "파일 이름이 맞는지, app.py와 같은 폴더에 있는지 확인한 뒤 새로고침해 주세요."
    )
    st.stop()  # 아래 코드는 실행하지 않음

# 파일은 있지만 비어 있거나 CSV 형식이 아니면 읽다가 오류가 남 → 빨간 오류 대신 안내
try:
    df = load_data(CSV_PATH.stat().st_mtime)
except pd.errors.EmptyDataError:  # 파일 안에 아무 내용도 없음
    st.error(f"'{CSV_PATH.name}' 파일이 비어 있습니다. 데이터가 들어 있는 파일로 바꾼 뒤 새로고침해 주세요.")
    st.stop()
except (UnicodeDecodeError, pd.errors.ParserError):  # 한글이 깨졌거나 CSV 모양이 아님
    st.error(
        f"'{CSV_PATH.name}' 파일을 읽을 수 없습니다. "
        "엑셀에서 '다른 이름으로 저장 → CSV UTF-8(쉼표로 분리)'로 다시 저장한 뒤 새로고침해 주세요."
    )
    st.stop()

# ---------------- 안전장치 2: 필요한 열이 모두 있는지 확인 ----------------
df.columns = df.columns.str.strip()  # 열 이름 앞뒤의 실수로 들어간 공백 제거 (" sales" → "sales")
missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]  # 없는 열만 모으기
if missing:
    st.error(
        f"데이터 파일에 필요한 열이 없습니다: {', '.join(missing)}\n\n"
        f"필요한 열: {', '.join(REQUIRED_COLUMNS)}\n\n"
        "CSV 첫 줄(열 이름)에 위 열을 추가하거나 이름을 맞춘 뒤 새로고침해 주세요."
    )
    st.stop()

# ---------------- 안전장치 3: 값이 이상한 행 걸러내기 ----------------
total_rows = len(df)  # 걸러내기 전 전체 행 수
df["date"] = pd.to_datetime(df["date"], errors="coerce")  # 날짜로 못 바꾸는 값은 빈칸(NaT)으로
df["sales"] = pd.to_numeric(df["sales"], errors="coerce")  # 숫자로 못 바꾸는 값은 빈칸(NaN)으로
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df = df.dropna(subset=REQUIRED_COLUMNS)  # 필요한 칸 중 하나라도 비어 있는 행은 뺌
skipped = total_rows - len(df)  # 빠진 행 수

if df.empty:
    st.error("데이터 파일에 쓸 수 있는 행이 하나도 없습니다. 날짜·매출 칸에 올바른 값이 들어 있는지 확인해 주세요.")
    st.stop()
if skipped > 0:  # 일부만 문제면 화면은 그대로 보여 주고 알려만 줌
    st.info(f"값이 비어 있거나 잘못된 {skipped}개 행은 제외했습니다. 정확한 결과가 필요하면 CSV에서 해당 행을 고쳐 주세요.")

# ---------------- 왼쪽 사이드바: 필터 ----------------
st.sidebar.header("필터")

# 지역 선택 (여러 개 고를 수 있음, 처음엔 전체 선택)
regions = sorted(df["region"].astype(str).unique())  # astype(str): 숫자가 섞여 있어도 정렬 오류가 안 나게 모두 글자로
df["region"] = df["region"].astype(str)
selected_regions = st.sidebar.multiselect("지역", regions, default=regions)

# 카테고리 선택 (드롭다운에서 하나만 고름, 맨 앞에 '전체' 추가)
df["category"] = df["category"].astype(str)
categories = ["전체"] + sorted(df["category"].unique())  # ['전체', '생활용품', '식품', ...]
selected_category = st.sidebar.selectbox("카테고리", categories)  # 처음엔 맨 앞의 '전체'가 선택됨

# 기간 선택 (슬라이더 양쪽 손잡이로 시작일·종료일을 고름)
min_date = df["date"].min().date()  # 데이터의 첫 날짜
max_date = df["date"].max().date()  # 데이터의 마지막 날짜
if min_date == max_date:  # 날짜가 하루뿐이면 슬라이더를 만들 수 없으므로 글자로만 표시
    st.sidebar.caption(f"기간: {min_date} (데이터가 하루치뿐입니다)")
    start_date, end_date = min_date, max_date
else:
    start_date, end_date = st.sidebar.slider(
        "기간",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),  # 값을 두 개 주면 범위를 고르는 슬라이더가 됨 (처음엔 전체 기간)
        format="YYYY-MM-DD",  # 슬라이더에 날짜를 2026-01-01 형태로 표시
    )

# ---------------- 조건으로 거르기 → filtered ----------------
condition = (
    df["region"].isin(selected_regions)  # 조건 1: 선택한 지역 안에 있음
    & (df["date"].dt.date >= start_date)  # 조건 2: 시작일 이후
    & (df["date"].dt.date <= end_date)  # 조건 3: 종료일 이전
)
if selected_category != "전체":  # '전체'가 아닐 때만 카테고리 조건을 추가
    condition = condition & (df["category"] == selected_category)  # 조건 4: 고른 카테고리와 같음

filtered = df[condition]  # 모든 조건이 True인 행만 남김 → 아래 지표·그래프·표는 전부 이것을 씀

# 필터 아래에 몇 건이 골라졌는지 표시
st.sidebar.markdown(f"**선택 조건: {len(filtered):,}건 / 전체 {len(df):,}건**")

# ---------------- 안전장치 4: 조건에 맞는 데이터가 0건이면 지표·그래프·표를 그리지 않음 ----------------
if filtered.empty:
    st.warning("선택한 조건에 맞는 데이터가 없습니다. 왼쪽에서 지역을 더 고르거나 기간을 늘려 조건을 넓혀 보세요.")
    st.stop()  # 아래 코드는 실행하지 않음

# ---------------- 위: 핵심 지표 ----------------
total_sales = filtered["sales"].sum()  # 지표 1: 매출 합계
order_count = len(filtered)  # 지표 2: 행 1개 = 주문 1건
avg_order = total_sales / order_count  # 지표 3: 주문 1건당 평균 매출

col1, col2, col3 = st.columns(3)  # 화면을 세 칸으로 나눔
col1.metric("총 매출", f"{total_sales:,.0f}원")  # 천 단위 쉼표 표시, 소수점 없이
col2.metric("주문 건수", f"{order_count:,}건")
col3.metric("평균 주문 금액", f"{avg_order:,.0f}원")  # .0f: 소수점 없이 반올림

st.divider()  # 구분선

# ---------------- 가운데: 그래프 2개 (나란히) ----------------
left, right = st.columns(2)  # 그래프를 왼쪽·오른쪽에 나란히 놓기 위해 두 칸으로 나눔

with left:  # 왼쪽 칸에 들어갈 내용
    st.subheader("월별 매출")
    monthly = (
        filtered.groupby(filtered["date"].dt.strftime("%Y-%m"))["sales"]  # "2026-01" 형태로 월별 묶기
        .sum()
        .rename("매출")
    )
    monthly.index.name = "월"
    st.line_chart(monthly)  # 시간에 따른 흐름이 잘 보이도록 선그래프로 표시

with right:  # 오른쪽 칸에 들어갈 내용
    st.subheader("카테고리별 매출")
    by_category = (
        filtered.groupby("category")["sales"]  # 카테고리끼리 묶기
        .sum()
        .rename("매출")
    )
    by_category.index.name = "카테고리"
    st.bar_chart(by_category)  # 카테고리끼리 크기를 비교하기 좋은 막대그래프

st.divider()

# ---------------- 아래: 상세 표 ----------------
st.subheader("상세 데이터")
table = filtered.sort_values("date").copy()  # 날짜순 정렬
table["date"] = table["date"].dt.strftime("%Y-%m-%d")  # 시간 없이 날짜만 보이게
table = table.rename(
    columns={"date": "날짜", "region": "지역", "category": "카테고리", "sales": "매출(원)", "quantity": "수량"}
)
st.dataframe(table, use_container_width=True, hide_index=True)  # 표 너비를 화면에 맞춤
