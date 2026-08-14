# 검증로그 — 하위갈래 D (TSFM 한계·실패 분석)

> 작성일: 2026-08-15
> 작성자: 독립 검증 에이전트 (요약 작성 에이전트와 별개)
> 대상: `02_요약정리/하위갈래D_TSFM한계_실패분석.md`
> 원칙: 확인 못 한 것은 "확인 불가"로 명시. 원 요약 파일은 **수정하지 않음**(제안만 기재).

---

## 작업 1 — 이월 지시 마무리: 핵심 3편의 References 교차 대조

### 1.0 확보 경로 (재현 가능하도록 기록)

| 논문 | 로컬 사본의 References 유무 | 이번에 쓴 확보 방법 | 최종 상태 |
|---|---|---|---|
| Frequency Matters (2511.05619) | **없음** — 로컬 .md(225행)는 Appendix F에서 끝나고 References 섹션이 누락됨. `## Appendix A Related Work`는 있으나 서지목록은 아님 | Chrome `javascript_tool`로 `https://arxiv.org/html/2511.05619v1`의 `.ltx_bibitem` 노드 전량 추출 | **확보 완료 (17건 전부)** |
| Re(Visiting) (2511.18578) | **없음** — 로컬 .md(240행)는 Section 4.1 중간에서 "[수집 중단 지점]" 주석과 함께 절단됨 | 동일 방법. `document.getElementById('bib')` (14,603자) → `.ltx_bibitem` 66개 노드에서 제목만 추출 | **확보 완료 (66건 전부)** |
| Internal Semantics (2511.15324) | **있음** — 로컬 .md 74~102행 | Read로 직접 확인 | **확보 완료 (15건 전부)** |

보조 시도 기록: `mcp__workspace__bash`의 curl은 워크스페이스에 외부 네트워크가 없어 실패(exit 56). `web_fetch`로 Semantic Scholar Graph API(`/paper/arXiv:2511.18578/references`)를 호출했으나 **빈 응답** — 사용 불가. 결국 Chrome javascript_tool 경로가 유일하게 성공했다.

---

### 1.1 Frequency Matters (2511.05619) — References 17건 전수 확인

전체 목록(제목만): Chronos / TabNet / XGBoost / TimesFM(decoder-only) / The UCR time series archive / Joint embedding go temporal / Masked autoencoders are scalable vision learners / Time-LLM / Condition monitoring of bearing damage(FaultDetection 벤치마크 데이터셋) / Classification of household devices by electricity usage profiles(ElectricDevices) / PatchTST(A time series is worth 64 words) / Lag-Llama / Moirai(Unified training…) / MOMENT / Zerveas et al. transformer framework / Survey on masked autoencoder / GPT4TS(One fits all).

**판정: negative transfer·도메인 적응 실패·사전학습 코퍼스 편향 관련 신규 문헌 — 확인 결과 추가 문헌 없음.**
17건은 전부 (a) TSFM/딥러닝 아키텍처 원논문, (b) SSL 방법론, (c) 실험에 쓴 UCR 계열 데이터셋 출처다. 실패 분석 계열 선행연구를 인용하지 않는다. 이 논문의 "TSFM이 왜 무너지는가"라는 문제제기는 **선행 실패연구를 딛고 선 것이 아니라 자기 산업 사례에서 독립적으로 출발**한 것으로 보인다 — 이는 오히려 해당 문제의식의 선행연구 공백을 방증하는 근거로 쓸 수 있다.

---

### 1.2 Re(Visiting) (2511.18578) — References 66건 전수 확인

