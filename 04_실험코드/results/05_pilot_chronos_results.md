# Chronos Zero-shot CRPS 파일럿 검증 결과

- 검증 범위: 3축(변동성 군집 / 두꺼운 꼬리 / 체제전환) 중 **변동성 군집** 1축만
- 목적: "사전학습 TSFM(Chronos)이 zero-shot으로 CRPS 계산이 가능한 확률적 출력을 실제로 내놓는가"만 확인
- 실행 환경: 클라우드 워크스페이스(cwd) 내 `pilot_chronos/`, GPU 없음(CPU), 아웃바운드 HTTPS는 조직 정책 프록시를 경유

## (a) 설치·로딩 성공 여부 — **부분 성공**

| 항목 | 결과 |
|---|---|
| torch (CPU) 설치 | 성공 (여러 번 재설치 끝에) |
| chronos-forecasting, arch, gluonts 설치 | 성공 |
| GARCH(1,1) 합성 데이터 생성 | 성공 |
| `amazon/chronos-t5-tiny` 로드 (HuggingFace Hub) | **실패 — 네트워크 정책 차단** |
| CRPS/PIT 계산 코드 경로 | 성공 (합성 샘플로 별도 검증) |

**핵심 블로커**: 이 클라우드 세션의 아웃바운드 프록시가 `huggingface.co`를 조직 egress 정책으로 차단한다
(`403 Forbidden`, `connect_rejected: policy denial`). 프록시 allowlist에는 `pypi.org`,
`files.pythonhosted.org`, `registry.npmjs.org` 등 패키지 레지스트리만 포함되어 있고
모델 허브(huggingface.co)는 포함되어 있지 않다. 이는 우회 대상이 아닌 명시적 정책 차단이므로
그대로 보고한다.

따라서 **실제 Chronos 모델을 통한 zero-shot 추론은 이 환경에서 실행하지 못했다.**
아래 (b)~(d)는 두 부분으로 나눠 보고한다: ① 코드/파이프라인 관점에서 검증된 사실(문헌·API 스펙 기반 확인),
② 이번 세션에서 실측하지 못한 부분.

## 설치 관련 부수 이슈 (참고)

- 기본 `pip install torch`는 PyPI에서 CUDA 포함 빌드(2.13.0+cu130, ~2GB의 nvidia-* 패키지 동반)를 받아온다.
  `download.pytorch.org`(CPU 전용 wheel 인덱스)도 프록시에서 차단되어 있어 대안 인덱스를 쓰지 못했다.
- 환경에 사전 설치되어 있던 구버전 torch(2.4.1, cu12 계열 nvidia 패키지 동반)와 새로 설치한
  torch(cu13 계열)가 공존하며 `nvidia-nccl-cu12`/`cu13` 심볼 충돌
  (`undefined symbol: ncclCommResume`)을 일으켰다. cu12 계열 nvidia 패키지를 모두 제거하고
  `pip install --force-reinstall torch`로 정리한 뒤에야 `import torch`가 정상 동작했다.
- CPU 전용으로만 쓸 것이므로 실제로는 CUDA 관련 패키지가 전혀 필요 없다 — 본실험 환경에서는
  처음부터 CPU 전용 wheel(가능하면 `download.pytorch.org`가 허용된 환경에서)을 쓰거나,
  최소한 사전 설치된 torch와의 충돌을 피하기 위해 가상환경(venv) 격리를 권장한다.

## (b) 출력 형태 — 이번 세션에서 실측 불가 (모델 미로딩)

Chronos 공식 API(`ChronosPipeline.predict`)는 문서/소스 기준으로
`forecast[num_series, num_samples, horizon]` 형태의 샘플 텐서를 반환하며,
`np.quantile(samples, q, axis=1)`로 임의 분위수 추출이 가능한 구조다.
파일럿 스크립트(`pilot_chronos.py`)에는 이 출력 shape을 로깅하고
`pilot_result.json`에 기록하는 코드를 작성해 두었으나, 모델 로딩이 막혀
**이번 세션에서는 실제 shape 값을 확인하지 못했다.**

## (c) 시계열별 CRPS 값 — 이번 세션에서 실측 불가

동일한 이유로 8개 GARCH(1,1) 합성 시계열에 대한 실제 Chronos 예측 기반 CRPS는
계산하지 못했다. 대신 **CRPS 계산 로직 자체는 임의의 합성 샘플(가짜 정규분포 샘플)로
별도 검증**했고, 정상 작동을 확인했다:

- 분위수 기반 근사(pinball loss 평균 x2)와 샘플 기반 경험적 CRPS
  (`E|X-y| - 0.5*E|X-X'|`)가 서로 근접한 값을 산출함 (예: h=0에서 0.480 vs 0.469).
- 즉, "모델이 샘플/분위수를 반환하기만 하면" CRPS 계산 자체는 이 코드로 문제없이 수행된다.

