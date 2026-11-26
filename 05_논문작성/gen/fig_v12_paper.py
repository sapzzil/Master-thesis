"""발표 v12 결과 그림: 논문 그림(4-2, 2-1, 5-3, 5-2, 6-1)과 같은 색·모양·구성을 쓰고 발표용으로 글씨만 키운다.
논문과 같은 규칙: 모델 색 = Chronos-T5 회색, Chronos-2 파랑, TimesFM-2.5 빨강, Moirai-2 초록, RW 검정, GARCH-t 보라.
입력 모양 = ● 가격, ▲ 수익률 (발표에서는 찬 모양 = 1년, 빈 모양 = 한 달을 더해 4조건을 구분).
사용: python3 fig_v12_paper.py → figs/v12/
"""
import pathlib
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, koreanize_matplotlib  # noqa: F401  (논문 그림과 같은 글꼴)
from matplotlib.lines import Line2D
from scipy import stats

_R = pathlib.Path(__file__).resolve().parents[2]
T = str(_R / "04_실험코드/results_v4_t5fix/tables") + "/"
T0 = str(_R / "04_실험코드/results_v4/tables") + "/"
OUT = str(_R / "05_논문작성/figs/v12") + "/"
plt.rcParams.update({"figure.dpi": 200, "font.size": 13, "axes.unicode_minus": False})

NM = {"chronos_t5_base": "Chronos-T5", "chronos2": "Chronos-2", "timesfm25": "TimesFM-2.5", "moirai2": "Moirai-2",
      "rw": "과거변동(RW)", "garch_t": "GARCH-t"}
COL = {"chronos_t5_base": "#7f7f7f", "chronos2": "#1f77b4", "timesfm25": "#d62728", "moirai2": "#2ca02c", "rw": "k", "garch_t": "#9467bd"}
TS = ["chronos_t5_base", "chronos2", "timesfm25", "moirai2"]
CONDS = [(21, "return"), (21, "price"), (252, "return"), (252, "price")]          # 논문 표·그림 순서
CO = [(m, L, k) for m in TS for L, k in CONDS] + [("rw", 21, "return"), ("rw", 252, "return"), ("garch_t", 252, "return")]


def lab(m, L, k):
    return f"{NM[m]} {'한 달' if L == 21 else '1년'}·{'수익률' if k == 'return' else '가격'}"


def mk(L, k):
    """입력 모양(● 가격, ▲ 수익률)은 논문과 같게, 찬 모양 = 1년, 빈 모양 = 한 달."""
    return dict(marker="o" if k == "price" else "^", full=(L == 252))


def dot(ax, x, y, m, L, k, s=70, z=3):
    d = mk(L, k)
    ax.scatter(x, y, s=s, marker=d["marker"], facecolor=COL[m] if d["full"] else "white", edgecolor=COL[m], lw=1.8, zorder=z)


def cond_legend(ax_or_fig, **kw):
    h = [Line2D([], [], ls="", marker=mk(L, k)["marker"], ms=9, mfc="#555" if mk(L, k)["full"] else "white", mec="#555", mew=1.6,
                label=f"{'한 달' if L == 21 else '1년'}·{'수익률' if k == 'return' else '가격'}") for L, k in CONDS]
    return ax_or_fig.legend(handles=h, frameon=False, **kw)


def model_legend(ax_or_fig, models, **kw):
    h = [Line2D([], [], color=COL[m], lw=3, label=NM[m]) for m in models]
    return ax_or_fig.legend(handles=h, frameon=False, **kw)


def grid(ax, axis="x"):
    ax.grid(axis=axis, alpha=.3)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


t1 = pd.read_csv(T + "T1_synth_scenarios.csv")
t4 = pd.read_csv(T + "T4_H5_synth.csv")
t6 = pd.read_csv(T + "T6_real_coverage_H5.csv")
t7 = pd.read_csv(T + "T7_H6_real.csv")
t10 = pd.read_csv(T0 + "T1_synth_scenarios.csv")
t60 = pd.read_csv(T0 + "T6_real_coverage_H5.csv")


def g1(df, m, L, k):
    return df[(df.model == m) & (df.L == L) & (df.input == k)]


