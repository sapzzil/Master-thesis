# 원고 v4 2단계에서 새로 정한 그림(데이터 그림 3개 + 도식 3개). 기존 figs.py·figs_theory.py는 건드리지 않음.
# 사용: python3 figs_v4_new.py <real_cal_width.csv 경로>
#   real_cal_width.csv = PC의 scored_v4.parquet(실제 데이터, 채점일)에서 모델·조건별 보정 전후 평균 폭을 계산한 파일
import sys, pathlib, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, koreanize_matplotlib  # noqa: F401
from matplotlib.patches import FancyBboxPatch
from scipy import stats

_R = pathlib.Path(__file__).resolve().parents[2]
T = str(_R / "04_실험코드/results_v4_t5fix/tables") + "/"
P = str(_R / "04_실험코드/results_v4_post") + "/"
F = str(_R / "05_논문작성/figs/v4") + "/"
pathlib.Path(F).mkdir(parents=True, exist_ok=True)
REAL_W = sys.argv[1]
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.unicode_minus": False})
NM = {"chronos_t5_base": "Chronos-T5", "chronos2": "Chronos-2", "timesfm25": "TimesFM-2.5", "moirai2": "Moirai-2", "rw": "과거변동(RW)", "garch_t": "GARCH-t"}
COL = {"chronos_t5_base": "#7f7f7f", "chronos2": "#1f77b4", "timesfm25": "#d62728", "moirai2": "#2ca02c", "rw": "k", "garch_t": "#9467bd"}
TS = ["chronos_t5_base", "chronos2", "timesfm25", "moirai2"]
CONDS = [(21, "return"), (21, "price"), (252, "return"), (252, "price")]
CO = [(m, L, k) for m in TS for L, k in CONDS] + [("rw", 21, "return"), ("rw", 252, "return"), ("garch_t", 252, "return")]


def lab(m, L, k):
    if m in ("rw", "garch_t"):
        return f"{NM[m]} {'한 달' if L == 21 else '1년'}"
    return f"{NM[m]} {'한 달' if L == 21 else '1년'}·{'수익률' if k == 'return' else '가격'}"


def sel(d, m, L, k):
    return d[(d.model == m) & (d.L == L) & (d.input == k)]


t1 = pd.read_csv(T + "T1_synth_scenarios.csv")
t7 = pd.read_csv(T + "T7_H6_real.csv")
b4 = pd.read_csv(P + "b4_vs_garch.csv")
rw = pd.read_csv(REAL_W)

# ---------- [새] 4장: 커버리지 차이의 분산 분해 ----------
d = t1[t1.model.isin(TS)].copy(); d["c"] = d.model + d.L.astype(str) + d.input


def dec(dd):
    M = dd.pivot(index="c", columns="scenario", values="cov").values; g = M.mean(); tot = ((M - g) ** 2).sum()
    r = M.shape[1] * ((M.mean(1) - g) ** 2).sum() / tot; c = M.shape[0] * ((M.mean(0) - g) ** 2).sum() / tot
    return [r * 100, c * 100, (1 - r - c) * 100]


rows = [("TSFM 16개 조건 전체", dec(d)), ("TimesFM-2.5 1년·가격 제외 (15개)", dec(d[d.c != "timesfm25252price"]))]
fig, ax = plt.subplots(figsize=(7.5, 2.4))
cols = ["#4d4d4d", "#d9d9d9", "#f2f2f2"]; names = ["모델·입력 조건", "금융 특성(시나리오)", "나머지"]
for i, (lb, v) in enumerate(rows[::-1]):
    left = 0
    for j, (x, c) in enumerate(zip(v, cols)):
        ax.barh(i, x, left=left, color=c, height=.55, edgecolor="#666", lw=.6)
        if x > 4:
            ax.text(left + x / 2, i, f"{x:.0f}%", ha="center", va="center", fontsize=10, color="white" if j == 0 else "#222")
        left += x
ax.set_yticks([0, 1], [r[0] for r in rows[::-1]]); ax.set_xlim(0, 100); ax.set_xlabel("커버리지 변동 중 차지하는 비율 (%)")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=c, ec="#666", lw=.6) for c in cols], labels=names, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False)
fig.tight_layout(); fig.savefig(F + "fig4_x_분산분해.png"); plt.close()
print("분산 분해", [[round(x, 1) for x in r[1]] for r in rows])

