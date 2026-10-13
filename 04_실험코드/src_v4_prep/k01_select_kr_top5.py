# -*- coding: utf-8 -*-
"""
k01_select_kr_top5.py — v4 준비: 한국 대형 개별주 5종목 선정 및 데이터 수집 (v2)
=================================================================================
선정 규칙 (계획서 v4 §3, 사전 고정)
  1) 2017-01-02 기준 KOSPI 상장 '보통주'를 시가총액 순으로 나열
     (우선주 제외: 종목코드 끝자리가 0이 아니거나 종목명이 '우', '우B' 등으로 끝남. ETF/ETN/리츠는 KOSPI 시총표에 없음)
  2) 위에서부터 차례로 보며, 2017-01-02 이전 거래일 수가 252일 이상인 종목만 채택 (미만이면 다음 순위로 대체)
  3) 5종목이 찰 때까지 반복
데이터: FinanceDataReader 일별 종가, 2015-01-01 ~ 2026-09-22 (미국 데이터와 같은 종료일)
        pykrx 종가와 교차 대조, 하루 |로그수익률| > 0.36 (가격제한폭 30% 초과) 이면 액면분할 미반영 의심으로 표시
시가총액 순위 출처 (위에서부터 먼저 되는 것 사용)
  - 1순위: pykrx.stock.get_market_cap("20170102", market="KOSPI")
  - 2순위: FinanceData/marcap 저장소의 KRX 일별 시가총액 기록 data/raw_v4/marcap-2017.parquet
           (github.com/FinanceData/marcap, KRX 공시 일별 시가총액을 연도별로 보관. sha256을 kr_source_log.txt에 기록)
  - 3순위: pykrx·marcap 모두 실패하면: KRX 정보데이터시스템(data.krx.co.kr) [통계 > 기본통계 > 주식 > 종목시세 > 전종목 시세]에서
    조회일 2017-01-02, 시장 KOSPI로 CSV를 내려받아 data/raw_v4/krx_marketcap_20170102.csv 로 저장한 뒤 다시 실행
출력 (data/raw_v4/)
  kr_top5_selection.csv   선정 근거 (상위 30개 순위, 우선주 여부, 이력 일수, 채택 여부)
  kr_fdr_{code}.parquet   선정 종목 일별 데이터
  kr_crosscheck.csv       FDR vs pykrx 대조, 분할 의심 일자
  kr_source_log.txt       시가총액 순위를 어디서 가져왔는지 기록
주의: 모델을 돌리지 않는다. 결과 해석 금지.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw_v4"
OUT.mkdir(parents=True, exist_ok=True)

BASE_DATE = "20170102"
BASE_TS = pd.Timestamp("2017-01-02")
START, END = "2015-01-01", "2026-09-22"
MIN_HISTORY = 252
MANUAL_CSV = OUT / "krx_marketcap_20170102.csv"
MARCAP = OUT / "marcap-2017.parquet"


def is_preferred(code: str, name: str) -> bool:
    return code[-1] != "0" or bool(re.search(r"우[A-Z]?$|\d우[A-Z]?$|우\(전환\)$", name))


def load_ranking():
    """(code, name, market_cap) 시가총액 내림차순 DataFrame과 출처 문자열."""
    try:
        from pykrx import stock
        cap = stock.get_market_cap(BASE_DATE, market="KOSPI")
        if cap is None or len(cap) == 0:
            raise RuntimeError("pykrx 결과가 비어 있음")
        cap = cap.sort_values("시가총액", ascending=False).head(60)
        rows = [{"code": c, "name": stock.get_market_ticker_name(c), "market_cap": int(r["시가총액"])}
                for c, r in cap.iterrows()]
        return pd.DataFrame(rows), "pykrx.get_market_cap(20170102, KOSPI)"
    except Exception as e:  # noqa: BLE001
        err = f"pykrx 실패: {type(e).__name__}: {e}"
        print(err)
        if MARCAP.exists():
            import hashlib
            m = pd.read_parquet(MARCAP)
            d = m[(pd.to_datetime(m["Date"]) == BASE_TS) & (m["Market"] == "KOSPI")]
            if len(d):
                d = d.sort_values("Marcap", ascending=False).head(60)
                out = pd.DataFrame({"code": d["Code"].astype(str).str.zfill(6), "name": d["Name"],
                                    "market_cap": d["Marcap"].astype("int64")}).reset_index(drop=True)
                sha = hashlib.sha256(MARCAP.read_bytes()).hexdigest()
                return out, f"FinanceData/marcap {MARCAP.name} (sha256 {sha}); {err}"
        if not MANUAL_CSV.exists():
            raise SystemExit(
                err + f"\n→ KRX 정보데이터시스템에서 2017-01-02 KOSPI 전종목 시세 CSV를 받아\n   {MANUAL_CSV} 로 저장 후 재실행하세요."
            )
        df = None
        for enc in ("cp949", "utf-8-sig", "utf-8"):
            try:
                df = pd.read_csv(MANUAL_CSV, encoding=enc, dtype=str)
                break
            except Exception:  # noqa: BLE001
                continue
        col = {c: c.strip() for c in df.columns}
        df = df.rename(columns=col)
        code_col = next(c for c in df.columns if "종목코드" in c or "단축코드" in c)
        name_col = next(c for c in df.columns if "종목명" in c)
        cap_col = next(c for c in df.columns if "시가총액" in c)
        out = pd.DataFrame({
            "code": df[code_col].str.zfill(6),
            "name": df[name_col],
            "market_cap": pd.to_numeric(df[cap_col].str.replace(",", ""), errors="coerce"),
        }).dropna().sort_values("market_cap", ascending=False).head(60)
        return out.reset_index(drop=True), f"수동 CSV: {MANUAL_CSV.name} ({err})"


def main():
    import FinanceDataReader as fdr
    rank, source = load_ranking()
    (OUT / "kr_source_log.txt").write_text(source + "\n", encoding="utf-8")
    print("[순위 출처]", source)

    rank["preferred"] = [is_preferred(c, n) for c, n in zip(rank["code"], rank["name"])]
    rank["history_days_before_base"] = np.nan
    rank["selected"] = False
    selected, frames = [], {}
    for i, r in rank.iterrows():
        if len(selected) == 5:
            break
        if r["preferred"]:
            continue
        f = fdr.DataReader(r["code"], START, END)
        f.columns = [str(c).lower() for c in f.columns]
        n_before = int((f.index < BASE_TS).sum())
        rank.loc[i, "history_days_before_base"] = n_before
        if n_before >= MIN_HISTORY:
            rank.loc[i, "selected"] = True
            selected.append((r["code"], r["name"]))
            frames[r["code"]] = f
    rank.head(30).to_csv(OUT / "kr_top5_selection.csv", index=False, encoding="utf-8-sig")
    print("[선정]\n", rank[rank["selected"]][["code", "name", "market_cap", "history_days_before_base"]].to_string(index=False))

    checks = []
    try:
        from pykrx import stock
    except Exception:  # noqa: BLE001
        stock = None
    for code, name in selected:
        f = frames[code]
        f.to_parquet(OUT / f"kr_fdr_{code}.parquet")
        lr = np.log(f["close"].astype(float)).diff().abs()
        jumps = lr[lr > 0.36]
        row = {"code": code, "name": name, "fdr_days": len(f),
               "first": str(f.index.min().date()), "last": str(f.index.max().date()),
               "suspect_jumps": ";".join(f"{d.date()}:{v:.2f}" for d, v in jumps.items())}
        if stock is not None:
            try:
                p = stock.get_market_ohlcv(START.replace("-", ""), END.replace("-", ""), code)
                pc = p["종가"].astype(float)
                j = pd.concat([f["close"].astype(float), pc], axis=1, keys=["fdr", "pykrx"]).dropna()
                diff = ((j["fdr"] / j["pykrx"]) - 1).abs()
                row.update({"pykrx_days": len(pc), "days_diff_gt_0.1pct": int((diff > 0.001).sum()),
                            "max_rel_diff": float(diff.max()),
                            "missing_in_fdr": int(len(pc.index.difference(f.index)))})
            except Exception as e:  # noqa: BLE001
                row["pykrx_check"] = f"실패: {type(e).__name__}: {e}"
        if MARCAP.exists():
            m = pd.read_parquet(MARCAP, columns=["Code", "Date", "Close"])
            mc = m[m["Code"].astype(str).str.zfill(6) == code].set_index(pd.to_datetime(m.loc[m["Code"].astype(str).str.zfill(6) == code, "Date"]))["Close"].astype(float)
            jj = pd.concat([f["close"].astype(float), mc], axis=1, keys=["fdr", "marcap"]).dropna()
            dd = ((jj["fdr"] / jj["marcap"]) - 1).abs()
            row.update({"marcap2017_days": len(jj), "marcap2017_days_diff_gt_0.1pct": int((dd > 0.001).sum()),
                        "marcap2017_max_rel_diff": float(dd.max()) if len(dd) else None})
        checks.append(row)
    pd.DataFrame(checks).to_csv(OUT / "kr_crosscheck.csv", index=False, encoding="utf-8-sig")
    print("[대조]\n", pd.DataFrame(checks).to_string(index=False))


if __name__ == "__main__":
    main()
