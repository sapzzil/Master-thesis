"""
데이터 경로 진단 + 스냅샷 확보
================================
목적: pykrx / FinanceDataReader / yfinance 중 어느 경로가 살아있는지 확인하고,
      살아있는 경로로 한국·미국 데이터를 로컬 parquet으로 고정한다.

배경: pykrx가 2026-02-27 이후 KRX 로그인(KRX_ID/KRX_PW 환경변수)을 요구하도록 변경됨.
      데이터 소스가 죽으면 논문이 멈추므로 조기 확보 후 로컬 캐싱이 필수.

실행: python 00_data_check.py
출력: 04_실험코드/data/raw/*.parquet  +  콘솔 진단 리포트
"""

import os
import sys
import traceback
from pathlib import Path
from datetime import datetime

import pandas as pd

# ----------------------------------------------------------------------
# 설정
# ----------------------------------------------------------------------
START = "2015-01-01"
END = datetime.today().strftime("%Y-%m-%d")

KR_TICKERS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "005380": "현대차",
    "035420": "NAVER",
    "068270": "셀트리온",
}
US_TICKERS = ["AAPL", "MSFT", "JPM", "XOM", "SPY"]

ROOT = Path(__file__).resolve().parents[1]     # 04_실험코드/
OUT = ROOT / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

results = {}


def report(name, ok, detail=""):
    mark = "OK  " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f"  |  {detail}" if detail else ""))
    results[name] = ok


def section(title):
    print("\n" + "=" * 68)
    print(f" {title}")
    print("=" * 68)


# ----------------------------------------------------------------------
# 1) pykrx
# ----------------------------------------------------------------------
def try_pykrx():
    section("1) pykrx  (KRX 직접)")
    has_cred = bool(os.getenv("KRX_ID") and os.getenv("KRX_PW"))
    print(f"  KRX 자격증명 환경변수: {'있음' if has_cred else '없음'}")
    if not has_cred:
        print("  → data.krx.co.kr 회원가입 후 아래처럼 설정하면 됩니다(무료):")
        print('     setx KRX_ID "your_id"')
        print('     setx KRX_PW "your_pw"')

    try:
        from pykrx import stock
    except ImportError:
        report("pykrx import", False, "pip install pykrx")
        return None

    frames = {}
    try:
        for code, name in KR_TICKERS.items():
            df = stock.get_market_ohlcv(
                START.replace("-", ""), END.replace("-", ""), code
            )
            if df is None or df.empty:
                raise RuntimeError(f"{code} 빈 응답")
            df = df.rename(columns={
                "시가": "open", "고가": "high", "저가": "low",
                "종가": "close", "거래량": "volume",
            })
            frames[code] = df[["open", "high", "low", "close", "volume"]]
        report("pykrx OHLCV", True, f"{len(frames)}종목")
        return frames
    except Exception as e:
        report("pykrx OHLCV", False, f"{type(e).__name__}: {str(e)[:90]}")
        return None


# ----------------------------------------------------------------------
# 2) FinanceDataReader
# ----------------------------------------------------------------------
def try_fdr():
    section("2) FinanceDataReader  (네이버 경유)")
    try:
        import FinanceDataReader as fdr
    except ImportError:
        report("FDR import", False, "pip install finance-datareader")
        return None
    except Exception as e:
        report("FDR import", False, f"{type(e).__name__}: {str(e)[:90]}")
        return None

    frames = {}
    try:
        for code, name in KR_TICKERS.items():
            df = fdr.DataReader(code, START, END)
            if df is None or df.empty:
                raise RuntimeError(f"{code} 빈 응답")
            df.columns = [c.lower() for c in df.columns]
            frames[code] = df
        report("FDR 한국 OHLCV", True, f"{len(frames)}종목")
    except Exception as e:
        report("FDR 한국 OHLCV", False, f"{type(e).__name__}: {str(e)[:90]}")
        return None

    try:
        ks = fdr.DataReader("KS11", START, END)
        ks.columns = [c.lower() for c in ks.columns]
        frames["KS11"] = ks
        report("FDR KOSPI 지수", True, f"{len(ks)}행")
    except Exception as e:
        report("FDR KOSPI 지수", False, f"{type(e).__name__}: {str(e)[:90]}")

    return frames


