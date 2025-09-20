import pandas as pd
import requests
from io import StringIO
import time # 지연 시간을 위한 time 라이브러리 추가

def save_all_pages_to_excel(code='KPI100', total_pages=10):
    """
    네이버 증권 지수 페이지의 '편입 종목' 테이블 전체 페이지 정보를 엑셀 파일로 저장합니다.
    
    Args:
        code (str): 지수 코드 (예: 'KPI100' for 코스피100, 'KOSDAQ' for 코스닥 등)
        total_pages (int): 크롤링할 전체 페이지 수
    """
    try:
        # 모든 페이지의 DataFrame을 저장할 빈 리스트 생성
        all_data_frames = []

        # 1. 1페이지부터 total_pages까지 반복
        for page in range(1, total_pages + 1):
            
            # 2. 각 페이지에 맞는 URL 동적 생성
            url = f"https://finance.naver.com/sise/entryJongmok.naver?type={code}&page={page}"
            
            # 3. 크롤링 진행 상황 출력
            print(f"'{code}' 지수의 {page}/{total_pages} 페이지를 크롤링 중입니다...")

            # 4. 크롤링 차단을 피하기 위한 User-Agent 설정
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # 5. 현재 페이지의 테이블을 DataFrame으로 읽어오기
            tables = pd.read_html(StringIO(response.text), encoding='euc-kr')
            df_page = tables[0]
            
            # 6. 불필요한 NaN 행 제거 및 리스트에 추가
            df_cleaned = df_page.dropna(how='all')
            all_data_frames.append(df_cleaned)
            
            # 7. 서버에 부담을 주지 않기 위해 약간의 지연 시간 부여
            time.sleep(0.5)

        # 8. 리스트에 저장된 모든 DataFrame을 하나로 병합
        if not all_data_frames:
            print("크롤링된 데이터가 없습니다.")
            return

        combined_df = pd.concat(all_data_frames, ignore_index=True)

        # '종목명' 열의 데이터 타입을 문자열로 변경
        if '종목명' in combined_df.columns:
            combined_df['종목명'] = combined_df['종목명'].astype(str)

        # 9. 최종 결과를 엑셀 파일로 저장
        filename = f"{code}_all_stocks.xlsx"
        combined_df.to_excel(filename, index=False)
        
        print(f"\n성공! 총 {len(combined_df)}개의 종목 정보가 '{filename}' 파일에 저장되었습니다.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 에러가 발생했습니다: {e}")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

# --- 코드 실행 ---
if __name__ == "__main__":
    # 코스피100 편입 종목 전체(10페이지) 정보를 가져옵니다.
    save_all_pages_to_excel(code='KPI100', total_pages=10)

    # # 만약 다른 지수(예: 코스닥)를 가져오고 싶다면 아래처럼 호출하세요.
    # # 코스닥은 페이지 수가 다를 수 있으니, 네이버 증권 페이지에서 직접 확인 후 total_pages를 조절하세요.
    # save_all_pages_to_excel(code='KOSDAQ', total_pages=34) # 예시: 코스닥이 34페이지인 경우