# Moirai 파일럿 검증 결과 (5단계 - 가설·실험·검증)

- 대상 모델: `Salesforce/moirai-1.0-R-small` (사전학습 TSFM, 분위수/혼합분포 출력형)
- 대상 축: 변동성 군집(volatility clustering), GARCH(1,1) 합성 데이터
- 목적: Moirai가 zero-shot으로 CRPS 계산 가능한 확률적 출력을 실제로 내놓는지 확인 (파이프라인 기술 검증)
- 실행일: 2026-08-25

## (a) 설치·로딩 성공 여부

- 패키지 설치: **성공** (`torch`, `uni2ts`, `arch`, `gluonts` 등). 단, 다수의 버전 충돌을 수동으로 해결해야 했음 (아래 (f) 참조).
- **사전학습 체크포인트 로딩: 실패.** `MoiraiModule.from_pretrained("Salesforce/moirai-1.0-R-small")` 호출 시 `httpx.ProxyError: 403 Forbidden`. 이 샌드박스 환경의 아웃바운드 네트워크 정책이 `huggingface.co` 및 미러(`hf-mirror.com`) 접속을 전면 차단하고 있어, 실제 사전학습 가중치를 다운로드할 수 없었다. `pypi.org`는 허용되어 패키지 설치는 문제없었다.
- 대안으로, uni2ts가 실제 사용하는 것과 **동일한 아키텍처**(`MoiraiModule`: patch embedding + Transformer encoder + Mixture 분포 헤드[StudentT + NegativeBinomial + LogNormal + NormalFixedScale])를 공개된 moirai-1.0-R-small 하이퍼파라미터(d_model=384, num_layers=6, patch_sizes=(8,16,32,64,128))로 **무작위 초기화**하여 구성, 파이프라인 레벨 검증을 대체 수행했다. → **이 파일럿은 "예측 품질"이 아니라 "확률적 출력 → CRPS/PIT 계산 파이프라인의 기술적 성립 여부"를 검증한 것**이다.

## (b) 출력 형태

- `MoiraiForecast` (uni2ts의 GluonTS 어댑터) + `create_predictor()`로 GluonTS `PyTorchPredictor`를 얻고, `PandasDataset`으로 context를 넣어 `predict()` 호출 시 GluonTS `SampleForecast` 객체가 반환됨을 확인.
- **샘플 추출 가능**: `forecast.samples` (shape: `(num_samples=100, horizon=24)`) 정상 접근됨.
- **분위수 추출 가능**: `forecast.quantile(q)` 메서드가 각 분위수 수준(0.05~0.95)에 대해 정상 동작함 (샘플 기반 empirical quantile로 계산됨).
- Moirai의 혼합분포(Mixture of StudentT/NegBin/LogNormal/NormalFixedScale) 파라미터 자체(각 성분의 mixture weight, 위치/척도 파라미터)에 대한 직접 접근은 이번 파일럿에서는 시도하지 않았으나(모델 forward 출력이 `distr_output.distribution(...)`을 통해 PyTorch `Distribution` 객체로 노출되는 구조이므로), API상 접근이 가능한 구조임은 소스 확인으로 파악됨. 본실험에서 필요하면 `MoiraiModule.forward()` 를 직접 호출해 분포 파라미터 텐서에 접근하는 경로도 열려 있다.
- 결론: **분위수 기반 CRPS와 샘플 기반 CRPS 모두 계산 가능한 출력 구조**를 실제로 확인함.

## (c) 시계열별 CRPS 값과 평균

10개 GARCH(1,1) 합성 시계열(context=512, horizon=24)에 대해 계산. (무작위 초기화 모델이므로 절대값 자체는 의미 없고, **계산이 정상 수행된다는 사실**이 핵심.)

| series_id | CRPS (분위수 근사, pinball×2) | CRPS (샘플 empirical) | PIT 평균 | PIT 표준편차 |
|---|---|---|---|---|
| garch_00 | 20.74 | 20.79 | 0.010 | 0.020 |
| garch_01 | 15.98 | 16.16 | 0.023 | 0.033 |
| garch_02 | 12.04 | 12.45 | 0.043 | 0.048 |
| garch_03 | 14.88 | 15.07 | 0.024 | 0.029 |
| garch_04 | 1.10 | 1.17 | 0.775 | 0.117 |
| garch_05 | 9.60 | 10.06 | 0.132 | 0.120 |
| garch_06 | 12.60 | 12.81 | 0.025 | 0.038 |
| garch_07 | 2.34 | 3.03 | 0.387 | 0.199 |
| garch_08 | 2.31 | 2.61 | 0.696 | 0.128 |
| garch_09 | 7.19 | 7.58 | 0.931 | 0.051 |
| **평균** | **9.88** | **10.17** | **0.305** | – |

두 CRPS 계산 방식(분위수 pinball-loss 근사와 샘플 기반 energy-form empirical 근사)의 값이 서로 매우 근접(시계열별 오차 대체로 3~9% 내외) → **상호 검증 결과 일관됨**, CRPS 계산 로직 자체는 신뢰할 만함.

## (d) PIT 값 요약