66건의 구성을 분류하면:
- **실증자산가격·모멘텀 문헌(약 25건)**: Jegadeesh & Titman(1993), Jegadeesh(1990), Brock et al.(1992), Moskowitz et al.(2012), Asness et al.(2013), Barroso & Santa-Clara(2015), Menkhoff et al.(2012), Gupta & Kelly(2018), Ehsani & Linnainmaa(2022), Liu & Tsyvinski, Gu/Kelly/Xiu(2020), Leippold et al.(2022), Chen et al.(2024), Bali et al.(2016), Frazzini et al.(2012), Martin & Nagel(2022) 등
- **"복잡성의 미덕" 논쟁(6건)**: Kelly et al.(2024), Berk(2023), Buncic(2025), Nagel(2025) "Seemingly Virtuous Complexity", Cartea et al.(2025) "The Limited Virtue of Complexity in a Noisy World", Kelly & Malamud(2025)
- **TSFM/LLM 모델 원논문(약 15건)**: Chronos, TimesFM, MOMENT, Moirai, Lag-Llama, TTM, Toto, Sundial, TiRex, Kairos, FlowState, xLSTM 7B, T5, Transformer, LLaMA, DeepSeek-V3, InstructGPT
- **생성모형(4건)**: Quant GAN, Fin-GAN, Sig-Wasserstein GAN, FTS-Diffusion
- **ML 기법·기초통계(약 12건)**: XGBoost, LightGBM, CatBoost, Ridge, Lasso, Elastic Net, PCR, Adam, SentencePiece/BPE, Huber, Isambard-AI 등

**판정: "negative transfer"를 정면으로 다룬 문헌은 References 66건 중 0건. 도메인 적응 실패·코퍼스 편향을 표제로 하는 문헌도 0건.**

다만 **인접 주제로 신규 검토 가치가 있는 항목 5건**을 아래에 남긴다(모두 이번 조사에서 **제목·서지정보만 확인**했고 **원문 미확인**이므로, 인용하려면 별도 확보 필요):

| # | 저자·연도 | 제목 | ID | 왜 관련있는가 | 기존 요약과의 중복 |
|---|---|---|---|---|---|
| N1 | Yu, Maddix, Han, Zhang, Ansari, Shchur, Faloutsos, Wilson, Mahoney, Wang (2025) | Understanding Transformers for Time Series: Rank Structure, Flow-of-ranks, and Compressibility | arXiv **2510.03358** | Re(Visiting)이 §2.1.2(Transformer 구조 설명)에서 인용. TSFM 내부 표현의 rank 구조/압축성을 분석 — Internal Semantics(2511.15324)와 같은 "내부 메커니즘" 계열이며, "TSFM이 금융 저SNR 데이터에서 무엇을 표현하지 못하는가"를 표현론적으로 뒷받침할 가능성 | **신규** (요약·01_자료원문 모두 없음) |
| N2 | He, Lv, Manela, Wu (2025) | Chronologically Consistent Large Language Models | arXiv **2502.21206** | 사전학습 코퍼스에 미래 정보가 섞이는 **look-ahead bias = 코퍼스 오염**을 정면으로 다룸. Re(Visiting)이 §5.1.4(from-scratch 사전학습으로 look-ahead bias 회피)의 근거로 인용 | **신규**. 단, 이미 확보한 `2510.07920_Profit_Mirage`(정보누출)·`2601.13770_Look_Ahead_Bench`와 주제 중복 가능 — 확인 필요 |
| N3 | Rahimikia & Drinkall (2024) | Re(Visiting) Large Language Models in Finance | SSRN (arXiv ID 없음) | 본 논문의 직계 선행작. "범용 대형모델보다 소규모 도메인 특화 사전학습이 낫다"는 주장 — 코퍼스 도메인 정합성 논거의 원류 | **신규** |
| N4 | Liang, Wen, Nie, Jiang, Jin, Song, Pan, Wen (2024) | Foundation Models for Time Series Analysis: A Tutorial and Survey | KDD 2024, pp.6555–6565 | TSFM 분야의 표준 서베이. 서론의 개념 정의·분류체계 인용용. **negative transfer 자체를 다루는지는 원문 미확인** | **신규** |
| N5 | Cartea, Duran-Martin, Sánchez-Betancourt 계열 (2025) | The Limited Virtue of Complexity in a Noisy World | (서지 미확인) | "특징이 노이즈로 측정될 때 모델 복잡도를 키우면 out-of-sample R²와 Sharpe가 **악화**된다"는 주장. 금융의 저SNR이라는 데이터 성질이 대형모델을 무너뜨린다는 **경제학 쪽 이론적 대응물** — 우리 연구질문("금융 데이터의 어떤 성질에서 붕괴하는가")과 개념적으로 가장 가까운 금융계량 문헌 | **신규**. 다만 TSFM이 아닌 선형 RFF 모델 대상이라 직접 근거로는 쓸 수 없음 |

