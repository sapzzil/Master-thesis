# ABSTRACT

### Prediction Intervals of Pretrained Time Series Foundation Models for Financial Returns: Sources of Error and Training-Free Post-hoc Calibration

> Kim, Seungmin
> Dept. of Artificial Intelligence Convergence
> Graduate School of Hanyang University

Time series foundation models (TSFMs) produce prediction intervals without task-specific training, but whether these intervals keep their nominal coverage on financial returns has not been systematically tested. This thesis diagnoses whether miscoverage of TSFM 80% intervals stems from financial stylized facts or from the model and its usage settings, evaluates performance on real equities, and tests whether a training-free post-hoc calibration can restore coverage.

We generate 17 synthetic scenarios whose feature strengths (volatility clustering, heavy tails, regime-switching frequency and magnitude) are calibrated to ten U.S. and Korean large-cap stocks, varying one feature at a time under common random numbers. Four TSFMs (Chronos-T5, Chronos-2, TimesFM-2.5, Moirai-2.0) are evaluated on next-day log returns under four settings (21- or 252-day context; return or price input), and the same protocol is applied to the ten stocks over 2017–2026 (24,132 forecasts). All settings and tests were preregistered.

Even on feature-free data, TSFM coverage already ranged from 14% to 88% depending on model and setting, while raising feature strength to the strongest observed level moved coverage mostly within 3 percentage points. Only volatility clustering reduced coverage in some settings; heavy tails and frequent regime switching increased it, a consequence of variance-based 80% intervals under leptokurtic distributions. Real-stock coverage matched feature-free synthetic coverage within 1.0 point on average (excluding the two collapsed Chronos-T5 return-input settings; 1.2 points across all 19). On real stocks, quantile loss was worse than a historical-volatility Gaussian benchmark in 13 of 16 settings. Adaptive conformal quantile calibration (ACI-CQR) restored coverage to 80% in all 340 synthetic and 19 real model-settings, at the cost of intervals 6–48% wider than the oracle. In exploratory analyses, calibrated intervals also restored the intended risk levels in a volatility-targeting strategy and in VaR backtests.

TSFM interval errors in finance thus arise mainly from model and input settings; with setting checks and post-hoc calibration, TSFM intervals are usable for risk measurement, although their accuracy does not exceed a simple benchmark.

Keywords: time series foundation model, prediction interval, coverage, controlled synthetic experiment, conformal prediction, stock returns
