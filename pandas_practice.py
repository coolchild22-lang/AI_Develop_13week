from pathlib import Path  # 파일 경로를 다루는 파이썬 기본 도구 (따로 설치 필요 없음)

import pandas as pd  # 표 형태 데이터를 다루는 라이브러리

# 이 .py 파일이 있는 폴더 기준으로 CSV 위치를 정함 → 어느 폴더에서 실행해도 파일을 찾을 수 있음
CSV_PATH = Path(__file__).parent / "sales_sample.csv"

# CSV 파일 불러오기 (utf-8-sig: 파일 맨 앞 숨은 문자(BOM) 제거)
df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

# 1. 행·열 개수
print("=== 1. 행·열 개수 ===")
rows, cols = df.shape  # shape는 (행 개수, 열 개수)를 알려 줌
print(f"행: {rows}개, 열: {cols}개")
print()

# 2. 열 이름과 자료형
print("=== 2. 열 이름과 자료형 ===")
print(df.dtypes)  # 각 열이 숫자(int64)인지 글자(object)인지 보여 줌
print()

# 3. 빈칸 개수
print("=== 3. 열별 빈칸 개수 ===")
print(df.isnull().sum())  # 빈칸이면 True(1)로 바꾼 뒤 열마다 더함
print()

# 4. 숫자 열 요약
print("=== 4. 숫자 열 요약 ===")
pd.set_option("display.float_format", "{:,.1f}".format)  # 3.789027e+05 같은 지수 표기 대신 378,902.7처럼 표시
print(df.describe())  # 개수, 평균, 표준편차, 최솟값, 사분위수, 최댓값
print()

# 5. 조건으로 거르기: 서울 지역 + 매출 10만 원 이상
print("=== 5. 서울 지역, 매출 10만 원 이상 주문 ===")
is_seoul = df["region"] == "서울"  # 지역이 서울이면 True, 아니면 False
is_big = df["sales"] >= 100000  # 매출이 10만 원 이상이면 True, 아니면 False
seoul_big = df[is_seoul & is_big]  # 두 조건이 모두 True인 행만 남김 (&는 '그리고')
print(f"주문 건수: {len(seoul_big)}건")  # 남은 행의 개수 = 주문 건수
