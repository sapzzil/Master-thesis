# Pretrained Time-Series Foundation Models for Financial Return Forecasting — 독립 요약

> 이 요약은 수집된 원문 파일(부분 수집본: Abstract 직접인용 + 2차 파라프레이즈, Section 4~7 및 부록 미확보)만을 근거로 독립적으로 작성한 것이다. 다른 프로젝트 문서(관련연구 초안, 기존 요약 등)는 참조하지 않았다.

## 서지정보
- 제목: Pretrained Time-Series Foundation Models for Financial Return Forecasting
- 식별자: arXiv:2606.27100v1 [q-fin.MF]
- 저자: Miquel Noguer i Alonso, Rodolfo Pereira Franklin (Artificial Intelligence Finance Institute)
- 제출일: 2026년 6월 25일
- 원문 URL: https://arxiv.org/abs/2606.27100 (HTML: https://arxiv.org/html/2606.27100)

## 한 줄 요약
5개 미국 주식(AAPL, AMZN, GOOG, JPM, META)의 20영업일 수익률 예측에서 사전학습 시계열 파운데이션 모델(TSFM) 6종을 처음부터 학습하는 신경망 베이스라인 5종과 롤링-오리진 프로토콜로 비교한 결과, TSFM이 순위 경쟁에서는 우세했지만(10개 태스크 중 8승), 랜덤워크 대비 통계적으로 유의미한 개선은 단 2개 태스크(Chronos/AMZN, Moirai-2.0/GOOG)에 그쳐 "순위 우세"와 "경제적으로 의미 있는 예측력"을 분리해서 봐야 한다는 결론(2차 정리 기반 서술 + Abstract 직접인용 결합).

## 문제의식/동기
(2차 정리 기반) 저자들은 실무자 관점의 질문을 던진다: 자산당 단 하나의 수익률 시계열만 있고 20영업일 예측을 원하며 종목별로 무거운 모델 개발을 하고 싶지 않은 상황에서, 즉시 사용 가능한(out-of-the-box) TSFM이 처음부터 학습하는 대안보다 나은가? 금융 수익률 예측은 낮은 신호대잡음비, 구조적 단절, 두꺼운 꼬리(heavy tail), 약한 지속성이라는 특성 때문에 시계열 파운데이션 모델에게 "의도적으로 보수적인(deliberately conservative)" 테스트 환경이라는 문제의식이 Abstract에 원문 그대로 명시되어 있다. 또한 저자들은 "강한 순위"가 곧 "잡음이 많은 시장에서의 경제적으로 의미 있는 예측가능성"을 함의하지 않는다는 점을 이론적으로 짚고자 한다(Abstract 원문).

배경으로는 Yule–Walker 자기회귀 모형(1920~30년대)과 Box-Jenkins ARMA(1970)로 이어지는 시계열 분석 전통을 언급하며, 최근 대규모 시간적 사전학습이 자산별 개별 모델 학습보다 나은 귀납적 편향을 줄 수 있는지에 대한 관심이 재부상했다고 서술한다(2차 정리 기반).

## 방법론 (2차 정리 기반, 세부는 미확보)
- **평가 대상 TSFM (6종)**: TimeGPT / TimeGPT-LH, TimesFM-2.5, Moirai-2.0, Chronos, Chronos-2 (Abstract에는 5개 계열로 언급되나 TimeGPT와 TimeGPT-LH를 별도로 세면 6종)
- **베이스라인 (5종, train-from-scratch)**: NBEATS, NHITS, PatchTST, iTransformer, KAN(콜모고로프-아르놀트 네트워크 기반 시계열 모델)
- **데이터**: 유동성 높은 미국 주식 5종 — AAPL, AMZN, GOOG, JPM, META. 선형 수익률과 로그 수익률 두 가지 표현 모두 사용.
- **프로토콜**: 모든 신경망 모델에 대해 컨텍스트 윈도우 L=512로 동일하게 맞춘 "equalized context budget", 롤링-오리진(rolling-origin) 평가, 예측 구간 h=1,...,H (H=20, 즉 20영업일).
- **평가 지표**: MAE 및 랜덤워크 벤치마크 대비 상대 성능("naive random-walk alternatives" 대비 스킬), 통계검정으로 Diebold–Mariano(DM) 검정(단측) 사용.
- **이론적 프레이밍**: 사전학습을 귀납적 사전(inductive prior)으로 보는 프레임, PAC-Bayes zero-shot 전이 경계, 정보이론적 예측가능성 상한, 어텐션의 연산자이론/스펙트럴 관점, 예측 점수의 분포기하학 등을 결합해 "왜 강한 순위가 경제적으로 유의미한 예측가능성을 함의하지 않는지" 이론적으로 설명하려는 시도(Section 3, 상세 미확보).
- **문제 정식화(3.1, 원문 확인됨)**: 확률공간 (Ω,ℱ,ℙ), 필트레이션 ℱ_t=σ(r_s:s≤t) 상의 수익률 과정 (r_t). 제곱손실 → 베이즈 최적 예측기는 조건부 평균; 절대손실(MAE의 기준) → 베이즈 최적 예측기는 조건부 중앙값. 준마팅게일 분해(Doob decomposition)로 마팅게일-차분 가설(랜덤워크 귀무가설)을 설명하되, 저자들은 이 가설을 유지해야 할 귀무가설이 아니라 "이겨야 할 벤치마크"로 취급한다고 명시. 제로 리턴 랜덤워크(r̂=0)가 (i) 마팅게일 가설 하 제곱손실 최적, (ii) 무조건부 중앙값이 0에 가까울 때 MAE 최적이라는 두 조건이 우연히 일치함을 지적하며, 따라서 랜덤워크를 MAE에서 이기려면 무조건부 중앙값을 넘어서는 "진정한 조건부 정보"가 필요하다고 강조.

