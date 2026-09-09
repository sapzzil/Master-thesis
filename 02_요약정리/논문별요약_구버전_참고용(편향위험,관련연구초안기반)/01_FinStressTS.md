# FinStressTS: A Parametric Synthetic Benchmark for Time-Series Forecasting in Finance

- **서지**: Jiaze Sun, Kelvin J.L. Koa 외 (NUS/NTU), arXiv:2606.03184, KDD'26
- **위협도**: 최상 (핵심 대조 대상, 인용 필수)
- **원문(한글역)**: `01_자료원문_ko/01_2606.03184_FinStressTS_Synthetic_Benchmark.md`
- **근거 문서**: `03_최종취합/관련연구_초안.md` §4 전체, `02_요약정리/하위갈래C`

## 한 줄 요약
금융 시계열의 6개 고전 계량경제학적 메커니즘(GARCH 변동성군집·HAR 다중스케일지속성·
Student-t 두꺼운꼬리·Markov 체제전환·Hawkes 자기흥분점프·ZIP 희소활동)을 각 5단계로
파라미터화해 30개(6×5) 독립 진단환경을 만든 합성 벤치마크. 15개 모델을 평가하지만
**전부 from-scratch로 학습된 모델**이며 사전학습 zero-shot TSFM은 단 하나도 다루지 않는다.

## 문제의식
실제 금융데이터는 단 하나의 실현경로만 관측되므로, 모델이 실패했을 때 그 원인(분포
오정렬인지, 체제변화 적응 실패인지, 데이터 부족인지)을 귀속시킬 수 없다. FinStressTS는
생성과정을 알고 있는 합성 환경으로 이 "attribution gap"을 해결하려 한다.

## 방법
- 6개 메커니즘 축 × 5단계 강도 = 30개 진단환경, 패널(N=50 계열, T=2,000)
- 점예측 과제: NMAE_σ(변동성 정규화 MAE) / 확률예측 과제: CRPS
- 15개 모델: 고전(AR/HAR/VAR), 신경망 점예측(DLinear/PatchTST/iTransformer/Autoformer/
  FEDformer/NonstationaryTransformer/TimeXer), 확률모델(DeepAR/TimeGrad/TSFlow/TimeMCL/
  RATD/QuantileFormer) — **전부 각 환경에서 처음부터 학습**
- data efficiency 학습곡선(n=100~1200)도 별도 측정

## 핵심 결과
1. 단순 AR/HAR/DLinear가 복잡한 Transformer를 꾸준히 이김 — 강건성이 표현력보다 중요
2. PatchTST(국소attention)가 iTransformer/TimeXer(전역 상호작용)보다 점프 환경에서 우세
3. Autoformer/FEDformer의 계절-추세 분해가 금융(약한 주기성)에서 오히려 발목 잡음
4. DeepAR이 24/30 세팅에서 최고 CRPS — 파라메트릭 정합성(GARCH와 구조적으로 동형)이 승리
5. 체제전환·ZIP처럼 다봉분포일 땐 TSFlow(flow 기반, 유연한 밀도)가 DeepAR을 역전
6. diffusion 기반 RATD는 매끈한 변동성엔 강하나 구조적 단절(체제전환·ZIP)엔 취약

## 결정적 공백 — 본 연구 기여①의 정확한 위치
원문 전체를 `TimesFM|Chronos|Moirai|Lag-Llama|TTM|TimeGPT|Kronos` 및 `zero-shot|pretrain`
로 검색해도 0건. "foundation model"이 1회 등장하나 이는 타 툴킷(ProbTS)을 설명하는
문장일 뿐 저자 실험이 아니다. → 사전학습 zero-shot TSFM을 이 6축 진단환경에 처음
투입하는 것이 본 연구 기여①이다.

## 사용 금지 근거(검증 결과 거짓)
"FinStressTS 저자가 Limitations에서 사전학습 모델의 취약점 상속을 미해결 과제로
명시했다" → **거짓**(원문 재확인 결과 Limitations 4개 항목 중 사전학습 관련 언급 없음).

## 재사용(코드) 시 유의점
- 6개 축이 완전히 독립적이지 않음(GARCH·HAR·두꺼운꼬리는 변동성 골격 공유, 체제전환·
  Hawkes·ZIP은 시장공통 잠재과정 골격 공유)
- Case1(GARCH)의 ceteris paribus 전제가 실제로 깨져 있음(Level2/3이 여러 파라미터를
  동시에 바꿈)
- 논문 본문(T=2,000)과 배포 코드 `presets.py`(T=20,000) 사이 10배 표본길이 불일치 —
  본 실험에서 어느 쪽을 따를지 명시적으로 결정하고 근거를 기록할 것
- Limitations에서 "복합 스트레스 지원"을 주장하나 실제 배포 30개 환경은 전부 단일
  메커니즘만 구현(논문-코드 괴리, 우리의 다축 조합 차별점 논거로 활용 가능)