- 시계열별 PIT 평균이 0.01~0.93으로 넓게 퍼져 있고 전체 평균은 0.305로 0.5(이상적 캘리브레이션)에서 크게 벗어남. **이는 예상된 결과**다 — 모델이 무작위 초기화 상태이므로 실제 가격 레벨(예: 100 근처)과 무관한 스케일의 분포를 출력하며, 당연히 캘리브레이션이 되어 있지 않다.
- 핵심은 값의 방향성이 아니라 **PIT 계산 자체가 문제없이 수행된다는 것**(각 horizon 시점에서 `mean(samples <= y_true)`로 empirical CDF 값 추출 가능) — 본실험에서 실제 사전학습 가중치로 이 계산을 그대로 재사용하면 캘리브레이션 진단(히스토그램, KS 검정 등)으로 바로 이어질 수 있음을 확인.

## (e) 소요 시간

- 데이터 생성(GARCH 10개): 0.01초
- 모델 로딩(무작위 초기화, small): 0.12초 (참고: 사전학습 로딩은 정책상 시도 불가 — 목록엔 실패 시각까지만 기록)
- 예측 실행(10개 시계열, context 512 → horizon 24, num_samples=100, CPU): **0.53초**
- 전체 파이프라인(데이터 생성~CRPS/PIT 계산): 1초 미만

CPU 기준으로 매우 가벼움 — small 체크포인트는 본실험 규모(3축 × 여러 모델 × 많은 시나리오)로 확장해도 연산 자원 문제는 없을 것으로 판단됨.

## (f) 발생한 에러/이상 징후

1. **[치명적] HuggingFace 접근 차단**: `huggingface.co`, `hf-mirror.com` 모두 프록시에서 403 Forbidden. 사전학습 가중치를 이 클라우드 샌드박스에서 직접 받을 수 없음. 본실험 전에 반드시 해결 필요 (조직 네트워크 정책 예외 요청, 또는 로컬/다른 환경에서 체크포인트를 미리 받아 이 환경에 업로드하는 방식 등).
2. **[해결됨] 의존성 버전 충돌 다수**: `uni2ts==2.0.0`이 요구하는 `torch<2.5`, `gluonts~=0.14.3`, `numpy~=1.26.0`, `jaxtyping~=0.2.24`, `jax[cpu]` 등이 환경의 최신 버전들과 충돌. `--no-deps` 개별 설치 + 버전 고정(`jaxtyping==0.2.24`, `jax[cpu]==0.4.30`, `numpy<2`, `torchmetrics` 수동 추가)으로 해결. `torch` 설치 과정에서 한 번 파일시스템 오류로 깨졌다가 재설치로 복구됨(원인 불명, 재현 시 재설치로 대응 가능).
3. **[정보성] gluonts 버전 불일치**: 설치된 `gluonts==0.17.0`이 uni2ts 요구사항(`~=0.14.3`)보다 높지만, 이번 파일럿에서 사용한 API(`PandasDataset`, `SampleForecast.samples`, `.quantile()`) 기준으로는 문제없이 동작함. 본실험에서 더 깊은 기능을 쓸 경우 재확인 필요.
4. 그 외 실행 중 예외나 NaN/Inf 값은 관측되지 않음.

## (g) 본실험 확장 가능성 판단

**조건부 가능(Conditional Go).**

- **기술적 파이프라인 자체는 문제없이 성립한다**: Moirai(GluonTS 어댑터)의 확률적 출력에서 분위수와 샘플을 모두 추출할 수 있고, 이를 이용한 CRPS(두 가지 계산 방식 모두) 및 PIT 계산이 실제로 정상 작동함을 확인했다. 연산 속도도 CPU 기준 시계열 10개/1초 미만으로, 3축×여러 모델×많은 시나리오 규모로 확장해도 계산 자원 문제는 없을 것으로 판단된다.
- **단, 유일하지만 결정적인 선결 과제는 네트워크 접근이다.** 사전학습 가중치를 이 클라우드 환경에서 직접 받을 수 없다는 것은 "zero-shot 확률 예측 품질"이라는 연구의 핵심 검증을 이 환경에서는 수행할 수 없다는 뜻이다. 본실험 착수 전 다음 중 하나가 반드시 필요하다:
  1. 조직 네트워크 정책에 huggingface.co(혹은 필요한 특정 리포지토리)에 대한 예외를 요청, 또는
  2. 네트워크 제약이 없는 별도 환경(로컬 PC 등)에서 `moirai-1.0-R-small`(및 필요시 base/large) 체크포인트를 미리 다운로드하여 이 프로젝트의 작업 공간에 업로드 후 `from_pretrained`의 로컬 경로 로딩 기능을 사용.
- 위 문제만 해결되면, 이번에 작성한 `pilot_moirai.py`의 데이터 생성/예측/CRPS/PIT 계산 구조를 그대로 본실험 코드의 기반으로 사용할 수 있다(체크포인트 로딩 함수의 `from_pretrained` 인자만 로컬 경로로 바꾸면 됨).
- 참고로 Chronos(자기회귀 샘플링형)를 검증 중인 별도 에이전트도 동일한 HuggingFace 차단 문제에 부딪혔을 가능성이 높다 — 본실험 설계 단계에서 이 네트워크 이슈를 공통 선결 조건으로 다뤄야 한다.

## 파일 목록

- `pilot_moirai.py` — 파일럿 스크립트 (데이터 생성, 모델 로딩, 예측, CRPS/PIT 계산 전체 파이프라인)
- `pilot_moirai_results.csv` — 시계열별 CRPS/PIT 상세 결과
- `pilot_run_log.txt` — 실행 로그
- `results.md` — 본 문서
