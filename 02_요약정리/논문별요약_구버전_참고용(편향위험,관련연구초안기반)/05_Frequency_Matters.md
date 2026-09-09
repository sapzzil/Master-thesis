# Frequency Matters: When Time Series Foundation Models Fail Under Spectral Shift

- **서지**: Tianze Wang 외 (King AI Labs / Microsoft Gaming), arXiv:2511.05619
- **위협도**: 높음 (다축 vs 단일축으로 차별화)
- **원문(한글역, 전문 수집)**: `01_자료원문_ko/05_2511.05619_Frequency_Matters_TSFM_Spectral_Shift.md`
- **근거 문서**: `02_요약정리/정독_선행연구3편.md` §2

## 한 줄 요약
게임(Candy Crush) 산업 규모 플레이어 참여예측(PEP) 과제에서 TSFM이 왜 저조한지를
"스펙트럴 시프트"(사전학습 때 못 본 주파수대역과 다운스트림 과제의 주파수대역 불일치)로
설명. MOMENT-small(frozen backbone + linear probing) 단 하나의 모델로 seen/unseen
주파수대역 이진 대조 합성실험을 설계해 검증.

## 방법상 우리와의 차이
- **통제 축은 주파수 하나뿐** — SNR·꼬리·체제전환·변동성군집 등 다른 메커니즘은 다루지 않음
- 평가 모델 **1개**(MOMENT-small)뿐
- 지표는 MSE/MAE, Accuracy/AUC — **CRPS·불확실성 정량화 개념 자체가 없음**
- **임계점 정량화 없음** — seen/unseen 이진 대조만, dose-response 곡선 없음
- 도메인은 게임(금융은 사전학습 코퍼스 도메인 나열에만 등장, 실험 대상 아님)

## 저자 스스로의 한계 인정 — 인용 가능
Limitations 원문 직접인용: "The synthetic probes also simplify real-world dynamics,
relying on sinusoidal signals that do not fully capture irregular sampling,
burstiness, or **regime shifts**."
→ 체제전환(regime shift)을 다루지 못했음을 저자 스스로 명시. 본 연구가 이 공백을
메운다는 근거로 직접 인용 가능.

## 우리 연구와의 관계
방법론적으로 본 연구와 **가장 가까운** 선행연구(합성 통제 실험으로 TSFM 실패를
진단한다는 발상 자체는 동일). 다만 축이 하나(주파수)뿐이고 도메인이 금융이 아니므로,
"다축(변동성군집·두꺼운꼬리·체제전환 등) × 금융 도메인"으로 명확히 차별화해야 하는
1순위 대조 대상.
