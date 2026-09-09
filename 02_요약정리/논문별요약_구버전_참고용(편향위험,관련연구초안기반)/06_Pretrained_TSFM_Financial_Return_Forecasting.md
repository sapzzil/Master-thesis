# Pretrained Time-Series Foundation Models for Financial Return Forecasting

- **서지**: Miquel Noguer i Alonso, Rodolfo Pereira Franklin (AI Finance Institute),
  arXiv:2606.27100
- **위협도**: 중 (동기 근거 — 모순의 다른 축)
- **원문(한글역, Abstract만 완역 + 나머지 파라프레이즈)**:
  `01_자료원문_ko/06_2606.27100_Pretrained_TSFM_Financial_Return_Forecasting.md`
- **근거 문서**: `03_최종취합/관련연구_초안.md` §5.1

## 한 줄 요약
미국 유동성 주식 5종(AAPL/AMZN/GOOG/JPM/META) 20영업일 예측 과제에서, 사전학습
TSFM(TimeGPT/TimeGPT-LH, TimesFM-2.5, Moirai-2.0, Chronos, Chronos-2)을
train-from-scratch 신경망 베이스라인(NBEATS/NHITS/PatchTST/iTransformer/KAN)과
벤치마크.

## 핵심 결과
- 사전학습 TSFM이 **10개 태스크-레벨 승리 중 8개**를 차지(Moirai-2.0·TimesFM-2.5가
  평균 순위 최상)
- 단, iTransformer 베이스라인이 META 양쪽 태스크에서 승리 — 특정 자산·국면에서는
  지역 지도학습이 범용 사전학습을 능가할 수 있음을 시사
- **더 중요한 지점**: 랜덤워크 벤치마크 대비 이득은 작고 드묾. 단측 Diebold–Mariano
  검정에서 통계적으로 유의한 개선은 10개 중 **2개뿐**(AMZN의 Chronos, GOOG의 Moirai-2.0)
- 결론: TSFM은 저데이터 금융 예측에서 모델개발 비용을 낮추는 유용한 실용적
  prior이지만, 통계적으로 신뢰할 수 있는 알파 생성의 보편적 엔진은 아님

## Re(Visiting)과의 관계 — "문헌 모순"이 아니라 "설계 차이"
언뜻 Re(Visiting)(2511.18578, off-the-shelf TSFM 부진)과 상반돼 보이지만, 4단계
재검증 결과 **정면 모순으로 과장해선 안 됨**:
- 이 논문 §2 관련연구가 Re(Visiting)을 직접 인용하며 스스로 "두 연구는
  **상호보완적(complementary)**"이라고 명시
- Abstract 후반도 "gains over the random-walk benchmark are small and sparse"라며
  결과를 스스로 완화
- 비교 대상이 다름(이 논문은 NBEATS·NHITS 등 신경망과 비교, Re(Visiting)은 CatBoost
  등 트리 앙상블과 비교) + 평가 범위가 다름(미국 5종목 vs 94개국 횡단면)
→ 본 연구는 "정면 모순"이 아니라 **"비교 대상·평가 설계에 따라 TSFM의 금융 성과가
크게 갈리며, 그 갈림의 원인을 설명하는 연구가 없다"**는 신중한 톤으로 서술. 이 갈림을
설명하는 것이 본 연구 기여②(합성 임계점 ↔ 실측 대조)의 핵심 동기.

## 수집 상태 주의 — 재확인 필요
원문은 **부분 수집**(Abstract~Methodology 3.4 도입부까지). Section 4(실험설계)·5(결과
상세)·6(논의)·7(결론)·Appendix는 미확보 — Abstract 요약 수준의 결과만 확정적으로
인용 가능, 세부 수치(Table 등)는 원문 재조회 후 사용.