# ---------- 8쪽: 금융 특성 강도와 커버리지 변화 (그림 4-2 바탕, 2×2) ----------
AX = {"CL": "변동성 군집", "TL": "두꺼운 꼬리", "RF": "국면 전환 빈도", "RS": "국면 전환 크기"}
fig, axs = plt.subplots(2, 2, figsize=(13, 8.4), sharex=True, sharey=True)
xs = [1, 2, 3, 4, 5]
for a, (code, name) in zip(axs.flat, AX.items()):
    a.axhspan(-2, 2, color="gray", alpha=.1); a.axhline(0, color="gray", lw=.8)
    for (m, L, k) in CO[:16]:
        g = g1(t1, m, L, k).set_index("scenario")["cov"]
        y = [0] + [100 * (g[f"{code}_L{i}"] - g["L1"]) for i in range(2, 6)]
        a.plot(xs, y, color=COL[m], lw=1.2, alpha=.6, ls="-" if k == "price" else "--", zorder=2)
        dot(a, xs[-1], y[-1], m, L, k, s=55)
    a.set_title(name, fontsize=16, fontweight="bold", loc="left")
    a.set_xticks(xs, ["L1", "L2", "L3", "L4", "L5"])
    grid(a, "y")
for a in axs[:, 0]:
    a.set_ylabel("L1 대비 커버리지 변화 (%p)")
axs[0, 0].set_ylim(-3.5, 4)
model_legend(fig, TS, loc="lower center", bbox_to_anchor=(0.5, 0.035), ncol=4, fontsize=12.5)
cond_legend(fig, loc="lower center", bbox_to_anchor=(0.5, -0.005), ncol=4, fontsize=12.5)
fig.text(0.5, 0.095, "선 = TSFM 16개 조건(실선 가격 입력, 점선 수익률 입력), 끝점 모양 = 입력 조건, 회색 띠 = 실질 기준 ±2%p", ha="center", fontsize=11.5, color="#555")
fig.tight_layout(rect=(0, .12, 1, 1)); fig.savefig(OUT + "p08_특성강도_변화.png", facecolor="white"); plt.close()

# ---------- 9쪽: 예상과 다른 발견 (왼쪽 그림 2-1, 오른쪽 이론 비교) ----------
nu = 3.56; s = np.sqrt((nu - 2) / nu); z = stats.norm.ppf(0.9)
x = np.linspace(-5, 5, 1000)
fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1.25, 1]})
a = axs[0]
a.plot(x, stats.norm.pdf(x), color="#1f77b4", lw=2.2, label="정규분포")
a.plot(x, stats.t.pdf(x / s, nu) / s, color="#d62728", lw=2.2, label=f"t분포 (ν = {nu}, 꼬리 L5)")
a.axvspan(-z, z, color="gray", alpha=.12, label="정규분포 기준 80% 구간")
a.set_xlim(-4, 4); a.set_xlabel("표준화한 수익률 (평균 0, 분산 1)"); a.set_ylabel("확률밀도")
a.legend(fontsize=12, loc="upper left", frameon=False)
a.set_title("분산이 같으면 t분포는 가운데가 더 높고 극단값이 더 자주 나온다", fontsize=13, loc="left")
grid(a, "y")
a = axs[1]; a.axis("off")
rows = []
for p in (0.80, 0.95, 0.99):
    zz = stats.norm.ppf((1 + p) / 2); c = 2 * stats.t.cdf(zz / s, nu) - 1
    rows.append((f"{p*100:.0f}% 구간", f"{c*100:.1f}%", c - p))
a.text(0.0, 0.93, "정규분포로 만든 구간에\n실제 데이터가 들어오는 비율 (꼬리 L5)", fontsize=14, fontweight="bold", va="top")
for i, (n, c, d) in enumerate(rows):
    y = 0.62 - i * 0.2
    col = "#1f77b4" if d > 0.005 else ("#d62728" if d < -0.005 else "#555")
    a.text(0.02, y, n, fontsize=17, va="center")
    a.text(0.40, y, "→", fontsize=17, va="center", color="#555")
    a.text(0.52, y, c, fontsize=19, va="center", fontweight="bold", color=col)
    a.text(0.80, y, "약속보다 높음" if d > 0.005 else ("약속보다 낮음" if d < -0.005 else "약속과 비슷"), fontsize=13, va="center", color=col)
a.text(0.0, 0.02, "이론 계산 (논문 표 4-3). 같은 방향이 Chronos-2의 98% 구간에서도 나타남(표 4-4)", fontsize=11, color="#555")
fig.tight_layout(); fig.savefig(OUT + "p09_꼬리_구간수준.png", facecolor="white"); plt.close()

