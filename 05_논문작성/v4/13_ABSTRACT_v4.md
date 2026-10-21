# ABSTRACT

### Prediction Intervals of Pretrained Time Series Foundation Models for Financial Returns:<br>Sources of Error and Training-Free Post-hoc Calibration

> Kim, Seungmin
> Dept. of Artificial Intelligence Convergence
> Graduate School of Applied Artificial Intelligence
> Hanyang University

Time series foundation models (TSFMs) produce prediction intervals without task-specific training, but whether these intervals keep their nominal coverage on financial returns has not been systematically tested. This thesis diagnoses whether miscoverage of TSFM 80% intervals stems from financial stylized facts or from the model and its usage settings, evaluates performance on real equities, and tests whether a training-free post-hoc calibration can restore coverage.

We generate 17 synthetic scenarios whose feature strengths (volatility clustering, heavy tails, regime-switching frequency and magnitude) are calibrated to ten U.S. and Korean large-cap stocks, varying one feature at a time under common random numbers. Four TSFMs (Chronos-T5, Chronos-2, TimesFM-2.5, Moirai-2.0) are evaluated on next-day log returns under four settings (21- or 252-day context; return or price input), and the same protocol is applied to the ten stocks over 2017–2026 (24,132 forecasts). Hypotheses and decision rules were specified before the experiments.

Even on feature-free data, TSFM coverage already ranged from 75% to 88% depending on model and setting, with half of the 16 settings outside the 80 ± 2% band. Raising feature strength to the strongest observed level moved coverage mostly within 3 percentage points. Only volatility clustering reduced coverage in some settings; heavy tails and frequent regime switching increased it, a consequence of variance-based 80% intervals under leptokurtic distributions. During the experiments we also found that the library's default sampling setting alone collapsed Chronos-T5 coverage on return inputs to 14%; reported results use the corrected setting. Real-stock coverage differed from feature-free synthetic coverage by 1.1 percentage points on average (at most 3.6) across all 19 model-settings. On real stocks, quantile loss was larger than that of a historical-volatility Gaussian benchmark in 12 of 16 settings. Adaptive conformal quantile calibration (ACI-CQR) restored average (unconditional) coverage to 80% in all 340 synthetic and 19 real model-settings, at the cost of intervals 5–48% wider than the oracle. In exploratory analyses, calibrated intervals brought realized volatility in a volatility-targeting strategy to 1.05–1.14 times the target and 10% VaR violation rates to 8.6–10.8%, although violation clustering remained in some settings.

These results show that the reliability of TSFM intervals on financial returns is governed by model and input settings rather than by stylized facts, and that synthetic experiments calibrated to real markets can anticipate real-stock coverage. Distributional accuracy did not exceed the simple benchmark, reaching parity only in the best settings (one-year return input for all four models). Current TSFMs are therefore better used not as return forecasters but as risk-measurement tools, after checking models and usage settings and applying training-free post-hoc calibration.

Keywords: time series foundation model, prediction interval, coverage, controlled synthetic experiment, conformal prediction, stock returns
