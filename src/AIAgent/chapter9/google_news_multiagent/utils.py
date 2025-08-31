from datetime import datetime, timedelta
import re


def clean_html(html_text: str) -> str:
    """HTML 태그 제거"""
    if not html_text:
        return ""

    # ① 정규표현식으로 HTML 태그 제거: <태그명>내용</태그명> 패턴 매칭
    clean_text = re.sub("<.*?>", "", html_text)
    # ② 연속된 공백(스페이스, 탭, 줄바꿈)을 하나의 공백으로 정리
    clean_text = re.sub("\s+", " ", clean_text).strip()
    return clean_text


def truncate_text(text: str, max_length: int = 500) -> str:
    """텍스트를 적절한 길이로 자르기"""
    if not text or len(text) <= max_length:
        return text
    # ③ 지정된 길이로 자르고 말줄임표(...) 추가
    return text[:max_length] + "..."


def convert_gmt_to_kst(gmt_time_str: str) -> str:
    # ④ GMT 시간을 KST로 변환
    """GMT 시간을 KST로 변환합니다."""
    KST_OFFSET_HOURS = 9
    gmt_time = datetime.strptime(gmt_time_str, "%a, %d %b %Y %H:%M:%S GMT")
    kst_time = gmt_time + timedelta(hours=KST_OFFSET_HOURS)
    return kst_time.strftime("%Y-%m-%d %H:%M:%S")
