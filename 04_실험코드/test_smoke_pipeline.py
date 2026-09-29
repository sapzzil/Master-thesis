# -*- coding: utf-8 -*-
"""
test_smoke_pipeline.py
======================
전체 01~04 파이프라인 30초 무결점 관통 스모크 테스트 (Smoke Test)

검증 순서:
1. 01_generate_finstress_3axis.py --smoke (합성 데이터 15개 시나리오 생성)
2. 02_run_zeroshot_inference.py --model all_tier1 --target both --smoke (GPU 추론)
3. 03_compute_metrics.py (불편추정 CRPS / 커버리지 / PIT 산출)
4. 04_analyze_results.py (Table 1, Figure 1 렌더링)
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PYTHON = sys.executable

def run_step(step_name, cmd):
    print(f"\n[스모크 단계] {step_name} 실행 중...")
    t0 = time.time()
    res = subprocess.run([PYTHON] + cmd, cwd=str(SRC), capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"  [FAIL] {step_name} 에러 발생! (코드: {res.returncode})")
        print(res.stderr)
        sys.exit(res.returncode)
    print(f"  [PASS] {step_name} 정상 완료 ({elapsed:.2f}초)")
    return elapsed

def main():
    print("=" * 68)
    print(" [전체 파이프라인 30초 무결점 관통 스모크 테스트 가동]")
    print(f" Python 인터프리터: {PYTHON}")
    print("=" * 68)

    t_total_start = time.time()

    # 1단계: 합성 데이터 생성 스모크
    run_step("1단계: 합성 데이터 생성", ["01_generate_finstress_3axis.py", "--smoke"])

    # 2단계: 다중 모델 추론 스모크 (Chronos-Tiny + Random Walk + GARCH-t)
    run_step("2단계: 다중 모델 추론 (Tier1)", ["02_run_zeroshot_inference.py", "--model", "all_tier1", "--target", "both", "--smoke"])

    # 3단계: 메트릭 산출 스모크
    run_step("3단계: 불편추정 CRPS/커버리지 산출", ["03_compute_metrics.py"])

    # 4단계: 가설 검정 및 Table/Figure 렌더링 스모크
    run_step("4단계: 통계 분석 및 그래프 렌더링", ["04_analyze_results.py"])

    total_elapsed = time.time() - t_total_start
    print("\n" + "=" * 68)
    print(f" [SUCCESS] [스모크 테스트 100% 무결점 통과!] 총 소요시간: {total_elapsed:.2f}초")
    print(f" 산출물 위치: {ROOT / 'results'}")
    print("=" * 68)


if __name__ == "__main__":
    main()
