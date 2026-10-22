# 2장(이론적 배경) 설명용 그림. 실험 결과가 아닌 이론 분포와 가상 예시 자료로 그린다.
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, koreanize_matplotlib
from scipy import stats
import pathlib
F = str(pathlib.Path(__file__).resolve().parents[1] / "figs") + "/"
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.unicode_minus": False})
z = stats.norm.ppf(0.9)

# 그림 2-1: 분산이 같은 정규분포와 t분포(ν=5)
nu = 5; s = np.sqrt((nu - 2) / nu)  # 분산 1로 맞춘 t분포의 척도
x = np.linspace(-5, 5, 1000)
fig, axs = plt.subplots(1, 2, figsize=(10, 3.4))
for a, lim in zip(axs, [(-4, 4), (2.5, 5)]):
    a.plot(x, stats.norm.pdf(x), color="#1f77b4", lw=1.5, label="정규분포")
    a.plot(x, stats.t.pdf(x / s, nu) / s, color="#d62728", lw=1.5, label="t분포(ν=5)")
    a.set_xlim(*lim); a.set_xlabel("표준화한 수익률(평균 0, 분산 1)")
axs[0].axvspan(-z, z, color="gray", alpha=0.12, label="정규분포 기준 80% 구간")
axs[0].set_ylabel("확률밀도"); axs[0].legend(fontsize=8, loc="upper left")
axs[0].set_title("전체 모양: t분포는 가운데가 더 높다", fontsize=9)
axs[1].set_ylim(0, 0.025); axs[1].set_title("오른쪽 꼬리 확대: t분포는 극단값이 더 자주 나온다", fontsize=9)
fig.tight_layout(); fig.savefig(F + "fig2_1_정규_t분포.png"); plt.close()

# 그림 2-2: 예측구간과 커버리지(가상 예시, 40일)
rng = np.random.default_rng(3)  # 40일 중 32일 포함(80%)이 되는 예시
n = 40; y = rng.normal(0, 1.0, n)
lo, hi = -z * 1.0, z * 1.0
inside = (y >= lo) & (y <= hi)
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.fill_between([0.5, n + 0.5], lo, hi, color="#1f77b4", alpha=0.15, label="80% 예측구간(q0.1~q0.9)")
ax.scatter(np.arange(1, n + 1)[inside], y[inside], color="#1f77b4", s=14, label="구간 안(포함)")
ax.scatter(np.arange(1, n + 1)[~inside], y[~inside], color="#d62728", s=18, marker="x", label="구간 밖(이탈)")
ax.set_xlim(0.5, n + 0.5); ax.set_xlabel("날짜"); ax.set_ylabel("수익률(%)")
ax.set_title(f"40일 중 {inside.sum()}일 포함 → 커버리지 {inside.mean()*100:.0f}%", fontsize=9)
ax.legend(fontsize=8, ncol=3, loc="lower right")
fig.tight_layout(); fig.savefig(F + "fig2_3_예측구간_커버리지.png"); plt.close()
print("fig2_2 coverage", inside.sum(), n)

# 그림 2-3: 적응형 콘포멀 추론(ACI)의 구간 조정(가상 예시)
rng = np.random.default_rng(3)
T = 200; vol = np.where(np.arange(T) < 100, 1.0, 2.0)  # 100일째에 변동이 두 배가 됨
y = rng.normal(0, vol)
base_hi = z * 1.0  # 모델은 변동 1%를 가정한 구간을 계속 냄
alpha, gamma = 0.2, 0.05
a_t = alpha; A = []; HI = []; err = []
hist = []  # 이탈 점수 기록(폭으로 나눈 값)
for t in range(T):
    w = 2 * base_hi
    if len(hist) >= 20:
        k = int(np.ceil((len(hist) + 1) * (1 - a_t)))
        q = max(hist) if k > len(hist) else np.sort(hist)[k - 1]
    else:
        q = 0.0
    lo_t, hi_t = -base_hi - q * w, base_hi + q * w
    e = int(y[t] < lo_t or y[t] > hi_t)
    hist.append(max(-base_hi - y[t], y[t] - base_hi) / w)
    A.append(a_t); HI.append(hi_t); err.append(e)
    a_t = float(np.clip(a_t + gamma * (alpha - e), 0.02, 0.5))