## 핵심 결과 (Abstract 원문 인용 기반)
- 10개 태스크-레벨(5종목 × 2가지 수익률 표현) 승리 중 8개를 사전학습 TSFM이 차지. Moirai-2.0과 TimesFM-2.5가 평균 순위 최상.
- 종목별 승자: TimesFM-2.5 → AAPL, JPM. Moirai-2.0 → GOOG(양쪽 태스크) 및 AMZN 중 하나. Chronos → 나머지 AMZN 태스크.
- iTransformer(베이스라인)가 META 양쪽 태스크(선형·로그 수익률)에서 승리 — "국지적 지도학습이 특정 자산·국면에서는 일반 사전학습을 능가할 수 있다"는 근거로 제시됨.
- **랜덤워크 대비 이득은 작고 드묾**: 단측 Diebold–Mariano 검정에서 "동등하거나 열등한 예측정확도" 귀무가설을 기각한 것은 AMZN에서의 Chronos, GOOG에서의 Moirai-2.0, 단 두 사례뿐. 즉 대부분의 순위 우세는 랜덤워크 대비 통계적으로 유의미한 개선으로 이어지지 않음.
- 저자들의 결론(Abstract 원문): 이러한 증거는 TSFM이 저데이터 금융 예측 상황에서 모델 개발 비용을 줄여주는 "유용한 실용적 사전(useful practical priors)"이라는 주장을 뒷받침하지만, "통계적으로 신뢰할 수 있는 알파 생성이나 트레이딩 성과의 보편적 엔진(universal engines)"은 아니라고 결론.
- Section 5(Results 상세), Section 6(Discussion/Limitations), Section 7(Conclusion 본문), Appendix A(전체 벤치마크 표), Appendix B(재현성 체크리스트)는 이번 수집본에 포함되지 않아 구체적 수치 표, 상세 논의는 확인 불가.

## 다른 TSFM 금융 연구(특히 Re(Visiting) 계열)에 대한 언급/포지셔닝
원문(Related Work, 2절)에 다음과 같은 명시적 포지셔닝이 있음(2차 정리 기반, 단 원문에 등장하는 문헌명임):
- 가장 밀접한 동시대 연구로 **Rahimikia et al.(2025)**을 언급. 이 연구는 여러 TSFM 계열에 대해 zero-shot 추론, 미세조정, 처음부터의 사전학습을 "글로벌 초과수익률 패널(broad global excess-return panel)"에서 평가했다고 소개됨. 그 연구의 주요 발견으로 (1) 기성(off-the-shelf) TSFM은 zero-shot·미세조정 환경에서 표준 앙상블/신경망 베이스라인보다 성능이 떨어지지만, (2) 금융 데이터에 특화된 사전학습(finance-native pretraining)이 그 격차의 상당 부분을 좁히고 더 강한 포트폴리오 성과를 낼 수 있다는 점을 인용.
- 본 논문은 이 선행연구와 스코프 차이를 명시적으로 구분: "5개 미국 주식에 대한 단일 자산 20영업일 예측" vs. "글로벌 수준의 익일(next-day) 횡단면 초과수익률 예측". 두 연구를 상호 보완적(complementary)이라고 서술.
- 정성적 결론이 일관된다고 강조: "일반(generic) TSFM의 이득은 자산별 저데이터 환경에서 유용할 수 있지만 제한적이며, 금융 특화적인 경제적 초과성과와 혼동해서는 안 된다."
- **주의**: 이 파일에는 "Re(Visiting)"이라는 명칭을 가진 논문이 직접 언급되어 있지 않다. 만약 사용자가 찾는 "Re(Visiting) TSFM 금융 연구"가 이 Rahimikia et al.(2025) 논문을 가리키는 것이라면 위 내용이 관련 서술이지만, 정확한 논문 제목·저자 전체 명단은 이 수집본만으로는 확인할 수 없다(References 섹션이 "생략(원문 참조)"으로 미수집 상태). 별도로 원문 References를 확인해 Rahimikia et al.(2025)의 정확한 논문 제목이 "Re(Visiting) ..." 형태인지 대조할 필요가 있음.
- Time-LLM, LLM4TS, PromptCast 계열(텍스트 LLM을 리프로그래밍/프롬프팅으로 시계열에 적용하는 갈래)은 "관련은 있으나 본 논문의 실증적 초점은 아님"으로 명확히 선을 그음 — 직접적인 Time-LLM/LLM 리프로그래밍 실험은 수행하지 않았다고 명시.
- 저자들의 이전 연구인 Alonso and Franklin(2025)이 언급되며, Time-LLM 계열 논의의 연장선임을 시사(2차 정리 기반, 상세 불명).