이미 `01_자료원문/`에 사본이 있어 **중복으로 확인된 것**: Chronos(2403.07815), TimesFM(2310.10688), Lag-Llama(2310.08278), Moirai(2402.02592), TTM(2401.03955), Toto(2407.07874), Sundial(2502.00816).
Re(Visiting)이 인용했으나 사본이 없는 TSFM 원논문: MOMENT(2402.03885), TiRex(2505.23719), Kairos(2509.25826), FlowState(2508.05287), xLSTM 7B — 다만 이들은 **모델 원논문**이지 실패분석 문헌이 아니므로 하위갈래 D의 대상은 아니다(하위갈래 A 소관).

---

### 1.3 Internal Semantics (2511.15324) — References 15건 전수 확인

전체 목록: Alain & Bengio(linear probes, 1610.01644) / Ansari et al.(Chronos) / Das et al.(TimesFM) / Garza et al.(TimeGPT, 2310.03589) / Goswami et al.(MOMENT) / Grabocka et al.(shapelets) / Hewitt & Manning(structural probe) / Ismail et al.(interpretability benchmarking) / Jolliffe(PCA) / Kornblith et al.(CKA) / McInnes et al.(UMAP) / van der Maaten & Hinton(t-SNE) / Wiliński et al.(2409.12915) / Woo et al.(Moirai).

**판정: negative transfer·도메인 적응 실패·코퍼스 편향 관련 문헌 — 확인 결과 추가 문헌 없음.** 15건 전부 TSFM 원논문 아니면 해석가능성/차원축소 방법론이다.

인접 신규 후보 1건:

| # | 저자·연도 | 제목 | ID | 왜 관련있는가 | 중복 |
|---|---|---|---|---|---|
| N6 | Wiliński, Goswami, Żukowska, Potosnak, Dubrawski (2024) | Exploring Representations and Interventions in Time Series Foundation Models | arXiv **2409.12915** | Internal Semantics가 "가장 가까운 선행연구"로 명시한 논문. TSFM 내부 중복성·개념 조향(concept steering) 분석. 코퍼스 편향은 다루지 않으나, **TSFM 내부 표현이 사전학습 분포에 어떻게 묶여 있는지**를 개입 실험으로 보인 문헌이라 붕괴 메커니즘 설명에 쓸 여지 있음 | **신규**. 원문 미확인 |

---

### 1.4 작업 1 종합 판정

> **세 논문의 References 총 98건(17+66+15)을 전수 확인한 결과, negative transfer·도메인 적응 실패·사전학습 코퍼스 편향을 표제·주제로 다루는 문헌은 단 한 건도 인용되지 않았다.**

이는 기존 요약이 "독립 키워드 검색으로 대체"한 선택이 결과적으로 **손실이 없었음**을 뜻한다. 동시에 더 중요한 발견은 다음이다:

**세 편 모두 "TSFM이 자기 도메인에서 실패한다"는 결론에 도달하면서도, 서로를 인용하지 않고 선행 실패연구도 인용하지 않는다.** 즉 TSFM 실패 분석은 아직 **누적적 문헌군(cumulative literature)을 형성하지 못한 파편화 상태**다. 이 사실 자체가 우리 논문 서론에서 연구공백을 주장하는 1차 근거로 쓸 수 있다(예: "세 편의 독립적 실패 보고가 서로 참조 없이 동시에 나타났다"). 다만 이 주장을 쓸 때는 세 편이 모두 2025년 11월에 arXiv에 올라온 **동시기 논문**이라 상호인용이 물리적으로 어려웠다는 점을 함께 밝혀야 공정하다.

---

## 작업 2 — 기존 요약 자체 검증

### 2.1 인용 문헌의 로컬 원문 사본 존재 여부

