# Moirai / Moirai-MoE / Moirai 2.0

- **서지**: Woo et al. (Salesforce), arXiv:2402.02592(1.0, ICML'24) / 2410.10469(MoE) /
  2511.11698(2.0)
- **위협도**: 해당 없음(경쟁문헌 아님) — **우리 실험의 주 후보 모델**
- **원문(한글역)**: `01_자료원문_ko/03_2402.02592_Moirai_Unified_Training_Universal_TSF_Transformers.md`
  (Moirai-MoE·2.0은 08~09번 대신 배경자료로 남아있음, 아래 참고)
- **근거 문서**: `03_최종취합/관련연구_초안.md` §2.1~2.2, `02_요약정리/하위갈래A`

## 한 줄 요약(Moirai 1.0)
여러 주파수·변수 개수를 통일된 방식으로 다루는 마스크 인코더 트랜스포머. 확률적 출력은
Student-t·로그정규·음이항·저분산정규분포의 **가중 혼합(mixture of parametric
distributions)** 헤드로 직접 파라미터를 출력. LOTSA(대규모 공개 시계열 아카이브)로
사전학습.

## 확률적 출력 유형
하위갈래A 분류상 **"파라메트릭·혼합분포형"**(유형 ii). CRPS는 혼합분포에서 샘플링 후
경험적으로 계산하거나(원문 Appendix C.1에 CRPS 평가 절 존재, 세부 수식 미확인) 이론적
공식을 쓸 수도 있음.

## 사전학습 코퍼스와 금융 노출
Moirai 2.0·Toto 원문에서 각각 "GIFT-Eval Pretrain is a subset of LOTSA"(§4),
"the remaining points come from the LOTSA dataset"(§4)로 LOTSA 하위집합 사용이
직접 확인됨(3·4단계 재검증). **다만 "LOTSA가 Econ/Fin 23개 데이터셋·0.10%를 포함한다"는
구체적 수치는 Moirai 1.0 Table 2 재조회에 실패해 미확정 상태** — 5단계 착수 전 반드시
재확인. 그전까지는 "LOTSA를 통해 금융 시계열에 어느 정도 노출됐을 가능성이 있다"는
정성적 주장까지만 사용.

## Moirai-MoE(2410.10469)
백본만 sparse Mixture-of-Experts로 교체, 출력 헤드·손실함수는 Moirai 1.0과 동일
(원문이 직접 인용하며 명시).

## Moirai 2.0(2511.11698)
Moirai 1.0의 혼합분포 출력을 폐기하고 **분위수 예측(9개 분위수, pinball loss)으로
전면 교체**. "directly aligned with the CRPS metric through optimization with the
quantile loss"라고 원문이 명시 — 학습목적함수와 평가지표(CRPS)가 정합적인 드문 사례.

## 우리 연구와의 관계
스코프 단순화(진행상황.md)에서 Chronos와 함께 대상 TSFM 핵심 후보. 파일럿 코드
(`04_실험코드/src/06_pilot_moirai.py`) 이미 작성·파이프라인 검증 완료(2026-08-25).
LOTSA 기반이므로 look-ahead 누출 통제 범위를 Chronos 단독에서 Moirai 계열 전체로
확대해야 함(진행상황.md 리스크 3번).
