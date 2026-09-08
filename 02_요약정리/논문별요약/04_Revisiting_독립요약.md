# Re(Visiting) Time Series Foundation Models in Finance — 독립 정독 요약

## 서지정보
- 제목: Re(Visiting) Time Series Foundation Models in Finance
- arXiv ID: 2511.18578 (2025년 11월)
- 저자: Eghbal Rahimikia (Alliance Manchester Business School, University of Manchester), Hao Ni (Dept. of Mathematics, UCL), Weiguan Wang (School of Economics, Shanghai University)
- 모델·데이터 공개: FinText.ai 포털, Hugging Face(https://huggingface.co/FinText)
- 주: 이 파일은 arXiv HTML의 Abstract부터 Section 4.1 "Data Source" 중반(Table 2 설명 및 "Model estimation follows an expanding-window approach..." 문장)까지만 수집된 부분본이다. 그 이후(4.2~4.4, Section 5 전체 결과표, Section 6, Appendix, References)는 원문에서 직접 읽지 못했으므로 아래 요약도 그 범위로 한정한다.

## 한 줄 요약
전 세계 94개국·34년치(1990~2023) 일별 초과수익률 약 20억 건을 이용해 시계열 파운데이션 모델(TSFM, 대표적으로 Chronos·TimesFM)을 제로샷/파인튜닝/처음부터 사전학습 세 체제로 최초로 종합 평가한 결과, 기성 사전학습 TSFM은 CatBoost 등 강력한 트리 앙상블 벤치마크에 성능이 크게 못 미치지만, 금융 데이터로 처음부터 사전학습시키고 데이터 규모·합성 데이터 증강·하이퍼파라미터 튜닝을 결합하면 벤치마크를 능가할 수 있다는 것을 보인 논문.

## 문제의식/동기
- 금융 시계열 예측은 트레이딩·포트폴리오 최적화·리스크 관리에 핵심적이지만, 데이터가 잡음이 많고(low signal-to-noise), 비정상적(non-stationary)이며, 자산·구간별로 이질적이라 일반화가 어렵다.
- LLM의 사전학습-파인튜닝 패러다임에 영감을 받아 등장한 TSFM(예: Chronos, TimesFM)이 범용 시계열 표현을 학습해 제로샷/소량샷으로 새로운 데이터셋에도 통할 것이라 기대되지만, 실제 금융 도메인에서 그 성능이 검증된 바가 거의 없다는 공백을 지적.
- 기존 TSFM 문헌은 금융 데이터의 고유 특성을 반영하지 않는 범용 데이터셋으로 벤치마킹하는 경우가 많다는 점도 문제로 짚음. 이 논문은 이를 보완해 "제대로 된 벤치마크(강력한 트리 앙상블 등)"부터 다시 세우고 TSFM을 처음부터 재검토(Re-visiting)한다.

## 방법론
### 데이터 규모
- 1990~2023년, 94개국의 기업 단위 일별 초과수익률(excess return) 패널. 미국은 CRSP, 미국 외는 Compustat 글로벌 일별 증권 파일 사용(둘 다 있으면 CRSP 우선).
- 상장폐지 수익�  반영(정보 없으면 관행에 따라 -30% 부여), 국가·일자별 시총 하위 5% 제외, 수익� 1000% 밖은 오류로 처리, Compustat 수익률은 같은 날 CRSP 분포의 0.1~99.9백분위로 윈저라이즈.
- 2022년 기준 학습 데이터가 최대: 미국 1억 7,696만 건66,250개 종목, 전 세계(All Markets) 4억 9,689만 건204,090개 종목(누적 관측치).
- 추가로 Jensen et al. (2023)의 JKP 팩터(13개 개념 클러스터, 153개 월보 팩터: Investment, Value, Low risk, Quality, Momentum �1)뭼 결합.）JKP 포함 시 2022년 기준 뿸국 4억 5,662븜 건33,180개 종목, 전 세계 14억 3,405만 건102,820개 종목. 초과수익�+JKP 전체 합산 시 2022년 최대 19개 3,095기 관(관측치), 135,990개 종목(수치덼 되문치).
- 모델 학습용퍰이터 그룹 3갅: (1) U.S.(미국 초과수익률벬), (2) global(미국+글로벌 초과수익률), (3) JKP-augmented(글로뫌+JKP 팩터).
- 모델 춴정은 확장 대욲(expanding-window) 방식: 2000년 모델은 1990년부터의 데이터로 학습, 이후 2022년까지 매년 모델을 춐가로 재추정.

### 평가 체제 3가지 (TSFM 적용방식강)
1. 사전학습 모델蝘 제로샷 추론(Pre-Trained/Zero-Shot Inference): 기성 사전학습 가중치를 파라미터 업데이트 없이 그대로 금융 데이터에 적용.
2. 파인튜닝(Fine-Tuned Model): 사전학습 초기값에서 시작해 금융 데이터(D_fin)로 전체 파라미터를 재학습.
3. 처음부터 사전학습(Pre-Trained from Scratch): 파라미터를 무작위 초기화한 뒤 오직 금융 데이터만으로 매년 새로 학습(미래 정보 유출 방지를 위해 해당 연도까지의 데이터만 사용).

### 비교 대상(벤치마크)
- 선형 모델: OLS, Lasso, Ridge, Elastic Net, PCR(주성분회귀)
- 트리 기반 앙상블: CatBoost, XGBoost, LightGBM
- 신경망(NN)
- TSFM: 핵심 비교는 Chronos(Ansari et al., 2024, Amazon)와 TimesFM(Das et al., 2024, Google) 두 모델군. 추가로 12개의 다른 TSFM 아키텍처(부록 D에 설명, 이번 수집본에는 미포함)로 확장 검증.
- 평가 척도: (i) 예측 성능 — 표본외 결정계수 R²_OOS(Gu et al. 2020 방식, 예측=0을 기준으로 벤치마크), 방향 정확도(accuracy), 매크로 평균 F1, 상승/하락별 정확도. (ii) 포트폴리오 성과 — 예측 초과수익률로 10분위 정렬해 상위/하위 분위를 매일 리밸런싱하는 롱숏(zero-cost, equal-weighted) 포트폴리오의 연환산 수익률, 표준편차, 샤프비율, 일평균 수익률(bps), 최대낙폭(Max DD), 1일 최대손실, 왜도, 첨도.
- 실험 창(윈도우) 크기: 과거 5, 21, 252, 512거래일. 평가 기간은 2001~2023년(초록에는 2001-2023, 본문 서술은 2001~2023년 언급, 이 부분 수치는 원문 인용대로 옮김).

## 확보된 범위 내 핵심 결과 (구체적 수치, 모두 Introduction 요약 서술에서 발췌 — Section 5 표는 미수집)
- 벤치마크(윈도우 평균, 미국 전체 주식): 선형회귀 R²_OOS = -0.47%, CatBoost R²_OOS = -0.10%. 방향 정확도는 4개 윈도우 모두 51% 살짝 상회. 소형주가 대형주보다 예측 가능성이 더 큼.
- 최고 성과 CatBoost(윈도우 252, 샤프비율 기준 최적): 연환산수익률 46.50%, 샤프비율 6.79(거래비용 미반영, 매일 리밸런싱 롱숏 포트폴리오).
- 제로샷: Chronos(large), 과거 512개 사용 시 R²_OOS = -1.37%, 방향정확도 51% 살짝 상회. TimesFM(500M) R²_OOS = -2.80%, 방향정확도 50% 살짝 밑돎. 두 모델 모두 윈도우 512에서 연환산수익률 각각 20.17%, -1.47%(CatBoost 대비 크게 열위). 12개 추가 TSFM 아키텍처로 확장해도 결과는 대체로 유사, 다만 대규모 데이터셋으로 사전학습된 TSFM일수록 일부 일반화 징후 존재.
- 파인튜닝: 대부분의 TSFM 성능이 파인튜닝 후 오히려 악화, Chronos(large)만 예외적으로 개선. 그러나 이 개선이 경제적 이득(포트폴리오 성과)으로 이어지지는 않음. 적합도(goodness-of-fit) 측면에서도 벤치마크와의 격차를 완전히 못 좁힘.
- 처음부터 사전학습: 큰 개선. Chronos(small) R²_OOS가 윈도우 5에서 -77.07% → -3.18%로, 윈도우 512에서 -1.27% → -0.59%로 대폭 개선(제로샷 대비). 다만 벤치마크 모델보다는 여전히 적합도가 낮음.
  - 포트폴리오 성과: Chronos(small)이 윈도우 512에서 연환산수익률 36.84%, 샤프비율 5.42. TimesFM(20M)은 같은 조건에서 30.36%, 3.66.
  - 윈도우 크기 효과: TSFM은 윈도우가 길수록(예: TimesFM(20M) 5일 -18.22% → 512일 30.36%) 성과가 좋아지는 반면, 벤치마크 모델은 오히려 짧은 윈도우에서 상대적으로 더 나은 경향(비대칭적 패턴).
  - 전 모델군(벤치마크/제로샷/파인튜닝/사전학습 TSFM)에서 롱숏 포트폴리오의 롱(매수) 다리가 숏(매도) 다리보다 일관되게 우수.
- 데이터 확장(미국→글로벌): 벤치마크 결과 혼재. 선형모델은 R²_OOS가 +0.43~0.60%p 개선되어 전부 양(+)으로 전환. Lasso, Ridge, NN도 상당히 개선. 반면 앙상블(CatBoost, XGBoost, LightGBM)은 소폭 악화. 그러나 대부분 모델에서 방향정확도와 포트폴리오 성과는 약화.
- JKP 팩터+합성 데이터 증강 결합 시 TSFM은 통계·경제적 성과 모두 일관되게 개선. Chronos(small)의 방향정확도 51.74% (윈도우 512) vs CatBoost 51.16%로 TSFM이 더 높음. 연환산수익률/샤프비율: Chronos(small) 41.89%/6.78 vs CatBoost 47.25%/6.46(같은 윈도우 512 조건, 수익률은 CatBoost가 더 높지만 샤프비율은 Chronos가 근소 우위).
- 하이퍼파라미터 튜닝만으로도(데이터 스케일링 없이) TSFM이 벤치마크를 능가할 수 있음을 확인.
- 시간에 따른 성과 저하: TSFM과 벤치마크 모두 포트폴리오 성과가 점진적으로 저하(시장 효율성 증가 반영)되나, TSFM의 저하 속도가 더 느리고 완만함.
- 미국 외 7개 주요국 시장으로 확장 테스트해도 미국에서 얻은 결과와 대체로 일관된 결과.

## 한국 시장이 원문에서 어떻게 언급되는지
수집된 범위에서 "South Korea"(또는 "Korea")가 명시적으로 등장하는 곳은 Introduction 단 한 군데다. 원문 인용:

> "This extensive coverage supports a rigorous evaluation of TSFMs and benchmark models, examining their robustness and generalizability across diverse market structures and institutional environments... testing across major markets, including the United States, Hong Kong, Taiwan, South Korea, Germany, the United Kingdom, India, and Australia."

즉 한국은 테스트(국제 검증) 대상 주요 시장 8개국 목록에 이름만 등장하며, 뒤이어 나오는 "미국 외 7개 주요 비미국 시장으로 확장 테스트"(Section 5.3, "we also extend the main empirical tests to seven major non-U.S. markets")가 바로 이 8개국 중 미국을 제외한 7개국(홍콩, 대만, 한국, 독일, 영국, 인도, 호주)을 가리키는 것으로 보인다. 다만 이 부분(5.3 International Results)의 실제 수치 결과표는 이번 수집 범위(Section 4.1 중반까지)에 포함되어 있지 않아, 한국 시장에 대한 구체적 성과 수치나 별도 서술은 확인할 수 없었다. Section 4.1의 Table 1/2, 국가 코드 목록(Table A.1, 각주 [7])에도 94개국이 포함된다는 언급만 있을 뿐, 한국 관련 개별 수치는 수집 범위 내 텍스트에 나타나지 않는다.

## 원문에서 확인되지 않은/수집 안 된 부분
- Section 4.1의 나머지 부분("Consequently, for each test conducted..." 이후)
- Section 4.2 Data Cleaning and Preprocessing
- Section 4.3 Sample and Model Sizes
- Section 4.4 Computational Resources
- Section 5 Numerical Results 전체 — 5.1(미국 데이터: 벤치마크/제로샷/파인튜닝/사전학습/학습시간 비교의 실제 표), 5.2(스케일 데이터: 스케일 벤치마크·TSFM 결과, 시간에 따른 포트폴리오 성과 추적, 거래비용, 하이퍼파라미터 영향), 5.3(국제 결과: 벤치마크·TSFM, 한국 포함 7개국 실제 수치)
- Section 6 Conclusion
- Appendix A(Data Overview), B(Extended Results), C(Benchmark Models 상세), D(TSFM 12개 모델 요약)
- References
→ 위 항목은 목차 제목만 확인되었을 뿐 본문 내용은 전혀 읽지 못했으므로, 이 요약에 등장하는 모든 구체적 수치는 오직 Abstract·Introduction(요약 서술)과 Section 4.1 앞부분(데이터 설명)에서 직접 인용한 것이다. Section 5 원표의 세부 수치(예: 방향정확도 소수점, 개별 윈도우별 완전한 표)는 "본문 서술 문장에서 인용된 값"만 확보되었고 표 자체는 확보되지 않았다는 점에 유의.

## 흥미롭거나 특기할 만한 점
- 저자들이 "TSFM"이라는 약어 사용에 대해 각주에서 직접 논쟁적 코멘트를 남긴다: Das et al.(2024)은 TimesFM 자체를 "time series foundation model"의 약칭으로 썼지만, 이 논문은 최근 문헌 관행을 따라 TSFM을 일반 용어로, TimesFM은 특정 모델명으로 구분해서 쓴다고 명시 — 다소 사소하지만 문헌 관햿까지건륨 이담 보여줌.
- Gu et al.(2020)의 R²_OOS 정의(과거 평균이 아니라 "0"을 기준으로 벤치마킹)를 그대로 채택한 이유를 각주에서 설명 — 개별 주식 수익률의 과거 평균이 매우 노이즈가 많아 약한 모델도 좋아 보이게 만들 수 있기 때문. 이는 이 논문의 R² 수치들(전부 음수인 경우가 많음)이 통상적인 R² 직관과 다르게 해석되어야 함을 시사.
- "제로샷 TSFM은 참담하지만, 처음부터 사전학습하면 크게 개선되고, 파인튜닝은 오히려 애매하거나 악화"라는 3단 구도가 명확한 서사를 이루며, "일반 시계열 사전학습이 금융 도메인으로 그대로 전이되지 않는다(generic time series pre-training does not directly transfer to financial domains)"는 결론 문장이 초록·서론 모두에서 강하게 반복됨 — 이는 파운데이션 모델의 "범용성" 주장에 대한 실증적 반박 사례로 읽힌다.
- Kelly et al.(2024)의 "복잡성의 미덕(virtue of complexity)" 이론에 대한 각주 3의 학술 논쟁 요약(Berk 2023, Buncic 2025, Nagel 2025, Cartea et al. 2025, Kelly and Malamud 2025의 응수)이 상당히 상세하게 소개되어 있어, 이 논문이 단순 응용 보고서가 아니라 최근 자산가격결정-복잡성 논쟁의 맥락 속에 스스로를 위치시키려는 의도가 엿보인다.
- 금융 데이터의 특수성(각주 6): 대부분의 자산가격결정 연구는 월별 데이터+다변량 팩터를 쓰는데, 이 논문은 일별 데이터를 택함으로써 사실상 단변량(univariate) 세팅에 국한된다고 스스로 명시 — TSFM 사전학습에 필요한 표본 크기 확보를 위한 트레이드오프임을 솔직하게 밝힘. 논문 제목의 "Re(Visiting)"이라는 언어유희(괄호로 "Visiting"을 강조)도 "TSFM을 처음 보러 간다/재검토한다"는 이중적 의미를 담은 것으로 보인다.