# ---------- 그림 5-2 개정: RW 대비 + GARCH-t 대비 ----------
rows = CO[:16][::-1]
fig, axs = plt.subplots(1, 2, figsize=(9.5, 5.4), sharey=True, gridspec_kw={"width_ratios": [1.25, 1]})
for i, (m, L, k) in enumerate(rows):
    r = sel(t7, m, L, k).iloc[0]; v = 100 * r.impr_vs_rw
    axs[0].barh(i, v, color=COL[m], alpha=.85 if r.p_holm < .05 else .35)
    axs[0].text(v - 0.3 if v < 0 else v + 0.3, i, f"{v:+.1f}", va="center", ha="right" if v < 0 else "left", fontsize=7)
    g = sel(b4, m, L, k)
    if len(g):
        v2 = 100 * g.iloc[0].impr_vs_garch
        axs[1].barh(i, v2, color=COL[m], alpha=.85 if g.iloc[0].p_holm < .05 else .35)
        axs[1].text(v2 - 0.2, i, f"{v2:+.1f}", va="center", ha="right", fontsize=7)
    else:
        axs[1].text(-0.15, i, "해당 없음 (과거 한 달)", va="center", ha="right", fontsize=7, color="#999")
for ax, xl, t in [(axs[0], (-12, 4), "(가) 과거변동(RW, 같은 과거 길이) 대비"), (axs[1], (-7, 1.5), "(나) GARCH-t(과거 1년) 대비")]:
    ax.axvline(0, color="k", lw=1); ax.axvspan(-2, 2, color="gray", alpha=.1); ax.set_xlim(*xl); ax.set_title(t, fontsize=9.5, loc="left")
    for yy in (3.5, 7.5, 11.5): ax.axhline(yy, color="#999", lw=.6, ls=":")
axs[0].set_yticks(range(16), [lab(*c) for c in rows], fontsize=7.5)
fig.supxlabel("분위수 손실 개선 % = 1 − TSFM 손실 ÷ 기준 모형 손실 (오른쪽 = TSFM이 나음)\n진한 막대 = Holm 보정 유의, 옅은 막대 = 유의하지 않음, 회색 띠 = 실질 기준 ±2%", fontsize=8.5)
fig.tight_layout(); fig.savefig(F + "fig5_2_기준모형_대비_손실.png"); plt.close()

# ---------- [새] 6장: 보정 후 구간 폭 ----------
o = t1[t1.model == "oracle"].set_index("scenario")["width"]
BAD = {("garch_t", "RS_L3"), ("garch_t", "TL_L2")}            # GARCH-t 추정 실패 계열이 들어간 시나리오(6.5절·표 6-3)
rows = CO[::-1]
fig, axs = plt.subplots(1, 2, figsize=(10, 6.2), sharey=True)
for i, (m, L, k) in enumerate(rows):
    g = sel(t1, m, L, k); g = g[[(m, s) not in BAD for s in g.scenario]]
    r = (g.cal_width.values / o.loc[g.scenario].values)
    axs[0].plot([r.min(), r.max()], [i, i], color=COL[m], lw=6, alpha=.35, solid_capstyle="butt")
    l1 = g[g.scenario == "L1"]
    if len(l1): axs[0].plot(l1.cal_width.iloc[0] / o.loc["L1"], i, "o", color=COL[m], ms=5)
    rr = sel(rw, m, L, k).iloc[0]
    axs[1].plot(rr.w * 100, i, "o", mfc="white", mec=COL[m], ms=5, mew=1.2)
    axs[1].plot(rr.cw * 100, i, "o", color=COL[m], ms=5)
    axs[1].annotate("", xy=(rr.cw * 100, i), xytext=(rr.w * 100, i), arrowprops=dict(arrowstyle="->", color=COL[m], lw=1))
axs[0].axvline(1, color="k", lw=1); axs[0].set_xlabel("보정 후 평균 폭 ÷ 오라클 폭 (1 = 정답 구간과 같음)")
axs[0].set_title("(가) 합성 17개 시나리오\n막대 = 시나리오 범위, 점 = L1(특성 없음)", fontsize=9, loc="left")
for nm, ls in [("rw", "--"), ("garch_t", ":")]:
    v = rw[(rw.model == nm) & (rw.L == 252)].cw.iloc[0] * 100
    axs[1].axvline(v, color=COL[nm], lw=1, ls=ls, label=f"{NM[nm]} 1년 보정 후 ({v:.2f})")
axs[1].set_xlabel("평균 폭 (%p, 일별 로그수익률)"); axs[1].legend(fontsize=7.5, loc="lower right")
axs[1].set_title("(나) 실제 10종목 (2017~2026)\n빈 점 = 보정 전, 찬 점 = 보정 후 (보정 후 커버리지 모두 약 80%)", fontsize=9, loc="left")
for ax in axs:
    for yy in (2.5, 6.5, 10.5, 14.5): ax.axhline(yy, color="#999", lw=.6, ls=":")