| 요약의 표에 등장 | 로컬 사본 | 파일명 |
|---|---|---|
| Mix, Don't Pick (2606.09912) | **있음** | `2606.09912_synthetic-corpus-composition-tsfm.md` |
| Adversarial Robustness (2505.19397) | **있음** | `2505.19397_Adversarial_Robustness_of_TSFMs.md` |
| OOD Generalization Survey (2503.13868) | **있음** | `2503.13868_OOD_Generalization_in_Time_Series_Survey.md` |
| Data Similarity & Diversity (2404.06198) | **있음** | `2404.06198_Data_Similarity_Diversity_Transfer_Learning_TSF.md` |
| TimeTic (2509.23695) | **있음** | `2509.23695_TimeTic_Transferability_Estimation_via_In_Context_Learning.md` |
| Dual Adaptation (ICML 2025) | **없음** | — (요약이 이미 "원문 접근 실패"로 정직하게 표시) |
| Chronos 질소예측 (ScienceDirect) | **없음** | — (요약이 이미 취소선 처리) |
| ACM Pretraining Corpora in Finance | **없음** | — (요약이 이미 취소선 처리) |

인용 8건 중 사본이 있어야 할 5건 전부 존재. **누락 없음.**

### 2.2 항목별 원문 대조 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| **Mix, Don't Pick — Abstract 인용문** ("up to a 2× gap…", "generator rankings differ substantially between Chronos-T5-Mini and Moirai-Small") | **정확 (1건 부분 부정확)** | 첫 번째 인용구는 로컬 원문 Abstract와 **글자 단위로 일치**. 두 번째는 원문이 `"generator rankings are not stable across architectures: across 11 generator families evaluated on Chronos-T5-Mini and Moirai-Small…"`이며, 요약이 큰따옴표 안에 쓴 `"generator rankings differ substantially between Chronos-T5-Mini and Moirai-Small"`은 **원문에 존재하지 않는 문장**이다. 의미는 보존되었으나 **직접인용 표기가 부적절** |
| **Mix, Don't Pick — Conclusion 인용문** ("synthetic data should not be treated as a monolithic category…") | **부정확(형식)** | 로컬 사본의 Conclusion 절(133행)은 **한국어 번역문만** 담고 있다("합성 데이터는 단일한(monolithic) 범주로 취급되어서는 안 된다…"). 요약이 제시한 영문 문장은 이 한국어를 되돌린 **역번역으로 보이며 원문 대조 불가**. 의미는 정확하나 인용부호를 붙일 근거 없음 |
| **Mix, Don't Pick — 원문 확인 수준 "전문 확인(Abstract~Conclusion)"** | **과장** | 로컬 사본 헤더는 `수집 상태: 부분`이며 Appendix B~I(하이퍼파라미터, 코퍼스 구성, 부트스트랩 CI 전체표, 도메인별 확장결과, PCA)는 **미확보**로 명시되어 있다. Table 1~4 수치와 Conclusion/Impact Statement는 확보됨 |
| **Mix, Don't Pick — "Impact Statement에서 finance를 명시적으로 언급"** | **정확** | Impact Statement에 "헬스케어, 에너지, **금융**, 인프라와 같은 중요한 영역"과 "코퍼스 구성 선택은 다운스트림 신뢰성에 영향을 미칠 수 있다"가 실재 |
| **Adversarial Robustness — Abstract 인용문 2건** | **정확** | `"even minimal perturbations can induce significant and controllable changes in forecast behaviors—including trend reversal, temporal drift, and amplitude shift"`, `"we identify potential architectural designs, such as structural sparsity and multi-task pretraining, that may improve robustness"` 모두 원문 Abstract와 일치 |
| **Adversarial Robustness — 6개 모델·6개 도메인 목록** | **정확** | TimesFM/UniTS/Moirai/TabPFN-TS/Chronos/TimeMoE, energy/weather/transportation/web/healthcare/sales — Figure 1 캡션과 일치 |
| **Adversarial Robustness — 원문 확인 수준 "Abstract + Introduction"** | **신규확인(과소평가)** | 로컬 사본 헤더는 `수집 상태: 완전 (Abstract부터 Discussion/Broader Impacts까지 본문 전체)`. 요약이 실제 확보 수준보다 **낮게** 적어 놓았다 |
| **Adversarial Robustness — "금융(financial manipulation)을 고위험 시나리오로 명시"** | **정확** | Introduction에 `"financial manipulation, infrastructure misallocation, or public service disruption"` 실재 |
| **OOD Survey — Abstract 인용문** | **정확** | 원문 Abstract와 일치. 요약이 "Abstract만 확인"이라 표시한 것도 로컬 사본 상태(`수집 상태: 부분` — Abstract+목차만)와 **정확히 일치** |
| **Data Similarity & Diversity — Abstract 인용문** | **정확** | `"source-target similarity reduces forecasting bias, while source diversity improves forecasting accuracy and uncertainty estimation, but increases the bias"` 원문과 일치. "5개 공개 소스 → 5개 타겟(real-world wholesales 포함)", "zero-shot·fine-tuned", "accuracy/bias/uncertainty estimation" 모두 정확 |
| **Data Similarity & Diversity — "TSFM이 아니라 사전학습 신경망 일반"이라는 단서** | **정확** | 원문이 `"pre-trained neural networks"`라 표기. 키워드에 "Foundation models"가 있으나 실험 대상은 신경망 전이학습. 요약의 단서 표기가 옳음 |
| **Data Similarity & Diversity — 원문 확인 수준 "Abstract 확인"** | **신규확인(과소평가)** | 로컬 사본은 Introduction부터 6장 도입부까지 확보(6장 중간 절단, References 미확보). Abstract보다 넓게 확인 가능 |
| **TimeTic — Abstract 인용문** | **정확** | 원문 Abstract와 일치. "10개 데이터셋·10개 TSFM·3개 예측과제 벤치마크"도 정확 |
| **TimeTic — "금융 도메인 특정 언급은 Abstract에서 확인 안 됨"** | **신규확인(수정 필요)** | Abstract에는 없는 것이 맞으나, **Introduction 첫 문단에 금융이 명시**됨: `"…particularly in domains with limited public data, such as healthcare (Gupta et al., 2024) and finance (Fu et al., 2024)"`. 로컬 사본은 `수집 상태: 완전`이므로 확인 가능했다 |
| **Dual Adaptation / Chronos 질소예측 / ACM 논문 3건의 "인용 금지" 처리** | **정확·적절** | 원문 미확보 상태를 정직하게 표시했고 취소선·금지 표기가 일관됨. 이번 검증에서도 재확보 시도하지 않았으므로 **여전히 확인 불가** |
| **요약 "확인하지 못한 것" 1번 (세 논문 References 미확인)** | **해소됨** | 본 로그 작업 1로 완료 |