# ---------- 10쪽: 모델별·입력 조건별 커버리지 차이 (L1, 모델별 묶음) ----------
rows = CO[:16][::-1]
fig, ax = plt.subplots(figsize=(11.5, 7.2))
ax.axvspan(78, 82, color="gray", alpha=.1); ax.axvline(80, color="k", lw=1)
for i, (m, L, k) in enumerate(rows):
    v = 100 * g1(t1, m, L, k).query("scenario=='L1'")["cov"].iloc[0]
    dot(ax, v, i, m, L, k, s=110)
    ax.text(v + 0.35, i, f"{v:.1f}", va="center", fontsize=11.5)
for yy in (3.5, 7.5, 11.5):
    ax.axhline(yy, color="#999", lw=1, ls=":")
ax.set_yticks(range(16), [lab(*c) for c in rows], fontsize=12)
for tl, (m, _, _) in zip(ax.get_yticklabels(), rows):
    tl.set_color(COL[m])
ax.set_xlim(73, 90)
dflt = [100 * g1(t10, "chronos_t5_base", L, "return").query("scenario=='L1'")["cov"].iloc[0] for L in (21, 252)]
ax.text(89.6, 0.3, f"Chronos-T5 수익률 입력을\n라이브러리 기본 설정(top-k = 50)으로 쓰면\n{min(dflt):.1f}~{max(dflt):.1f}% (그래프 범위 밖)",
        ha="right", va="bottom", multialignment="left", fontsize=12, color=COL["chronos_t5_base"], bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#999"))
ax.set_xlabel("커버리지 % (금융 특성 없는 합성 데이터 L1, 회색 띠 = 적정 범위 78~82%)")
cond_legend(ax, loc="upper left", bbox_to_anchor=(0.0, 1.07), ncol=4, fontsize=12)
grid(ax, "x"); ax.tick_params(axis="y", length=0)
fig.tight_layout(); fig.savefig(OUT + "p10_L1_조건별.png", facecolor="white"); plt.close()

# ---------- 13쪽: 합성 데이터와 실제 주가의 비교 (그림 5-3) ----------
a1 = t1[t1.scenario == "L1"].set_index(["model", "L", "input"])["cov"]
b1 = t6[t6.panel == "ALL"].set_index(["model", "L", "input"])["cov"]
j = pd.concat([a1, b1], axis=1, keys=["s", "r"]).dropna() * 100
fig, ax = plt.subplots(figsize=(9, 7.4)); lim = (73, 90)
ax.plot(lim, lim, color="gray", lw=1.2, ls="--"); ax.axvspan(78, 82, color="gray", alpha=.08); ax.axhspan(78, 82, color="gray", alpha=.08)
for (m, L, k), r in j.iterrows():
    dot(ax, r.s, r.r, m, L, k, s=110)
ax.set_xlim(*lim); ax.set_ylim(*lim)
ax.set_xlabel("합성 L1(특성 없음) 커버리지 %"); ax.set_ylabel("실제 10종목 커버리지 %"); ax.grid(alpha=.3)
ax.add_artist(ax.legend(handles=[Line2D([], [], color=c, marker="s", ls="", ms=10, label=NM[m]) for m, c in COL.items()], fontsize=12, loc="upper left", frameon=False))
md = (j.r - j.s).abs().mean(); mx = (j.r - j.s).abs().max()
ax.text(89.6, 73.4, f"점선 = 합성과 실제가 같음, 음영 = 80% ± 2%p\n19개 모델·조건 차이 평균 {md:.1f}%p, 최대 {mx:.1f}%p",
        ha="right", va="bottom", fontsize=11.5, color="#555", linespacing=1.6)
cond_legend(ax, loc="lower right", bbox_to_anchor=(1.0, 0.13), ncol=2, fontsize=11.5)
d0 = [(100 * g1(t10, "chronos_t5_base", L, "return").query("scenario=='L1'")["cov"].iloc[0],
       100 * t60[(t60.model == "chronos_t5_base") & (t60.L == L) & (t60.input == "return") & (t60.panel == "ALL")]["cov"].iloc[0]) for L in (21, 252)]
ax.text(73.4, 85.2, f"범위 밖: Chronos-T5 기본 설정(수익률)\n합성 {min(v[0] for v in d0):.0f}~{max(v[0] for v in d0):.0f}% → 실제 {min(v[1] for v in d0):.0f}~{max(v[1] for v in d0):.0f}%",
        fontsize=11.5, color=COL["chronos_t5_base"], va="top")
fig.tight_layout(); fig.savefig(OUT + "p13_합성_실제.png", facecolor="white"); plt.close()

# ---------- 14쪽: 기준 모형 대비 분포 정확도 (그림 5-2) ----------
rows = CO[:16][::-1]
fig, ax = plt.subplots(figsize=(11, 7.2))
ax.axvspan(-2, 2, color="gray", alpha=.1)
for i, (m, L, k) in enumerate(rows):
    r = t7[(t7.model == m) & (t7.L == L) & (t7.input == k)].iloc[0]; v = 100 * r.impr_vs_rw
    ax.barh(i, v, color=COL[m], alpha=.85 if r.p_holm < .05 else .35, height=.7)
    ax.text(v - 0.2 if v < 0 else v + 0.2, i, f"{v:+.1f}", va="center", ha="right" if v < 0 else "left", fontsize=11.5)
ax.axvline(0, color="k", lw=1.6)
for yy in (3.5, 7.5, 11.5):
    ax.axhline(yy, color="#999", lw=1, ls=":")
ax.set_yticks(range(16), [lab(*c) for c in rows], fontsize=12)
for tl, (m, _, _) in zip(ax.get_yticklabels(), rows):
    tl.set_color(COL[m])
ax.set_xlim(-12, 4)
ax.text(0.15, 16.0, "0 = 기준 모형(과거변동 RW)과 같음", fontsize=12, fontweight="bold", va="bottom")
ax.text(-11.8, 16.0, "← RW보다 손실이 큼 (TSFM이 나쁨)", fontsize=12, color="#555", va="bottom")
ax.set_ylim(-0.6, 16.9)
ax.set_xlabel("RW(같은 과거 길이) 대비 분위수 손실 개선 %\n진한 막대 = 유의(Holm 보정), 옅은 막대 = 유의하지 않음, 회색 띠 = 실질 기준 ±2%")
grid(ax, "x"); ax.tick_params(axis="y", length=0)
fig.tight_layout(); fig.savefig(OUT + "p14_RW대비_정확도.png", facecolor="white"); plt.close()

# ---------- 16쪽: 보정 후 커버리지 (그림 6-1, 모델별 묶음·점선) ----------
rows = CO[:19][::-1]
fig, axs = plt.subplots(1, 2, figsize=(14, 8.4), sharey=True)
for i, (m, L, k) in enumerate(rows):
    col = COL[m]
    g = g1(t4, m, L, k); a = t6[(t6.model == m) & (t6.L == L) & (t6.input == k) & (t6.panel == "ALL")].iloc[0]
    for ax, (b0, b1, c0, c1) in [(axs[0], (g["cov"].min(), g["cov"].max(), g.cal.min(), g.cal.max())), (axs[1], (a["cov"], a["cov"], a.cal, a.cal))]:
        x0 = 100 * (b0 + b1) / 2; x1 = 100 * (c0 + c1) / 2
        ax.annotate("", xy=(x1, i), xytext=(x0, i), arrowprops=dict(arrowstyle="->", color=col, lw=1.6))
        ax.plot([100 * b0, 100 * b1], [i, i], color=col, lw=7, alpha=.3, solid_capstyle="butt")
        ax.plot([100 * c0, 100 * c1], [i, i], color=col, lw=7, solid_capstyle="butt")
        ax.plot(x0, i, "o", mfc="white", mec=col, ms=7, mew=1.6); ax.plot(x1, i, "o", color=col, ms=7)
for ax, t in zip(axs, ["합성 17개 시나리오 (막대 = 시나리오 범위)", "실제 10종목 (2017~2026)"]):
    ax.axvline(80, color="k", lw=1); ax.axvspan(77, 83, color="gray", alpha=.1)
    for yy in (2.5, 6.5, 10.5, 14.5):
        ax.axhline(yy, color="#999", lw=1, ls=":")
    ax.set_title(t, fontsize=14, loc="left"); ax.set_xlim(70, 92); grid(ax, "x")
    ax.set_xlabel("커버리지 %")
axs[0].set_yticks(range(len(rows)), [lab(*c) if c[0] in TS else f"{NM[c[0]]} {'한 달' if c[1] == 21 else '1년'}" for c in rows], fontsize=12)
for tl, (m, _, _) in zip(axs[0].get_yticklabels(), rows):
    tl.set_color(COL[m])
axs[0].tick_params(axis="y", length=0)
fig.text(0.5, 0.01, "빈 점 = 보정 전, 찬 점 = 보정 후, 회색 띠 = 판정 범위 77~83%", ha="center", fontsize=12, color="#555")
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(OUT + "p16_보정결과.png", facecolor="white"); plt.close()
print("ok")
