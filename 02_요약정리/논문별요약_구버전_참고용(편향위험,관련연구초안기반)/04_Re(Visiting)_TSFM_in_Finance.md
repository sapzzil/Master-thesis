# Re(Visiting) Time Series Foundation Models in Finance

- **서지**: Rahimikia, Ni, Wang, arXiv:2511.18578, 2025년 11월
- **위협도**: 높음 (동기 근거 — 모순의 한 축)
- **원문(한글역, 부분 수집본)**: `01_자료원문_ko/04_2511.18578_Revisiting_TSFM_in_Finance.md`
- **근거 문서**: `03_최종취합/관련연구_초안.md` §5.1~5.2

## 한 줄 요약
TSFM의 금융시장 최초 포괄적 실증연구. 94개국 34년치 일간 초과수익률(~19.3억 관측치)
패널로 zero-shot / fine-tuning / pretrain-from-scratch 3체제를 CatBoost 등 강력한
트리 앙상블·선형·신경망 베이스라인과 비교.

## 핵심 결과
- 기성(off-the-shelf) TSFM zero-shot 추론은 **부진**: TimesFM(500M) R²=-2.80%,
  Chronos(large) R²=-1.37% — 둘 다 CatBoost(-0.10%)보다 열등
- 금융데이터로 파인튜닝하거나 처음부터 사전학습하면 상당히 개선(단, 파인튜닝은
  Chronos(large) 제외 대부분 오히려 성능 하락)
- 방향정확도는 4개 윈도우 전부 51% 근처, CatBoost 최고 Sharpe 6.79(윈도우 252)

## 방법론적 한계 — 본 연구가 메우는 공백
**CRPS·pinball·coverage·PIT를 전혀 쓰지 않는다.** Chronos가 확률모델임에도 몬테카를로
평균으로 조건부 평균만 추출해 점예측처럼 다룸. → 확률예측 캘리브레이션 축이 완전히
비어있음(본 연구 기여①과 직결).

## 한국 시장 관련 — 중요 정정
원문(§1): "testing across major markets, including...South Korea..." — 한국은 이미
평가 대상에 포함되어 있고, **대만과 함께 "가장 어려운 환경"으로 명시적으로 지목됨**
(앙상블 평균 Sharpe≈0.20, 데이터 증강 후에도 개선 미미).
→ **"TSFM×한국 시장 최초 적용"은 본 연구의 단독 novelty로 사용 불가.** 대신 "한국
시장이 TSFM에 특히 취약하다고 이미 보고됨"이라는 근거로 인용하고, 한국은 본 연구
기여③(실측 대조)의 보조 검증사례로만 배치(스코프 단순화표와 일치).

## 수집 상태 주의 — 재확인 필요
원문 자체가 **부분 수집**(Abstract~§4.1 "Data Source" 중반까지만, 이후 §4.2~Conclusion,
Appendix, References 미확보). §6 결론부의 "TSFM이 본질적으로 전체 예측분포를 생성할
수 있다" 류 인용은 **미확인 상태로 격하**됨 — 6단계 집필 전 원문(특히 §6) 재수집 필수.

## 우리 연구와의 관계
2606.27100(Pretrained TSFM Financial Return Forecasting)과 상반된 결과를 보고하는
것처럼 보이나, 4단계 재검증 결과 "정면 모순"이 아니라 비교 대상·평가 범위가 다른 데서
오는 차이로 신중하게 재프레이밍됨(05번 문서 참조). 이 갈림 자체를 설명하는 것이 본
연구 기여②의 동기.