### 2.3 지어낸 내용(환각) 점검

로컬 원문이 있는 5건에 대해 **표의 모든 사실 주장을 원문과 1:1 대조**했다. **사실관계를 지어낸 항목은 없다.** 문제는 전부 (a) 인용부호 사용의 부정확(2건), (b) 확인 수준의 과대/과소 표기(3건)에 국한된다. 특히 원문 미확보 문헌 3건을 취소선·"인용 금지"로 명시적으로 격리한 처리는 적절하며, 이 부분에서 환각 위험은 통제되어 있다고 판단한다.

---

## 원 요약 파일에 반영이 필요한 수정 제안 (직접 수정하지 않음)

우선순위 순.

1. **[중요·인용 정확성] Mix, Don't Pick 행의 영문 직접인용 2건을 손볼 것.**
   - `"generator rankings differ substantially between Chronos-T5-Mini and Moirai-Small"` → 원문 문장으로 교체: `"generator rankings are not stable across architectures"` (또는 인용부호를 풀고 의역으로 표시).
   - Conclusion 인용문 `"synthetic data should not be treated as a monolithic category…"` → 인용부호를 제거하고 "(Conclusion 요지, 로컬 사본은 한국어 번역만 보유 — 영문 원문 대조 미완)"로 표기. 논문에 영문 그대로 인용하려면 arXiv HTML에서 해당 문단을 재확보할 것.