## (d) PIT 값 요약 — 이번 세션에서 실측 불가 (동일 사유), 계산 로직만 검증

PIT(`P(X<=y_true)`를 샘플의 경험적 CDF로 추정)도 CRPS와 같은 합성 샘플 테스트에서
정상적으로 계산됨을 확인했다 (예: pit=0.490, 정규분포 대칭성에 부합하는 값).
실제 Chronos 출력에 대한 PIT 분포(사분위수 등)는 모델 접근이 막혀 산출하지 못했다.

## (e) 소요 시간

- GARCH(1,1) 합성 데이터 생성 (8개 시계열, context 512 + horizon 24): < 1초
- 패키지 설치(torch, chronos-forecasting, arch, gluonts) + 충돌 해결: 약 10분
  (대부분 torch/nvidia 패키지 충돌 디버깅 시간)
- 모델 로딩 시도: 즉시 실패 (네트워크 차단, 수 초 이내 에러)

## (f) 발생한 에러/이상 징후

1. `huggingface.co:443` — `403 Forbidden` (egress 정책 차단). **가장 중요한 이슈.**
2. `pip install torch` 기본 인덱스가 CUDA 포함 대형 빌드를 받아옴 (`download.pytorch.org` CPU 인덱스도 차단됨).
3. 사전 설치된 torch(cu12 계열)와 신규 설치 torch(cu13 계열) 공존으로 `undefined symbol: ncclCommResume` 발생 — cu12 nvidia 패키지 제거 후 해결.
4. gluonts에는 "샘플 배열을 넣으면 CRPS 스칼라가 나오는" 단일 함수형 유틸이 없음 (Forecast 객체 + Evaluator 클래스 기반). 그래서 pinball-loss 근사와 경험적 CRPS 공식을 직접 구현하는 방식으로 대체함 — 이 방식이 표준적이고 본실험에도 그대로 쓸 수 있음.

## (g) 본실험 확장 가능성 판단

**조건부로 "기술적으로 문제없음"** — 단, 아래 전제가 충족되어야 한다.

- **필수 선결 과제**: 이 클라우드 세션 환경에서는 `huggingface.co` 접근이 막혀 있어
  Chronos든 다른 사전학습 TSFM(TimesFM, Moirai 등)이든 **모델 가중치를 받아올 수 없다.**
  본실험을 이 환경에서 계속하려면 다음 중 하나가 필요하다:
  - 조직 관리자에게 `huggingface.co` (필요시 `cdn-lfs.huggingface.co` 등 관련 CDN)를 egress
    allowlist에 추가 요청, 또는
  - 모델 가중치를 사전에 다운로드하여 (allowlist에 있는) 다른 채널(예: 사설 패키지 레지스트리,
    프로젝트에 업로드된 파일)로 반입하는 방식, 또는
  - HuggingFace 접근이 허용되는 별도 환경(로컬/다른 클라우드)에서 실행.
- **파이프라인 자체는 문제없어 보임**: GARCH 합성 데이터 생성, CRPS(분위수/경험적 양쪽 방식),
  PIT 계산 코드는 모두 정상 동작을 확인했고, `amazon/chronos-t5-tiny`가 아니더라도 API 스펙상
  샘플 텐서를 반환하는 모델이라면 동일 코드로 그대로 CRPS/PIT을 산출할 수 있는 구조로 작성했다.
  본실험에서 3축(변동성 군집/두꺼운 꼬리/체제전환) x 여러 모델 x 많은 시나리오로 확장할 때도
  `build_series`류 함수와 `crps_from_*`/`pit_value` 함수를 재사용하면 된다.
  다만 시계열 개수·horizon이 늘어나면 `crps_from_samples_empirical`의 O(n_samples^2) 비용을
  주의해야 한다 (샘플 수를 100 내외로 유지하거나 벡터화를 강화할 것).
  CPU 추론 자체는 tiny 모델 기준으로 시계열당 수 초 내외로 예상되어(공식 벤치마크 기준), 수십~수백
  시나리오 규모라면 CPU만으로도 감당 가능할 것으로 보인다(단, 실측은 못 했음).
- **결론**: 코드/방법론 리스크는 낮음. 실질적 리스크는 전적으로 "이 클라우드 세션의 네트워크
  allowlist에 HuggingFace가 없다"는 인프라 문제 하나로 귀결된다. 이 부분이 해결되면 본실험 확장은
  기술적으로 무리가 없다고 판단한다.

## 산출물

- `pilot_chronos/pilot_chronos.py` — 파이프라인 전체 스크립트 (한글 주석, 섹션 구분)
- `pilot_chronos/pilot_result.json` — 이번 실행의 (부분) 결과 및 에러 로그
- `pilot_chronos/pilot_log.txt` — 실행 로그
