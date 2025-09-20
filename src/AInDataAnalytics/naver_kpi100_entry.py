import pandas as pd
import requests

def save_naver_index_stocks_to_excel(code='KPI100'):
    """
    네이버 증권 지수 페이지의 '편입 종목 상위' 테이블 정보를 엑셀 파일로 저장합니다.
    
    Args:
        code (str): 지수 코드 (예: 'KPI100' for 코스피100, 'KOSDAQ' for 코스닥 등)
    """
    try:
        # 1. '편입 종목 상위' 테이블이 포함된 iframe URL
        # 이 URL은 메인 페이지 소스에서 iframe 태그를 분석하여 찾았습니다.
        url = f"https://finance.naver.com/sise/entryJongmok.naver?type={code}"

        # 2. 크롤링 차단을 피하기 위한 User-Agent 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        
        # 3. HTTP GET 요청 보내기
        response = requests.get(url, headers=headers)
        response.raise_for_status() # 요청이 실패하면 예외 발생

        # 4. pandas의 read_html을 사용하여 HTML 테이블을 DataFrame으로 읽어오기
        # 네이버 금융은 'euc-kr' 인코딩을 사용합니다.
        # read_html은 페이지의 모든 테이블을 리스트 형태로 반환합니다.
        tables = pd.read_html(response.text, encoding='euc-kr')
        
        # 5. 원하는 테이블 선택 및 데이터 정제
        # 해당 페이지에는 테이블이 하나만 존재하므로, 첫 번째 테이블(tables[0])을 선택합니다.
        df = tables[0]
        
        # 6. 불필요한 NaN 행 제거 (read_html이 생성하는 빈 줄 제거)
        df_cleaned = df.dropna(how='all').reset_index(drop=True)
        
        # '종목명' 열의 데이터 타입을 문자열로 변경 (숫자로 시작하는 종목명 오류 방지)
        if '종목명' in df_cleaned.columns:
            df_cleaned['종목명'] = df_cleaned['종목명'].astype(str)

        # 7. 엑셀 파일로 저장
        # index=False 옵션으로 DataFrame의 인덱스가 엑셀에 저장되는 것을 방지합니다.
        filename = f"{code}_top_stocks.xlsx"
        df_cleaned.to_excel(filename, index=False)
        
        print(f"성공! '{filename}' 파일이 현재 폴더에 저장되었습니다.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 에러가 발생했습니다: {e}")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

# --- 코드 실행 ---
if __name__ == "__main__":
    # 코스피100 편입 종목 상위 정보를 가져옵니다.
    save_naver_index_stocks_to_excel('KPI100')

    # # 다른 지수(예: 코스닥)를 가져오고 싶다면 아래처럼 호출하세요.
    # save_naver_index_stocks_to_excel('KOSDAQ')