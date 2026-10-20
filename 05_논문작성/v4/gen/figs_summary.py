import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, koreanize_matplotlib
from matplotlib.patches import FancyBboxPatch
import pathlib; _R=pathlib.Path(__file__).resolve().parents[3]
T=str(_R/"04_실험코드/results_v4_t5fix/tables")+"/"
F=str(_R/"05_논문작성/v4/figs")+"/"
plt.rcParams.update({"figure.dpi":150,"font.size":9})
# S1 design
fig,ax=plt.subplots(figsize=(10,4.2)); ax.set_xlim(0,100); ax.set_ylim(0,42); ax.axis("off")
def box(x,y,w,h,t,fc):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.4,rounding_size=1.2",fc=fc,ec="#444",lw=0.8))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=8.6,linespacing=1.35)
def arr(x0,y0,x1,y1): ax.annotate("",xy=(x1,y1),xytext=(x0,y0),arrowprops=dict(arrowstyle="-|>",color="#444",lw=1))
box(1,27,19,11,"실제 10종목에서\n특성 강도 측정\n(군집·꼬리·국면 빈도·크기)","#eef3fb")
box(26,27,21,11,"① 합성 데이터 실험\n17개 시나리오 × 100계열\n(특성 하나씩만 L1~L5)","#eef3fb")
box(26,4,21,11,"② 실제 주가 실증\n미국 5 + 한국 5종목\n2017.01~2026.09 (24,132건)","#fdf3e7")
box(53,15,21,12,"같은 예측 절차\nTSFM 4종 × 4조건\n(과거 21/252일 × 수익률/가격)\n+ RW, GARCH-t\n내일 수익률 80% 구간","#f2f2f2")
box(80,30,19,8,"RQ1 진단\n오차는 어디서 오는가","#e8f4ea")
box(80,17,19,8,"RQ2 평가\n실제 주식에서 쓸 만한가","#e8f4ea")
box(80,4,19,8,"RQ3 처방\nACI-CQR 사후보정","#e8f4ea")
arr(20.8,32.5,25.2,32.5); arr(47.8,32,52.6,24); arr(47.8,9.5,52.6,18)
arr(74.8,23,79.2,33); arr(74.8,21,79.2,21); arr(74.8,19,79.2,8.5)
ax.text(50,41,"모든 설정·가설·코드는 실행 전에 동결(사전등록)",ha="center",fontsize=8.5,color="#555")
fig.tight_layout(); fig.savefig(F+"figS1_연구설계.png"); plt.close()
# S3 synthetic L1 vs real
t1=pd.read_csv(T+"T1_synth_scenarios.csv"); t6=pd.read_csv(T+"T6_real_coverage_H5.csv")
a=t1[t1.scenario=="L1"].set_index(["model","L","input"])["cov"]; b=t6[t6.panel=="ALL"].set_index(["model","L","input"])["cov"]
j=pd.concat([a,b],axis=1,keys=["s","r"]).dropna()*100
COL={"chronos_t5_base":"#7f7f7f","chronos2":"#1f77b4","timesfm25":"#d62728","moirai2":"#2ca02c","rw":"k","garch_t":"#9467bd"}
NM={"chronos_t5_base":"Chronos-T5","chronos2":"Chronos-2","timesfm25":"TimesFM-2.5","moirai2":"Moirai-2","rw":"과거변동(RW)","garch_t":"GARCH-t"}
fig,ax=plt.subplots(figsize=(6.4,5.2)); lim=(73,90)
ax.plot(lim,lim,color="gray",lw=1,ls="--"); ax.axvspan(78,82,color="gray",alpha=.08); ax.axhspan(78,82,color="gray",alpha=.08)
for (m,L,k),r in j.iterrows():
    ax.scatter(r.s,r.r,color=COL[m],marker="o" if k=="price" else "^",s=40,edgecolor="white",lw=.5)
ax.set_xlim(*lim); ax.set_ylim(*lim); ax.set_xlabel("합성 L1(특성 없음) 커버리지 %"); ax.set_ylabel("실제 10종목 커버리지 %"); ax.grid(alpha=.3)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([],[],color=c,marker="s",ls="",label=NM[m]) for m,c in COL.items()],fontsize=7.5,loc="upper left")
ax.text(89.5,73.6,"● 가격 입력  ▲ 수익률 입력\n점선 = 합성과 실제가 같음, 음영 = 80% ± 2%p",ha="right",va="bottom",fontsize=7.5,color="#555",linespacing=1.6)
md=(j.r-j.s).abs().mean()
fig.suptitle(f"특성이 하나도 없는 합성 데이터의 커버리지가 실제 주가 커버리지를 거의 그대로 예측한다 (19개 평균 차이 {md:.1f}%p)",fontsize=8.5)
fig.tight_layout(); fig.savefig(F+"figS3_합성L1_vs_실제.png")
# 본문(그림 5-3)용: 그림 안 제목 없이 같은 그림을 저장(설명은 그림 제목으로)
fig._suptitle.set_visible(False); fig.tight_layout(); fig.savefig(F+"fig5_3_합성L1_vs_실제.png"); plt.close(); print("ok")