axs[0].set_yticks(range(len(rows)), [lab(*c) for c in rows], fontsize=7.5)
fig.text(0.01, 0.005, "GARCH-t는 추정이 실패한 계열이 들어간 두 시나리오(전환 크기 L3, 꼬리 L2)를 빼고 그렸음.", fontsize=7.5, color="#555")
fig.tight_layout(rect=(0, .02, 1, 1)); fig.savefig(F + "fig6_x_보정후_폭.png"); plt.close()


# ---------- 도식 공통 ----------
def box(ax, x, y, w, h, txt, fc="#f2f2f2", fs=8.5, ec="#444"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01", fc=fc, ec=ec, lw=0.8))
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, linespacing=1.4)


def arr(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#444"))


# ---------- 그림 2-2 개정: 입력 → 분위수 → 예측구간 ----------
rng = np.random.default_rng(5); ser = np.cumsum(rng.normal(0, 1, 24)) * 0.3
fig = plt.figure(figsize=(8.2, 8.6))
gs = fig.add_gridspec(2, 2, height_ratios=[3.1, 1.25])
for j, (title, steps, last) in enumerate([
        ("(가) 토큰화 방식 (Chronos-T5)", ["평균 절댓값으로 나누어 크기 조정", "값의 범위를 같은 폭의 구간으로 나누고\n각 값을 구간 번호(토큰)로 바꿈",
                                     "언어 모델(T5)이\n다음 토큰의 확률을 계산", "토큰을 여러 번 뽑아(표본 추출)\n다시 값으로 되돌림"], "표본을 정렬해 분위수를 구함"),
        ("(나) 패치 방식 (Chronos-2, TimesFM, Moirai)", ["입력의 크기를 정규화(방식은 모델마다 다름)", "패치마다 하나의 벡터로 변환\n(언어 모델의 단어 하나에 해당)",
                                                  "트랜스포머가\n패치 사이의 관계를 학습", "다음 시점의 여러 분위수를\n한 번에 출력"], "출력한 분위수가 곧 예측 분포")]):
    a = fig.add_subplot(gs[0, j]); a.set_xlim(0, 1); a.set_ylim(0, 1); a.axis("off"); a.set_title(title, fontsize=10)
    ins = a.inset_axes([0.2, 0.86, 0.6, 0.11])
    if j == 0:
        ins.plot(ser, color="#1f77b4", lw=1); ins.set_title("과거 값", fontsize=8.5)
    else:
        cc = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
        for q in range(4): ins.plot(range(q * 6, min(q * 6 + 7, 24)), ser[q * 6:min(q * 6 + 7, 24)], color=cc[q], lw=1.2)
        for q in range(1, 4): ins.axvline(q * 6, color="#999", lw=.5, ls=":")
        ins.set_title("과거 값을 일정 길이(패치)로 나눔", fontsize=8.5)
    ins.set_xticks([]); ins.set_yticks([])
    ys = [0.73, 0.57, 0.41, 0.25]
    arr(a, .5, .84, .5, .78)
    for n, (y, s) in enumerate(zip(ys, steps)):
        box(a, .5, y, .8, .1, s, fc="#dbe9f6" if n == 2 else "#f2f2f2")
        arr(a, .5, y - .05, .5, y - .11 + .005)
    box(a, .5, .09, .8, .09, last, fc="#fde2e2")
# 아래: 공통 출력
a = fig.add_subplot(gs[1, :])
past = ser[-12:] * 0.9
a.plot(range(12), past, color="#444", lw=1.2)
qs = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]); sd = 1.0
qv = past[-1] + stats.norm.ppf(qs) * sd
a.fill_between([12.6, 13.4], qv[0], qv[-1], color="#fde2e2", ec="#d62728", lw=.8)
for q, v in zip(qs, qv):
    a.plot([12.6, 13.4], [v, v], color="#d62728" if q in (0.1, 0.5, 0.9) else "#e8a0a0", lw=1.6 if q == 0.5 else .9)