HI = np.array(HI); err = np.array(err)
fig, axs = plt.subplots(2, 1, figsize=(10, 4.6), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
d = np.arange(T)
axs[0].fill_between(d, -base_hi, base_hi, color="gray", alpha=0.18, label="원래 구간(변동 1% 가정)")
axs[0].plot(d, HI, color="#1f77b4", lw=1.2, label="보정한 구간 상·하단"); axs[0].plot(d, -HI, color="#1f77b4", lw=1.2)
axs[0].scatter(d[err == 1], y[err == 1], color="#d62728", s=10, marker="x", label="보정 구간 이탈")
axs[0].scatter(d[err == 0], y[err == 0], color="#555555", s=4)
axs[0].axvline(100, color="k", lw=0.6, ls=":"); axs[0].text(101, axs[0].get_ylim()[1] * 0.85, "변동이 두 배로 커짐", fontsize=8)
axs[0].set_ylabel("수익률(%)"); axs[0].legend(fontsize=7.5, ncol=3, loc="lower left")
axs[1].plot(d, A, color="#2ca02c", lw=1.2); axs[1].axhline(alpha, color="k", lw=0.6, ls="--")
axs[1].set_ylabel("α_t"); axs[1].set_xlabel("날짜")
fig.tight_layout(); fig.savefig(F + "fig2_4_ACI_조정.png"); plt.close()
print("fig2_3 cov first/second half", 1 - err[20:100].mean(), 1 - err[100:].mean())

# 그림 2-2: TSFM의 입력 방식 개념도(토큰화 방식과 패치 방식)
from matplotlib.patches import FancyBboxPatch
def box(ax, x, y, w, h, txt, fc="#f2f2f2"):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02", fc=fc, ec="#444", lw=0.8))
    ax.text(x, y, txt, ha="center", va="center", fontsize=10.5)
def arrow(ax, x, y1, y2):
    ax.annotate("", xy=(x, y2), xytext=(x, y1), arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#444"))
rng = np.random.default_rng(5); ser = np.cumsum(rng.normal(0, 1, 24)) * 0.3
fig, axs = plt.subplots(1, 2, figsize=(8.2, 6.6))
for a in axs: a.set_xlim(0, 1); a.set_ylim(0, 1); a.axis("off")
# (가) 토큰화
a = axs[0]; a.set_title("(가) 토큰화 방식 (Chronos)", fontsize=11.5)
ins = a.inset_axes([0.2, 0.83, 0.6, 0.12]); ins.plot(ser, color="#1f77b4", lw=1); ins.set_xticks([]); ins.set_yticks([]); ins.set_title("과거 값", fontsize=10)
arrow(a, 0.5, 0.81, 0.75)
box(a, 0.5, 0.70, 0.78, 0.08, "평균 절댓값으로 나누어 크기 조정")
arrow(a, 0.5, 0.655, 0.605)
box(a, 0.5, 0.55, 0.78, 0.10, "값의 범위를 같은 폭의 구간으로 나누고\n각 값을 구간 번호(토큰)로 바꿈")
arrow(a, 0.5, 0.495, 0.445)
box(a, 0.5, 0.39, 0.78, 0.10, "언어 모델(T5)이\n다음 토큰의 확률을 계산", fc="#dbe9f6")
arrow(a, 0.5, 0.335, 0.285)
box(a, 0.5, 0.23, 0.78, 0.10, "토큰을 여러 번 뽑아(표본 추출)\n다시 값으로 되돌림")
arrow(a, 0.5, 0.175, 0.125)
box(a, 0.5, 0.075, 0.78, 0.08, "표본으로 분포·분위수를 구함", fc="#fde2e2")
# (나) 패치
a = axs[1]; a.set_title("(나) 패치 방식 (TimesFM, Moirai)", fontsize=11.5)
ins = a.inset_axes([0.2, 0.83, 0.6, 0.12])
cols = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
for k in range(4): ins.plot(range(k * 6, k * 6 + 7 if k < 3 else 24), ser[k * 6:k * 6 + 7 if k < 3 else 24], color=cols[k], lw=1.2)
for k in range(1, 4): ins.axvline(k * 6, color="#999", lw=0.5, ls=":")
ins.set_xticks([]); ins.set_yticks([]); ins.set_title("과거 값을 일정 길이(패치)로 나눔", fontsize=10)
arrow(a, 0.5, 0.81, 0.75)
box(a, 0.5, 0.70, 0.78, 0.08, "입력 전체를 평균·표준편차로 정규화")
arrow(a, 0.5, 0.655, 0.605)
box(a, 0.5, 0.55, 0.78, 0.10, "패치마다 하나의 벡터로 변환\n(언어 모델의 단어 하나에 해당)")
arrow(a, 0.5, 0.495, 0.445)
box(a, 0.5, 0.39, 0.78, 0.10, "트랜스포머가\n패치 사이의 관계를 학습", fc="#dbe9f6")
arrow(a, 0.5, 0.335, 0.285)
box(a, 0.5, 0.23, 0.78, 0.10, "다음 구간의 분위수(0.1, …, 0.9)를\n한 번에 출력")
arrow(a, 0.5, 0.175, 0.125)
box(a, 0.5, 0.075, 0.78, 0.08, "출력한 분위수가 곧 예측 분포", fc="#fde2e2")
fig.tight_layout(); fig.savefig(F + "fig2_2_입력방식.png"); plt.close()

# (기초 포함 버전 전용) 분위수와 80% 예측구간·VaR
x = np.linspace(-4, 4, 800); pdf = stats.norm.pdf(x)
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot(x, pdf, color="#333", lw=1.4)
ax.fill_between(x, pdf, where=(x >= -z) & (x <= z), color="#1f77b4", alpha=0.18, label="80% 예측구간")
ax.fill_between(x, pdf, where=(x < -z), color="#d62728", alpha=0.35, label="하위 10% (VaR 10%보다 큰 손실)")
for q, nm in [(-z, "0.1 분위수\n= VaR 10%"), (0, "0.5 분위수\n(중앙값)"), (z, "0.9 분위수")]:
    ax.axvline(q, color="#555", lw=0.8, ls="--"); ax.text(q, 0.43, nm, ha="center", fontsize=8)
ax.set_ylim(0, 0.5); ax.set_xlabel("다음 날 수익률(표준화)"); ax.set_ylabel("확률밀도"); ax.legend(fontsize=8, loc="center right")
fig.tight_layout(); fig.savefig(F + "figB_분위수_VaR.png"); plt.close()

# (기초 포함 버전 전용) 분위수 손실
u = np.linspace(-3, 3, 401)
fig, ax = plt.subplots(figsize=(6.5, 3.2))
for tau, c, ls, nm in [(0.1, "#d62728", "-", "0.1 분위수"), (0.5, "#555555", "--", "0.5 분위수(중앙값)"), (0.9, "#1f77b4", "-", "0.9 분위수")]:
    ax.plot(u, u * (tau - (u < 0)), color=c, ls=ls, lw=1.6, label=nm)
ax.axvline(0, color="k", lw=0.5)
ax.text(2.95, 0.45, "실제값이 예측보다 높음", ha="right", fontsize=8); ax.text(-2.95, 0.45, "실제값이 예측보다 낮음", ha="left", fontsize=8)
ax.set_xlabel("실제값 - 예측한 분위수 (y - q)"); ax.set_ylabel("분위수 손실"); ax.set_ylim(-0.05, 2.8); ax.legend(fontsize=8, loc="upper center", frameon=False)
fig.tight_layout(); fig.savefig(F + "figB_분위수손실.png"); plt.close()
