"""발표 3쪽 그림: 같은 실제 분포에서 80% 예측구간 폭이 다를 때 커버리지·VaR 위반율."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.stats import norm
plt.rcParams['font.family'] = 'Noto Sans CJK KR'
NAVY, RED, GREEN, GRAY = '#1B365D', '#C0262D', '#15803D', '#64748B'
cases = [('① 적정', 1.2816, GREEN), ('② 절반 폭', 0.6408, RED), ('③ 2배 폭', 2.5631, NAVY)]
x = np.linspace(-3.6, 3.6, 800); y = norm.pdf(x)
fig, axs = plt.subplots(1, 3, figsize=(7.5, 3.3), sharey=True)
for ax, (name, k, c) in zip(axs, cases):
    cov = norm.cdf(k) - norm.cdf(-k); vio = norm.cdf(-k)
    ax.plot(x, y, color=GRAY, lw=1.6)
    m = (x >= -k) & (x <= k); ax.fill_between(x[m], y[m], color=NAVY, alpha=0.18)
    t = x <= -k; ax.fill_between(x[t], y[t], color=RED, alpha=0.75)
    ax.vlines(-k, 0, 0.40, color=RED, lw=1.3, ls='--'); ax.vlines(k, 0, 0.40, color=NAVY, lw=1.0, ls=':')
    ax.set_title(f'{name}', color=c, fontsize=16, fontweight='bold')
    ax.text(0, 0.50, f'커버리지\n{cov*100:.0f}%', ha='center', va='center', fontsize=15, color=NAVY, fontweight='bold')
    ax.annotate(f'위반\n{vio*100:.1f}%' if vio < 0.01 else f'위반\n{vio*100:.0f}%',
                xy=(-k - 0.25, norm.pdf(k) * 0.35), xytext=((-2.3 if k > 2 else -3.6), 0.30), fontsize=14, color=RED, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1))
    ax.set_xticks([-k]); ax.set_xticklabels(['VaR 10%']); ax.tick_params(axis='x', labelsize=13, colors=GRAY)
    ax.set_yticks([]); [ax.spines[s].set_visible(False) for s in ('top', 'right', 'left')]
    ax.set_ylim(0, 0.58)
fig.tight_layout()
fig.savefig('/home/claude/master-thesis/05_논문작성/figs/slide3_예측구간_VaR.png', dpi=200)