a.text(13.6, qv[-1], "0.9 분위수", va="center", fontsize=8); a.text(13.6, qv[4], "0.5 분위수 = 점 예측", va="center", fontsize=8)
a.text(13.6, qv[0], "0.1 분위수", va="center", fontsize=8)
a.annotate("", xy=(17.3, qv[0]), xytext=(17.3, qv[-1]), arrowprops=dict(arrowstyle="<->", color="#d62728", lw=1))
a.text(17.5, (qv[0] + qv[-1]) / 2, "80% 예측구간\n(실제값이 이 안에 들어올\n확률이 80%라는 뜻)", va="center", fontsize=8, color="#d62728")
a.set_xlim(-0.5, 22); a.axis("off")
a.set_title("(다) 공통 출력: 다음 날 값에 대한 분위수 9개 → 80% 예측구간", fontsize=10, loc="left")
a.text(6, min(past) - 0.9, "과거 값", ha="center", fontsize=8, color="#444"); a.text(13, min(qv) - 0.9, "다음 날", ha="center", fontsize=8, color="#444")
fig.tight_layout(); fig.savefig(F + "fig2_2_입력과_출력.png"); plt.close()

# ---------- [새] 3장: 실험 설계 흐름도 ----------
fig, a = plt.subplots(figsize=(9.5, 5.6)); a.set_xlim(0, 1); a.set_ylim(0, 1); a.axis("off")
box(a, .17, .86, .3, .1, "① 실제 10종목(미국 5, 한국 5)에서\n금융 특성의 강도를 측정")
box(a, .17, .66, .3, .12, "② 특성별 강도 단계 L1~L5\n(L1 = 특성 없음, L3~L5 = 실측 범위)")
box(a, .17, .44, .3, .16, "③ 합성 데이터 생성\n특성 하나씩 × 단계 = 17개 시나리오\n시나리오마다 100개 계열\n(공통 난수, 하루 변동 2.11% 고정)", fc="#dbe9f6")
box(a, .5, .66, .26, .2, "④ 같은 방식으로 예측\nTSFM 4종 × 입력 조건 4개\n(과거 한 달·1년 × 수익률·가격)\n+ 기준 모형 RW·GARCH-t\n→ 다음 날 80% 예측구간", fc="#fff2cc")
box(a, .83, .86, .3, .1, "실제 10종목 2017~2026\n(평가 17,700건)", fc="#dbe9f6")
box(a, .5, .3, .26, .12, "⑤ 평가\n커버리지(캘리브레이션 오차)\n분위수 손실, 구간 폭")
box(a, .83, .5, .3, .14, "⑥ 사후보정\n적응형 콘포멀 예측(ACI-CQR)\n모델 재학습 없이 구간만 조정", fc="#fde2e2")
box(a, .83, .25, .3, .1, "⑦ 보정 후 다시 평가\n커버리지 복원, 구간 폭")
arr(a, .17, .81, .17, .72); arr(a, .17, .6, .17, .52)
arr(a, .32, .44, .37, .6); arr(a, .68, .86, .63, .74)
arr(a, .5, .56, .5, .36); arr(a, .63, .3, .68, .45); arr(a, .83, .43, .83, .3)
for x, y, t in [(.02, .3, "RQ1 진단: 합성 데이터에서 특성이 오차를 만드는가"), (.02, .22, "RQ2 실증: 실제 주식에서도 같은가"), (.02, .14, "RQ3 보정: 재학습 없이 고칠 수 있는가, 대가는 무엇인가")]:
    a.text(x, y, t, fontsize=8.5, color="#333")
fig.tight_layout(); fig.savefig(F + "fig3_x_실험설계_흐름도.png"); plt.close()

# ---------- [새] 7장: 실무 적용 절차 ----------
fig, a = plt.subplots(figsize=(9.5, 2.6)); a.set_xlim(0, 1); a.set_ylim(0, 1); a.axis("off")
steps = [("1. 점검", "특성 없는 합성 데이터(L1)로\n모델·입력 조건별 커버리지 확인\n→ 크게 벗어나는 설정 제외"),
         ("2. 보정", "적응형 콘포멀 예측으로\n구간 조정(모델 재학습 없음)\n→ 평균 커버리지 80%"),
         ("3. 선택", "보정 후 구간 폭을 비교해\n가장 좁은 조건을 고름\n(기준 모형과도 비교)"),
         ("4. 사용·감시", "구간 하단을 위험 한도(VaR)로 사용\n변동성이 큰 시기의\n위반 몰림을 따로 확인")]
xs = [.12, .37, .62, .87]
for x, (h, s) in zip(xs, steps):
    box(a, x, .45, .22, .62, "", fc="#f7f7f7")
    a.text(x, .67, h, ha="center", fontsize=10, fontweight="bold"); a.text(x, .38, s, ha="center", va="center", fontsize=8, linespacing=1.45)
for x1, x2 in zip(xs[:-1], xs[1:]): arr(a, x1 + .115, .45, x2 - .115, .45)
fig.tight_layout(); fig.savefig(F + "fig7_x_실무절차.png"); plt.close()
print("done")
