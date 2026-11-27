"""L1(특성 없음)에서 캘리브레이션 오차를 평균 폭·폭 흔들림·중심 이동으로 나눈 탐색 분석 그림 (사후 추가 분석, 198차 이후).
입력: 04_실험코드/results_v4_width/L1_scored_days.parquet (scored_v4.parquet에서 L1·채점일만 추출)
"""
import sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, koreanize_matplotlib  # noqa
from matplotlib.lines import Line2D
from scipy.stats import norm
plt.rcParams.update({"figure.dpi": 200, "font.size": 12, "axes.unicode_minus": False})
src, out = sys.argv[1], sys.argv[2]
t = pd.read_parquet(src)
Z = norm.ppf(0.9); SIG = 0.02698795 / Z          # L1 참 분포: 평균 0, 하루 변동 2.106%
NM = {"chronos_t5_base": "Chronos-T5", "chronos2": "Chronos-2", "timesfm25": "TimesFM-2.5", "moirai2": "Moirai-2", "rw": "RW", "garch_t": "GARCH-t"}
COL = {"chronos_t5_base": "#7f7f7f", "chronos2": "#1f77b4", "timesfm25": "#d62728", "moirai2": "#2ca02c", "rw": "k", "garch_t": "#9467bd"}
CONDS = [(21, "return"), (21, "price"), (252, "return"), (252, "price")]
CO = [(m, L, k) for m in ["chronos_t5_base", "chronos2", "timesfm25", "moirai2"] for L, k in CONDS] + [("rw", 21, "return"), ("rw", 252, "return"), ("garch_t", 252, "return")]
lab = lambda m, L, k: f"{NM[m]} {'한 달' if L == 21 else '1년'}·{'수익률' if k == 'return' else '가격'}" if m in NM and m not in ("rw", "garch_t") else f"{NM[m]} {'한 달' if L == 21 else '1년'}"
rows = []
for m, L, k in CO:
    g = t[(t.model == m) & (t.L == L) & (t.input == k)]
    lo, hi = g.lo.values, g.hi.values; w = hi - lo
    p = norm.cdf(hi / SIG) - norm.cdf(lo / SIG); pc = 2 * norm.cdf(w / (2 * SIG)) - 1; pf = 2 * norm.cdf(w.mean() / (2 * SIG)) - 1
    rows.append(dict(m=m, L=L, k=k, lab=lab(m, L, k), r=w.mean() / (2 * Z * SIG), a=(pf - .8) * 100, b=(pc.mean() - pf) * 100,
                     c=(p.mean() - pc.mean()) * 100, exp=(p.mean() - .8) * 100, act=(g.cover.mean() - .8) * 100))
d = pd.DataFrame(rows); d.round(2).to_csv(f"{out}/L1_분해.csv", index=False, encoding="utf-8-sig")

# 그림 1: 한 계열에서 구간이 어떻게 움직이는지
u = "1"   # 두 조건의 이 계열 커버리지가 조건 평균에 가까운 계열(한 달·가격 76.7%, 1년·수익률 80.0%)
fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
for ax, (m, L, k) in zip(axs, [("moirai2", 21, "price"), ("moirai2", 252, "return")]):
    g = t[(t.model == m) & (t.L == L) & (t.input == k) & (t.unit == u)].sort_values("day")
    x = g.day.values - 20
    ax.axhspan(-Z * SIG * 100, Z * SIG * 100, color="#dddddd", label="정답 80% 구간(폭 일정)")
    ax.fill_between(x, g.lo * 100, g.hi * 100, color=COL[m], alpha=.25, step="mid", label="모델 80% 구간")
    ax.plot(x, (g.lo + g.hi) / 2 * 100, color=COL[m], lw=1.2, label="모델 구간의 가운데")
    hit = g.cover.values
    ax.scatter(x[hit], g.y[hit] * 100, s=14, color="k", zorder=3, label="실제값(들어옴)")
    ax.scatter(x[~hit], g.y[~hit] * 100, s=40, marker="x", color="#d62728", zorder=3, label="실제값(빠짐)")
    ax.axhline(0, color="#999", lw=.6)
    ax.set_title(f"{lab(m, L, k)}  (이 계열 커버리지 {hit.mean()*100:.0f}%)", fontsize=12)
    ax.set_xlabel("평가일")
