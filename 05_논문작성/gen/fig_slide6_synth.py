"""발표 6쪽 예시 그림: 같은 난수(계열 #80)로 만든 L1·군집 L5·꼬리 L5 (번호 없이 굵은 제목·색 구분)."""
import sys, os, importlib.util
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
SRC = '/home/claude/master-thesis/04_실험코드/src_v4'
sys.path.insert(0, SRC)
import config_v4 as C
spec = importlib.util.spec_from_file_location('gen', os.path.join(SRC, '01_generate_synthetic_v4.py'))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
plt.rcParams['font.family'] = 'Noto Sans CJK KR'
S = 80
d = G.base_draws(S)
r1 = C.SIGMA * d['z']
rc, _ = G.gen_cluster(C.LEVELS['cluster_ab']['L5'], d)
rt, _ = G.gen_tail(C.LEVELS['tail_nu']['L5'], d)
w = C.WARMUP; x = np.arange(len(r1) - w)
P = [('특성 없음 (L1)', r1, '#334155'),
     (f"변동성 군집 L5 (α+β = {C.LEVELS['cluster_ab']['L5']:.3f})", rc, '#1B365D'),
     (f"두꺼운 꼬리 L5 (ν = {C.LEVELS['tail_nu']['L5']:.2f})", rt, '#0F766E')]
thr = 3 * C.SIGMA
fig, axs = plt.subplots(3, 1, figsize=(7.6, 4.8), sharex=True)
for ax, (title, r, col) in zip(axs, P):
    rr = r[w:] * 100
    if r is not r1:
        ax.vlines(x, 0, r1[w:] * 100, color='#CBD5E1', lw=0.9)
    ax.vlines(x, 0, rr, color=col, lw=0.9)
    o = np.abs(r[w:]) > thr
    ax.plot(x[o], rr[o], 'o', color='#C0262D', ms=3.5)
    ax.set_title(title, loc='left', fontsize=12, fontweight='bold', color=col, pad=3)
    ax.set_ylim(-11, 11); ax.set_yticks([-10, 0, 10]); ax.tick_params(labelsize=9)
    ax.set_ylabel('%', fontsize=9)
    [ax.spines[s].set_visible(False) for s in ('top', 'right')]
axs[-1].set_xlabel('일', fontsize=10)
fig.text(0.99, 0.005, f'계열 #{S} · 회색: 같은 난수로 만든 L1 · 빨간 점: ±3σ({thr*100:.1f}%) 초과일', ha='right', fontsize=8.5, color='#64748B')
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig('/home/claude/master-thesis/05_논문작성/figs/slide6_합성예시.png', dpi=200)
print('ok', len(x))