2. **[중요·정확성] TimeTic 행의 "금융 도메인 특정 언급은 Abstract에서 확인 안 됨"을 수정.**
   → "Abstract에는 없으나 Introduction에서 finance를 데이터 부족 도메인의 대표 사례로 명시(Fu et al., 2024 인용)"로 갱신. 이로써 TimeTic은 금융 맥락에서도 인용 가능성이 올라간다.

3. **[중간·정직성 상향] 원문 확인 수준 표기 3건을 로컬 사본의 실제 상태에 맞게 조정.**
   - Mix, Don't Pick: "전문 확인(Abstract~Conclusion)" → "본문 전체 + Table 1~4 + Conclusion/Impact Statement 확인, **Appendix B~I 미확보**"
   - Adversarial Robustness: "Abstract + Introduction 확인" → "본문 전체(Discussion/Broader Impacts 포함) 확인, References/Appendix 미확보"
   - Data Similarity & Diversity: "Abstract 확인" → "Abstract~6장 도입부 확인, 6장 후반·결론·References 미확보"

4. **[중간·구조] "확인하지 못한 것" 1번 항목을 해소 처리하고 본 로그를 참조로 걸 것.**
   → "3편 References 총 98건 전수 확인 완료(2026-08-15, `검증로그_하위갈래D.md`). negative transfer 관련 인용 0건 — 독립 키워드 검색으로 대체한 데 따른 문헌 손실 없음."로 교체.

5. **[중간·신규 추가] 표 하단 또는 별도 절에 "3편 References에서 발굴된 인접 후보(원문 미확인)" 6건(N1~N6)을 신뢰도 최하 등급으로 추가.**
   특히 다음 3건은 확보 우선순위가 높다고 본다.
   - **2510.03358** (Rank Structure / Flow-of-ranks) — Internal Semantics와 짝을 이루는 표현론적 근거
   - **2409.12915** (Wiliński et al.) — Internal Semantics가 자인한 최근접 선행연구인데 우리 목록에 빠져 있음
   - **Cartea et al. (2025) "The Limited Virtue of Complexity in a Noisy World"** — 저SNR이 대형모델을 무너뜨린다는 금융계량 쪽 이론적 대응물

6. **[낮음·논지 강화] 종합 소견에 작업 1의 메타 발견을 한 문단 추가 제안.**
   → "세 편의 핵심 실패보고(2511.05619 / 2511.18578 / 2511.15324)는 References 총 98건 중 negative transfer 계열 문헌을 단 한 건도 인용하지 않으며 서로도 인용하지 않는다. TSFM 실패 분석은 아직 누적적 문헌군을 이루지 못한 파편화 상태이고, 이는 본 연구가 겨냥하는 공백의 1차 증거다." — 단, 세 편이 모두 2025년 11월 동시기 arXiv 공개라 상호인용이 물리적으로 어려웠다는 단서를 반드시 병기할 것.

---

## 이번 검증에서도 여전히 "확인 불가"인 것

1. **Dual Adaptation of TSFM for Financial Forecasting (ICML 2025)** — 이번 세션에서 재확보를 시도하지 않음. 원문 미확인 유지, 인용 금지.
2. **Chronos 질소예측 논문 (ScienceDirect S2589914725001677)** — 유료 접근, 재시도 안 함. 인용 금지 유지.
3. **ACM DL "TSFM in Finance: Pretraining Corpora…" (10.1145/3785706.3785728)** — 재시도 안 함. 인용 금지 유지.
4. **신규 후보 N1~N6 전부** — 서지정보(제목·저자·ID)만 확인했고 **초록조차 읽지 않았다**. 관련성 설명은 인용 문맥(Cited by 정보)과 제목에서 추론한 것이므로, 논문에 쓰려면 반드시 원문 확보 후 재검증할 것.
5. **Re(Visiting)의 Section 4.2~6 및 Appendix 본문** — 이번에는 References(`#bib`)만 추출했고 본문 나머지는 여전히 미확보. 로컬 사본의 "[수집 중단 지점]" 상태 그대로다.
6. **Mix, Don't Pick의 영문 Conclusion 원문** — 로컬 사본이 한국어 번역만 보유. 영문 직접인용이 필요하면 재확보 필요.