# ----------------------------------------------------------------------
# 3) yfinance (한국 .KS / 미국)
# ----------------------------------------------------------------------
def try_yfinance():
    section("3) yfinance  (KRX 우회)")
    try:
        import yfinance as yf
    except ImportError:
        report("yfinance import", False, "pip install yfinance")
        return None, None

    kr, us = {}, {}
    try:
        for code in KR_TICKERS:
            t = f"{code}.KS"
            df = yf.download(t, start=START, end=END, progress=False, auto_adjust=False)
            if df is None or df.empty:
                raise RuntimeError(f"{t} 빈 응답")
            df.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower()
                          for c in df.columns]
            kr[code] = df
        report("yfinance 한국(.KS)", True, f"{len(kr)}종목")
    except Exception as e:
        report("yfinance 한국(.KS)", False, f"{type(e).__name__}: {str(e)[:90]}")
        kr = None

    try:
        for t in US_TICKERS:
            df = yf.download(t, start=START, end=END, progress=False, auto_adjust=False)
            if df is None or df.empty:
                raise RuntimeError(f"{t} 빈 응답")
            df.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower()
                          for c in df.columns]
            us[t] = df
        report("yfinance 미국", True, f"{len(us)}종목")
    except Exception as e:
        report("yfinance 미국", False, f"{type(e).__name__}: {str(e)[:90]}")
        us = None

    return kr, us


# ----------------------------------------------------------------------
# 저장
# ----------------------------------------------------------------------
def save(frames, prefix):
    if not frames:
        return 0
    n = 0
    for key, df in frames.items():
        try:
            path = OUT / f"{prefix}_{key}.parquet"
            df.to_parquet(path)
            n += 1
        except Exception as e:
            print(f"    저장 실패 {key}: {type(e).__name__}: {e}")
    return n


def main():
    print("\n" + "#" * 68)
    print("#  데이터 경로 진단 및 스냅샷 확보")
    print(f"#  기간: {START} ~ {END}")
    print(f"#  저장 위치: {OUT}")
    print("#" * 68)

    kr_pykrx = try_pykrx()
    kr_fdr = try_fdr()
    kr_yf, us_yf = try_yfinance()

    section("스냅샷 저장")
    saved = 0
    # 한국: 우선순위 pykrx > FDR > yfinance
    if kr_pykrx:
        saved += save(kr_pykrx, "kr_pykrx")
        print("  한국 주 경로: pykrx")
    elif kr_fdr:
        saved += save(kr_fdr, "kr_fdr")
        print("  한국 주 경로: FinanceDataReader")
    elif kr_yf:
        saved += save(kr_yf, "kr_yf")
        print("  한국 주 경로: yfinance (.KS)")
    else:
        print("  [경고] 한국 데이터 경로가 전부 실패했습니다.")

    # 백업본도 같이 저장 (경로별 비교 검증용)
    if kr_fdr and kr_pykrx:
        saved += save(kr_fdr, "kr_fdr")
    if kr_yf and (kr_pykrx or kr_fdr):
        saved += save(kr_yf, "kr_yf")
    if us_yf:
        saved += save(us_yf, "us_yf")

    print(f"\n  저장된 파일: {saved}개")

    section("요약")
    for k, v in results.items():
        print(f"  {'OK  ' if v else 'FAIL'}  {k}")

    ok_kr = any([kr_pykrx, kr_fdr, kr_yf])
    ok_us = bool(us_yf)
    print()
    print(f"  한국 데이터 확보: {'가능' if ok_kr else '실패 — 확인 필요'}")
    print(f"  미국 데이터 확보: {'가능' if ok_us else '실패 — 확인 필요'}")
    print()
    if ok_kr and ok_us:
        print("  → 다음 단계로 진행 가능합니다.")
    else:
        print("  → 위 FAIL 항목을 Claude에게 그대로 보여주세요.")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
