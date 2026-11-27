# 대시보드의 "총 매출" 지표를 엑셀로 검산하는 파일을 만드는 연습용 코드
from pathlib import Path  # 파일 경로를 다루는 파이썬 기본 도구

import pandas as pd  # 표 형태 데이터를 다루는 라이브러리

FOLDER = Path(__file__).parent  # 이 .py 파일이 있는 폴더
df = pd.read_csv(FOLDER / "sales_sample.csv", encoding="utf-8-sig")

# 대시보드와 똑같은 방법(pandas)으로 계산한 총 매출 (필터: 전체 지역, 전체 기간)
python_total = int(df["sales"].sum())
last_row = len(df) + 1  # 엑셀은 1행이 제목이라 데이터는 2행 ~ 151행

# 원본 데이터 오른쪽(G·H열)에 검산 칸을 붙임. "="로 시작하는 글자는 엑셀이 수식으로 계산함
check = pd.DataFrame(
    {
        "검산 항목": ["① 엑셀 계산 (SUM 수식)", "② 대시보드 값 (pandas)", "③ 차이 (①-②)", "④ 결과"],
        "값": [
            f"=SUM(D2:D{last_row})",  # 엑셀이 매출 열(D열)을 직접 더함
            python_total,  # 파이썬이 계산한 값을 숫자로 적어 둠
            "=H2-H3",  # 두 값의 차이 → 0이면 같음
            '=IF(H4=0,"일치","불일치")',  # 차이가 0이면 "일치" 표시
        ],
    }
)

# 원본 데이터(A~E열) + 빈 열(F) + 검산 칸(G~H열)을 옆으로 붙이기
sheet = pd.concat([df, pd.DataFrame({"": [""] * len(df)}), check], axis=1)

out_path = FOLDER / "총매출_검산.csv"
sheet.to_csv(out_path, index=False, encoding="utf-8-sig")  # utf-8-sig: 엑셀에서 한글이 안 깨지게 함

print(f"파이썬 총 매출: {python_total:,}원")
print(f"검산 파일 저장: {out_path}")
