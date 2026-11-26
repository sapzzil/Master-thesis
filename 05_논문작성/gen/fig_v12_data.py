"""발표 v12 데이터 그림 초안 (8·9·10·13·14·16·17쪽). 숫자는 실험 결과 파일에서 직접 읽는다.
사용: python3 fig_v12_data.py   → 05_논문작성/figs/v12/*.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm, t as tdist

plt.rcParams['font.family'] = 'Noto Sans CJK KR'
plt.rcParams['axes.unicode_minus'] = False
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
R = f'{ROOT}/04_실험코드/results_v4_t5fix/tables'
R0 = f'{ROOT}/04_실험코드/results_v4/tables'           # 기본 설정(top-k=50) 실행
E = f'{ROOT}/04_실험코드/results_v4_t5fix_econ'
OUT = f'{ROOT}/05_논문작성/figs/v12'
os.makedirs(OUT, exist_ok=True)

INK, MUTED, GRID = '#1E293B', '#64748B', '#E2E8F0'
BLUE, ORANGE, GRAY = '#2B6CB0', '#D9480F', '#94A3B8'
BAND = '#DCEAF7'
MODEL = {'chronos_t5_base': 'Chronos-T5', 'chronos2': 'Chronos-2', 'timesfm25': 'TimesFM-2.5', 'moirai2': 'Moirai-2',
         'rw': 'RW', 'garch_t': 'GARCH-t'}
TSFM = ['chronos_t5_base', 'chronos2', 'timesfm25', 'moirai2']


def cond_name(m, L, i):
    if m in ('rw', 'garch_t'):
        return f"{MODEL[m]} {'1년' if L == 252 else '한 달'}"
    return f"{MODEL[m]} {'1년' if L == 252 else '한 달'}·{'수익률' if i == 'return' else '가격'}"


def style(ax, grid_axis='x'):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=12, length=0)
    ax.grid(axis=grid_axis, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(f'{OUT}/{name}.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


T1 = pd.read_csv(f'{R}/T1_synth_scenarios.csv')
T1['cond'] = [cond_name(m, L, i) if m != 'oracle' else '오라클' for m, L, i in zip(T1.model, T1.L, T1.input)]
TS = T1[T1.model.isin(TSFM)]

# ---------- 8쪽: 금융 특성 강도와 커버리지 변화 ----------
FEAT = [('CL', '변동성 군집'), ('TL', '두꺼운 꼬리'), ('RF', '국면 전환 빈도'), ('RS', '국면 전환 크기')]
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.axhspan(-2, 2, color=BAND, zorder=0)
ax.axhline(0, color=MUTED, lw=1)
rng = np.random.default_rng(1)
for k, (code, lab) in enumerate(FEAT):
    d = []
    for c, g in TS.groupby('cond'):
        d.append((g[g.scenario == f'{code}_L5']['cov'].values[0] - g[g.scenario == 'L1']['cov'].values[0]) * 100)
    d = np.array(d)
    col = ORANGE if code == 'CL' else BLUE
    ax.scatter(k + rng.uniform(-0.12, 0.12, len(d)), d, s=70, color=col, alpha=0.85, edgecolor='white', lw=1.2, zorder=3)
    ax.text(k, 4.3, f'중앙값 {np.median(d):+.1f}%p', ha='center', fontsize=12, color=INK)
ax.set_xticks(range(4), [l for _, l in FEAT], fontsize=14, color=INK)
ax.set_ylim(-5, 5)
ax.set_ylabel('L5 − L1 커버리지 (%p)', fontsize=13, color=INK)
ax.text(3.45, -1.75, '±2%p', fontsize=11, color=BLUE)
ax.set_xlabel('점 하나 = TSFM 16개 조건 중 하나. 특성을 실측 최대(L5)까지 넣었을 때 특성 없음(L1) 대비 변화', fontsize=11, color=MUTED, labelpad=10)
style(ax, 'y')
save(fig, 'p08_특성강도_변화')

# ---------- 9쪽: 예상과 다른 발견 (이론 계산, 표 4-3) ----------
lv = np.linspace(0.80, 0.99, 200)
z = norm.ppf((1 + lv) / 2)
fig, ax = plt.subplots(figsize=(10, 4.8))
ax.axhline(0, color=MUTED, lw=1.2)
ax.text(80.2, -0.6, '0 = 정규분포 (꼬리 없음, L1)', fontsize=12, color=MUTED)
for nu, lab, col in [(7.64, '꼬리 L3 (ν = 7.64)', GRAY), (3.56, '꼬리 L5 (ν = 3.56)', ORANGE)]:
    cov = 2 * tdist.cdf(z * np.sqrt(nu / (nu - 2)), nu) - 1
    ax.plot(lv * 100, (cov - lv) * 100, color=col, lw=2.5)
    ax.text(86 if nu < 5 else 84, (2 * tdist.cdf(norm.ppf((1 + (0.86 if nu < 5 else 0.84)) / 2) * np.sqrt(nu / (nu - 2)), nu) - 1 - (0.86 if nu < 5 else 0.84)) * 100 + 0.45, lab, fontsize=12.5, color=col if col != GRAY else MUTED, fontweight='bold' if nu < 5 else 'normal', rotation=0)
for p in (0.80, 0.99):
    zz = norm.ppf((1 + p) / 2); c = 2 * tdist.cdf(zz * np.sqrt(3.56 / 1.56), 3.56) - 1
    ax.scatter([p * 100], [(c - p) * 100], s=80, color=ORANGE, edgecolor='white', lw=1.5, zorder=4)
    ax.annotate(f'{p*100:.0f}% 구간 → {c*100:.1f}%', (p * 100, (c - p) * 100), xytext=(14 if p < .9 else -40, -4 if p < .9 else 52),
                textcoords='offset points', fontsize=13, color=INK, ha='left' if p < .9 else 'right', fontweight='bold')
ax.set_xlim(79.5, 99.5); ax.set_ylim(-2.5, 8)
ax.set_xlabel('구간 수준 (명목 커버리지, %)', fontsize=13, color=INK)
ax.set_ylabel('실현 − 명목 커버리지 (%p)', fontsize=13, color=INK)
ax.set_title('분산이 같은 정규분포로 만든 구간을 t분포 데이터에 적용했을 때의 이론 커버리지 (논문 표 4-3)', fontsize=11, color=MUTED, loc='left')
style(ax, 'y')
save(fig, 'p09_꼬리_구간수준')

# ---------- 10쪽: 모델별·입력 조건별 커버리지 차이 (L1) ----------
l1 = TS[TS.scenario == 'L1'].copy()
l1['c'] = l1['cov'] * 100
l1 = l1.sort_values('c')
t0 = pd.read_csv(f'{R0}/T1_synth_scenarios.csv')
dflt = t0[(t0.model == 'chronos_t5_base') & (t0.input == 'return') & (t0.scenario == 'L1')]['cov'] * 100
fig, ax = plt.subplots(figsize=(10.5, 6))
y = np.arange(len(l1))
ax.axvspan(78, 82, color=BAND, zorder=0)
out = (l1.c < 78) | (l1.c > 82)
ax.scatter(l1.c, y, s=90, color=np.where(out, ORANGE, BLUE), edgecolor='white', lw=1.2, zorder=3)
for yy, c in enumerate(l1.c):
    ax.text(c + 0.35, yy, f'{c:.1f}', va='center', fontsize=10.5, color=INK)
ax.set_yticks(y, l1.cond, fontsize=11.5, color=INK)
ax.set_xlim(73, 90)
ax.text(80, len(l1) - 0.2, '적정 78~82%', ha='center', fontsize=11.5, color=BLUE)
ax.text(84.2, 1.2, f'Chronos-T5 수익률 입력을\n라이브러리 기본 설정(top-k = 50)으로 쓰면\n{dflt.min():.1f}~{dflt.max():.1f}% (그래프 범위 밖)', fontsize=11.5, color=ORANGE,
        fontweight='bold', va='center', bbox=dict(boxstyle='round,pad=0.5', fc='white', ec=ORANGE, lw=1.2))
ax.set_xlabel(f'커버리지 (%) — 금융 특성 없는 합성 데이터 L1, TSFM 16개 조건 (적정 범위 밖 {int(out.sum())}개)', fontsize=12.5, color=INK)
style(ax, 'x'); ax.tick_params(axis='y', left=False)
save(fig, 'p10_L1_조건별')

# ---------- 13쪽: 합성 데이터와 실제 주가의 비교 ----------
T6 = pd.read_csv(f'{R}/T6_real_coverage_H5.csv'); T6 = T6[T6.panel == 'ALL']
T6['cond'] = [cond_name(m, L, i) for m, L, i in zip(T6.model, T6.L, T6.input)]
m = T6.merge(T1[T1.scenario == 'L1'][['cond', 'cov']], on='cond', suffixes=('_r', '_s'))
m['x'], m['y'] = m.cov_s * 100, m.cov_r * 100
T60 = pd.read_csv(f'{R0}/T6_real_coverage_H5.csv'); T60 = T60[(T60.panel == 'ALL') & (T60.model == 'chronos_t5_base') & (T60.input == 'return')]
d0 = t0[(t0.model == 'chronos_t5_base') & (t0.input == 'return') & (t0.scenario == 'L1')]
dd = d0.merge(T60, on='L')
fig, (ax, a1) = plt.subplots(1, 2, figsize=(11, 5.6), gridspec_kw={'width_ratios': [3.2, 1], 'wspace': 0.25})
for a, lo, hi in ((ax, 73, 90), (a1, 10, 22)):
    a.plot([lo, hi], [lo, hi], color=MUTED, lw=1, ls='--')
    a.set_xlim(lo, hi); a.set_ylim(lo, hi); a.set_aspect('equal')
    style(a, 'both')
hl = m.cond == 'TimesFM-2.5 1년·가격'
ax.scatter(m.x[~hl], m.y[~hl], s=80, color=BLUE, alpha=0.85, edgecolor='white', lw=1.2, zorder=3)
ax.scatter(m.x[hl], m.y[hl], s=110, color=ORANGE, edgecolor='white', lw=1.2, zorder=4)
r = m[hl].iloc[0]
ax.annotate(f'TimesFM-2.5 1년·가격\n합성 {r.x:.1f}% · 실제 {r.y:.1f}%', (r.x, r.y), xytext=(-150, -10), textcoords='offset points',
            fontsize=11.5, color=INK, arrowprops=dict(arrowstyle='-', color=MUTED))
ax.text(89.5, 74.5, f'19개 모델·조건\n차이 평균 {(m.y - m.x).abs().mean():.1f}%p, 최대 {(m.y - m.x).abs().max():.1f}%p', fontsize=12, color=INK, va='bottom', ha='right')
ax.set_xlabel('합성 L1 커버리지 (%)', fontsize=13, color=INK); ax.set_ylabel('실제 10종목 커버리지 (%)', fontsize=13, color=INK)
a1.scatter(dd['cov_x'] * 100, dd['cov_y'] * 100, s=110, color=ORANGE, marker='D', edgecolor='white', lw=1.2, zorder=4)
a1.set_title('Chronos-T5 기본 설정\n(수익률 입력)', fontsize=11.5, color=ORANGE, fontweight='bold')
for _, q in dd.iterrows():
    a1.annotate(f"{'1년' if q.L == 252 else '한 달'}", (q.cov_x * 100, q.cov_y * 100), xytext=((-24, 6) if q.L == 252 else (8, -14)), textcoords='offset points', fontsize=10, color=INK)
a1.set_xlabel('합성 L1 (%)', fontsize=11, color=INK)
save(fig, 'p13_합성_실제')

# ---------- 14쪽: 기준 모형 대비 분포 정확도 ----------
T7 = pd.read_csv(f'{R}/T7_H6_real.csv')
T7['cond'] = [cond_name(mm, L, i) for mm, L, i in zip(T7.model, T7.L, T7.input)]
T7['v'] = T7.impr_vs_rw * 100
T7 = T7.sort_values('v')
fig, ax = plt.subplots(figsize=(10, 6))
y = np.arange(len(T7))
ax.axvspan(-2, 2, color='#F1F5F9', zorder=0)
ax.axvline(0, color=MUTED, lw=1.2)
COL = {'반대(RW 우위)': ORANGE, '차이 없음': GRAY, '유의하나 작음': BLUE}
for yy, (v, j) in enumerate(zip(T7.v, T7['판정'])):
    ax.plot([0, v], [yy, yy], color=GRID, lw=2, zorder=1)
    ax.scatter(v, yy, s=90, color=COL[j], edgecolor='white', lw=1.2, zorder=3)
ax.set_yticks(y, T7.cond, fontsize=11.5, color=INK)
ax.set_xlim(-11, 4)
ax.set_xlabel('RW 대비 분위수 손실 개선율 (%)   ← RW보다 나쁨 · RW보다 좋음 →', fontsize=12.5, color=INK)
n_bad = (T7['판정'] == '반대(RW 우위)').sum()
for lab, c, yy in [(f'RW보다 손실이 유의하게 큼 ({n_bad}개)', ORANGE, 2), ('차이 없음 (3개)', GRAY, 1), ('유의하게 작으나 2% 미만 (1개)', BLUE, 0)]:
    ax.scatter(-10.6, yy + 12.5, s=60, color=c); ax.text(-10.3, yy + 12.5, lab, va='center', fontsize=11, color=INK)
ax.text(1.0, len(T7) - 0.4, '실질 기준 ±2%', fontsize=10.5, color=MUTED, ha='center')
style(ax, 'x'); ax.tick_params(axis='y', left=False)
save(fig, 'p14_RW대비_정확도')

# ---------- 16쪽: 보정 후 커버리지와 구간 폭 ----------
T6s = T6.sort_values('cov')
T4 = pd.read_csv(f'{R}/T4_H5_synth.csv')
o = T4[T4.model == 'oracle'][['scenario', 'width']].rename(columns={'width': 'ow'})
w = T4[T4.model.isin(TSFM)].merge(o, on='scenario'); w['r'] = w.cal_width / w.ow
w['cond'] = [cond_name(mm, L, i) for mm, L, i in zip(w.model, w.L, w.input)]
wr = w.groupby('cond').r.agg(['min', 'max', 'mean']).sort_values('mean')
fig, (ax, a2) = plt.subplots(1, 2, figsize=(13, 6.2), gridspec_kw={'width_ratios': [1.15, 1], 'wspace': 0.75})
y = np.arange(len(T6s))
ax.axvspan(78, 82, color=BAND, zorder=0)
for yy, (b, a) in enumerate(zip(T6s['cov'] * 100, T6s['cal'] * 100)):
    ax.annotate('', xy=(a, yy), xytext=(b, yy), arrowprops=dict(arrowstyle='-|>', color=MUTED, lw=1.4, mutation_scale=12))
    ax.scatter(b, yy, s=55, color=GRAY, zorder=3); ax.scatter(a, yy, s=70, color=BLUE, edgecolor='white', lw=1, zorder=4)
ax.set_yticks(y, T6s.cond, fontsize=10.5, color=INK)
ax.set_xlim(74, 90)
ax.set_title('실제 10종목: 보정 전(회색) → 보정 후(파랑)', fontsize=13, color=INK, loc='left')
ax.set_xlabel('커버리지 (%)', fontsize=12, color=INK)
style(ax, 'x'); ax.tick_params(axis='y', left=False)
y2 = np.arange(len(wr))
a2.hlines(y2, (wr['min'] - 1) * 100, (wr['max'] - 1) * 100, color=BLUE, lw=5, alpha=0.35)
a2.scatter((wr['mean'] - 1) * 100, y2, s=55, color=BLUE, zorder=3)
a2.set_yticks(y2, wr.index, fontsize=10.5, color=INK)
a2.set_xlim(0, 52)
a2.set_title('합성 데이터: 오라클 대비 구간 폭 증가', fontsize=13, color=INK, loc='left')
a2.set_xlabel(f'오라클보다 넓은 정도 (%) — 막대 = 17개 시나리오 범위, 점 = 평균\n전체 {(w.r.min()-1)*100:.0f}~{(w.r.max()-1)*100:.0f}%', fontsize=11.5, color=INK)
style(a2, 'x'); a2.tick_params(axis='y', left=False)
save(fig, 'p16_보정결과_폭')

# ---------- 17쪽: VaR 백테스트 ----------
e3 = pd.read_csv(f'{E}/E3_var.csv'); e3.columns = ['c', 'k', 'v', 'kp', 'ind', 'p']
n0 = (e3[e3.k == '원래'].kp >= 8).sum(); n1 = (e3[e3.k == '보정'].kp >= 8).sum(); N = (e3.k == '원래').sum()
fig, ax = plt.subplots(figsize=(7, 4.6))
bars = ax.bar(['보정 전', '보정 후'], [n0, n1], color=[GRAY, BLUE], width=0.5)
for b, n in zip(bars, [n0, n1]):
    ax.text(b.get_x() + b.get_width() / 2, n + 0.3, f'{n}개', ha='center', fontsize=18, color=INK, fontweight='bold')
ax.axhline(N, color=MUTED, lw=1, ls='--'); ax.text(1.32, N, f'전체 {N}개', va='center', fontsize=11, color=MUTED)
ax.set_ylim(0, N + 2)
ax.set_yticks(range(0, N + 1, 5))
ax.set_title('VaR 10% 위반율 검정 통과 조건 수 (10종목 중 8종목 이상 통과, 19개 중)', fontsize=12, color=INK, loc='left')
ax.tick_params(axis='x', labelsize=14, colors=INK)
style(ax, 'y')
save(fig, 'p17_VaR')
print('saved to', OUT, sorted(os.listdir(OUT)))