axs[0].set_ylabel("일별 수익률 (%)")
axs[0].legend(loc="lower left", fontsize=9, ncol=2)
fig.suptitle("같은 데이터(특성 없음, 계열 1개)에서 과거 길이·입력에 따라 구간이 움직이는 모습", fontsize=13)
fig.tight_layout(); fig.savefig(f"{out}/w1_구간_움직임.png"); plt.close()

# 그림 2: 쌓은 막대
fig, ax = plt.subplots(figsize=(14, 5.6))
x = np.arange(len(d))
for col, c, nm in [("a", "#9ecae1", "① 평균 폭"), ("b", "#fdae6b", "② 폭 흔들림"), ("c", "#bcbddc", "③ 중심 이동")]:
    v = d[col].values
    pos = np.where(v > 0, v, 0); neg = np.where(v < 0, v, 0)
    if col == "a":
        bp, bn = np.zeros(len(d)), np.zeros(len(d))
    ax.bar(x, pos, bottom=bp, color=c, edgecolor="white", width=.7, label=nm); ax.bar(x, neg, bottom=bn, color=c, edgecolor="white", width=.7)
    bp += pos; bn += neg
ax.scatter(x, d.act, color="k", s=40, zorder=4, label="실제 캘리브레이션 오차")
ax.axhline(0, color="k", lw=.8); ax.axhspan(-2, 2, color="#eeeeee", zorder=0)
for i in range(4, len(d), 4):
    if i <= 16: ax.axvline(i - .5, color="#888", ls=":", lw=1)
ax.set_xticks(x); ax.set_xticklabels(d.lab, rotation=55, ha="right", fontsize=10)
ax.set_ylabel("커버리지 − 80% (%p)")
ax.set_title("특성 없는 데이터(L1)의 캘리브레이션 오차를 세 부분으로 나눔  (옅은 띠 = ±2%p)", fontsize=13)
ax.legend(ncol=4, fontsize=10, loc="upper left")
fig.tight_layout(); fig.savefig(f"{out}/w2_분해_막대.png"); plt.close()

# 그림 3: 폭 비율 대 캘리브레이션 오차
fig, ax = plt.subplots(figsize=(8.5, 6))
r = np.linspace(.88, 1.36, 200)
ax.plot(r, (2 * norm.cdf(Z * r) - 1 - .8) * 100, color="#555", lw=1.5, label="폭이 매일 같고 가운데가 맞을 때(이론)")
for _, e in d.iterrows():
    full = e.L == 252; mk = "o" if e.k == "price" else "^"
    ax.scatter(e.r, e.act, s=90, marker=mk, facecolor=COL[e.m] if full else "white", edgecolor=COL[e.m], lw=1.8, zorder=3)
ax.axhline(0, color="k", lw=.6); ax.axvline(1, color="k", lw=.6, ls=":")
ax.set_xlabel("평균 폭 ÷ 정답 폭"); ax.set_ylabel("캘리브레이션 오차 (%p)")
ax.set_title("곡선보다 아래 = 평균 폭으로 기대한 것보다 덜 맞힘", fontsize=12)
h = [Line2D([], [], color=COL[m], lw=3, label=NM[m]) for m in ["chronos_t5_base", "chronos2", "timesfm25", "moirai2", "rw", "garch_t"]]
h += [Line2D([], [], ls="", marker="o", ms=9, mfc="#555", mec="#555", label="1년(찬 점)"), Line2D([], [], ls="", marker="o", ms=9, mfc="white", mec="#555", label="한 달(빈 점)"),
      Line2D([], [], ls="", marker="o", ms=9, mfc="#555", mec="#555", label="● 가격"), Line2D([], [], ls="", marker="^", ms=9, mfc="#555", mec="#555", label="▲ 수익률")]
ax.legend(handles=[ax.get_lines()[0]] + h, fontsize=9, loc="upper left")
fig.tight_layout(); fig.savefig(f"{out}/w3_폭비율_산점도.png"); plt.close()
print(d.round(2).to_string())