## 수집되지 않은/미확보 부분
- **Section 3.5~3.21**: 목차상 제목만 확인, 본문 상세(수식, 구체적 논증)는 3.4절 문장 중간에서 조회가 끊겨 미확보. 특히 인과 용량/최대 트레이딩 효용(3.5), 어텐션의 연산자이론/스펙트럴 갭(3.6~3.7), 시그니처·패칭 이론(3.8), 정보기하학(3.9~3.10), 각 모델(TimeGPT, TimesFM-2.5, Moirai-2.0, NBEATS, NHITS, PatchTST, Chronos, iTransformer, KAN, Chronos-2)의 상세 아키텍처 설명(3.12~3.21) 전부 미확보.
- **Section 4 (Experimental Design)**: 4.1 데이터/대상/벤치마크 범위, 4.2 평가 모델 목록 상세, 4.3 컨텍스트 윈도우·학습 프로토콜·재현성, 4.4 지표 및 통계검정(스킬 점수, 상대 MAE, Harvey–Leybourne–Newbold 보정, 부호 규약, 다중비교 처리 등) — 전부 본문 미확보, Abstract에 언급된 개요만 파악.
- **Section 5 (Results)**: 5.1~5.4 절 세부(구체적 MAE 수치, DM 검정통계량, 유의수준, 자산별/모델별 표 전체)는 미확보. Abstract 요약 수준의 정보만 확보.
- **Section 6 (Discussion and Limitations)**: 전체 미확보.
- **Section 7 (Conclusion)**: 본문 미확보(Abstract 결론 문장으로만 유추).
- **Appendix A (전체 벤치마크 표), Appendix B (재현성 체크리스트)**: 전체 미확보.
- **References**: 전체 미확보(생략 표시). Rahimikia et al.(2025)을 포함한 인용 문헌의 정확한 서지정보 확인 불가.

## 흥미롭거나 특기할 만한 점 (자유 서술)
- Abstract 자체가 "sensational이 아니라 pragmatic한 결론"이라고 스스로 규정하는 점이 인상적이다 — 저자들은 TSFM이 순위에서 이겼다는 사실과 통계적으로 유의미하게 랜덤워크를 이겼다는 사실을 의도적으로 분리해서 보고하고 있으며, "8/10 태스크 승리"라는 화려한 숫자 바로 뒤에 "그러나 DM 검정 유의는 2건뿐"이라는 절제된 결론을 붙이는 서술 구조 자체가 방법론적 정직성을 강조하려는 의도로 읽힌다.
- 문제 정식화(3.1)에서 "랜덤워크는 지켜야 할 귀무가설이 아니라 이겨야 할 벤치마크"라는 표현이 명시적으로 등장하는데, 이는 많은 금융 시계열 논문이 암묵적으로 랜덤워크=효율적시장가설의 검정 대상으로 다루는 것과 결이 다르다. 즉 이 논문은 EMH 검증이 목적이 아니라 순수하게 예측 성능(forecast accuracy) 벤치마킹이 목적임을 프레이밍 단계에서부터 분명히 하고 있다.
- iTransformer가 유독 META에서만 승리했다는 점은 "특정 자산·국면(regime)에서는 국지적 지도학습이 일반 사전학습을 이길 수 있다"는 논지의 유일한 반례이자 핵심 근거로 쓰이는데, 왜 하필 META인지에 대한 설명(예: META 특유의 변동성 구조, 실적 발표 패턴 등)이 이 수집본에는 없어 궁금증이 남는다 — Section 5.2/6에서 다뤄졌을 가능성이 높다.
- KAN(콜모고로프-아르놀트 네트워크)을 "유일하게 최상위권에 꾸준히 진입하는 train-from-scratch 모델"로 특별히 언급한 부분(Related Work)이 있는데, 정작 Abstract의 승자 목록(TimesFM-2.5, Moirai-2.0, Chronos, iTransformer)에는 KAN이 등장하지 않는다. "최상위권 진입"과 "1위 승리"는 다른 claim이므로 모순은 아니지만, KAN이 구체적으로 어떤 순위를 기록했는지는 미확보 구간(Section 5)에 있어 확인이 필요하다.
- 이론 섹션(3.2~3.10)이 상당히 방대하게 예고되어 있는데(PAC-Bayes, 정보이론적 상한, 연산자이론, 스펙트럴 갭, 시그니처 이론, 정보기하학 등) 실증 섹션(4~5)에 비해 이론이 논문 분량의 큰 비중을 차지하는 구조로 보인다. 이는 실증 결과가 상대적으로 절제된 톤("pragmatic, not sensational")인 것과 대비되어, 저자들이 약한 실증 결과를 이론적 프레이밍으로 보완하려는 전략을 취했을 가능성을 시사한다(다만 이는 목차 구조만으로 추정한 것으로 원문 확인 필요).
