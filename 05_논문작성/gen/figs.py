# 그림 생성 스크립트(작성 당시 클라우드 경로 기준). 경제 분석 그림(fig5_3)은 econ_v4.py가 만든 E1_curves.pkl·E2_ports.pkl이 필요하다.
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, koreanize_matplotlib
from scipy import stats
import pathlib; _R=pathlib.Path(__file__).resolve().parents[2]
T=str(_R/"04_실험코드/results_v4_t5fix/tables")+"/"   # 95차: 본문 기준 결과
S="/tmp/claude-0/-home-claude/fa74dbd6-df2f-598d-89dd-28a1a0c58d47/scratchpad/"
F=str(_R/"05_논문작성/figs")+"/"
NM={"chronos_t5_base":"Chronos-T5","chronos2":"Chronos-2","timesfm25":"TimesFM-2.5","moirai2":"Moirai-2","rw":"과거변동(RW)","garch_t":"GARCH-t","oracle":"오라클 모형"}
COL={"chronos_t5_base":"#7f7f7f","chronos2":"#1f77b4","timesfm25":"#d62728","moirai2":"#2ca02c"}
ORD=["chronos_t5_base","chronos2","timesfm25","moirai2","rw","garch_t","oracle"]
CO=[(m,L,k) for m in ORD[:4] for L,k in [(21,"return"),(21,"price"),(252,"return"),(252,"price")]]+[("rw",21,"return"),("rw",252,"return"),("garch_t",252,"return"),("oracle",0,"-")]
def lab(m,L,k): return "오라클 모형" if m=="oracle" else f"{NM[m]} {'한 달' if L==21 else '1년'}·{'수익률' if k=='return' else '가격'}"
plt.rcParams.update({"figure.dpi":150,"font.size":9})
t1=pd.read_csv(T+"T1_synth_scenarios.csv")
SC=["L1"]+[f"{a}_L{i}" for a in ["CL","TL","RF","RS"] for i in range(2,6)]
AX={"CL":"군집","TL":"꼬리","RF":"전환빈도","RS":"전환크기"}
def scl(s): return "L1 (특성 없음)" if s=="L1" else f"{AX[s[:2]]} {s[3:]}"
# Fig 4-1 heatmap
M=np.array([[t1[(t1.model==m)&(t1.L==L)&(t1.input==k)&(t1.scenario==s)]["cov"].iloc[0]*100 for (m,L,k) in CO] for s in SC])
fig,ax=plt.subplots(figsize=(11,6.2))
im=ax.imshow(M,cmap="RdBu",vmin=70,vmax=90,aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v=M[i,j]; ax.text(j,i,f"{v:.0f}" if v<30 else f"{v:.1f}",ha="center",va="center",fontsize=6.3,color="white" if abs(v-80)>7 else "black")
ax.set_xticks(range(len(CO))); ax.set_xticklabels([lab(*c) for c in CO],rotation=60,ha="right",fontsize=7)
ax.set_yticks(range(len(SC))); ax.set_yticklabels([scl(s) for s in SC],fontsize=7.5)
for y in [0.5,4.5,8.5,12.5]: ax.axhline(y,color="k",lw=0.6)
for x in [3.5,7.5,11.5,15.5]: ax.axvline(x,color="k",lw=0.6)
cb=fig.colorbar(im,ax=ax,shrink=0.8); cb.set_label("커버리지 % (목표 80, 파랑=넓음·빨강=좁음)")
fig.tight_layout(); fig.savefig(F+"fig4_1_합성커버리지_히트맵.png"); plt.close()
# Fig 4-2 dose-response delta vs L1
fig,axs=plt.subplots(1,4,figsize=(12,3.8),sharey=True)
z=stats.norm.ppf(.9)
for a,(code,name) in zip(axs,AX.items()):
    xs=[1,2,3,4,5]
    for (m,L,k) in CO[:16]:
        g=t1[(t1.model==m)&(t1.L==L)&(t1.input==k)].set_index("scenario")["cov"]
        y=[0]+[100*(g[f"{code}_L{i}"]-g["L1"]) for i in range(2,6)]
        a.plot(xs,y,color=COL[m],lw=1,alpha=.75,ls="-" if k=="price" else "--")
    g=t1[(t1.model=="rw")&(t1.L==252)].set_index("scenario")["cov"]
    a.plot(xs,[0]+[100*(g[f"{code}_L{i}"]-g["L1"]) for i in range(2,6)],color="k",lw=2,label="과거변동(RW) 1년")
    if code=="TL":
        th=[0]+[100*(2*stats.t.cdf(z*np.sqrt(nu/(nu-2)),nu)-1)-80 for nu in [11.28,7.64,4.39,3.56]]
        a.plot(xs,th,color="orange",lw=2,ls=":",label="이론: 정규 구간을 t분포에 적용")
    a.axhline(0,color="gray",lw=.6); a.axhspan(-2,2,color="gray",alpha=.1)
    a.set_title(name); a.set_xticks(xs); a.set_xticklabels(["L1","L2","L3","L4","L5"])
axs[0].set_ylabel("L1 대비 커버리지 변화 (%p)")
from matplotlib.lines import Line2D
h=[Line2D([],[],color=c,label=NM[m]) for m,c in COL.items()]+[Line2D([],[],color="gray",ls="-",label="가격 입력"),Line2D([],[],color="gray",ls="--",label="수익률 입력"),Line2D([],[],color="k",lw=2,label="과거변동(RW) 1년"),Line2D([],[],color="orange",ls=":",lw=2,label="이론(꼬리 축)")]
fig.legend(handles=h,loc="lower center",ncol=8,fontsize=7.5,frameon=False)
fig.tight_layout(rect=(0,.07,1,1)); fig.savefig(F+"fig4_2_강도별변화.png"); plt.close()
# Fig 5-1 real coverage
t6=pd.read_csv(T+"T6_real_coverage_H5.csv"); c6=pd.read_csv(T+"T6c_real_coverage_by_stock.csv")
fig,ax=plt.subplots(figsize=(8,6)); rows=CO[:19][::-1]
for i,(m,L,k) in enumerate(rows):
    a=t6[(t6.model==m)&(t6.L==L)&(t6.input==k)&(t6.panel=="ALL")].iloc[0]; cs=c6[(c6.model==m)&(c6.L==L)&(c6.input==k)].iloc[0,3:].astype(float)*100
    col=COL.get(m,"k")
    if a["cov"]<0.5:
        ax.annotate(f"{100*a['cov']:.1f}% ({cs.min():.0f}~{cs.max():.0f}) ◀",(70.3,i),va="center",fontsize=7.5,color=col); continue
    ax.plot([cs.min(),cs.max()],[i,i],color=col,lw=5,alpha=.25,solid_capstyle="butt")
    ax.errorbar(100*a["cov"],i,xerr=[[100*(a["cov"]-a.cov_lo)],[100*(a.cov_hi-a["cov"])]],fmt="o",color=col,ms=4,capsize=2)
ax.axvline(80,color="k",lw=1); ax.axvspan(78,82,color="gray",alpha=.1)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([lab(*c) for c in rows],fontsize=7.5); ax.set_xlim(70,92)
ax.set_xlabel("커버리지 % (점·막대 = 10종목 전체와 95% 구간, 옅은 띠 = 종목별 범위)")
fig.tight_layout(); fig.savefig(F+"fig5_1_실제커버리지.png"); plt.close()
# Fig 5-2 H5(RW 대비 손실)
t7=pd.read_csv(T+"T7_H6_real.csv"); rows=CO[:16][::-1]
fig,ax=plt.subplots(figsize=(7.5,5.2))
for i,(m,L,k) in enumerate(rows):
    r=t7[(t7.model==m)&(t7.L==L)&(t7.input==k)].iloc[0]; v=100*r.impr_vs_rw
    ax.barh(i,v,color=COL[m],alpha=.85 if r.p_holm<.05 else .35)
    ax.text(v-0.4 if v<0 else v+0.3,i,f"{v:+.1f}",va="center",ha="right" if v<0 else "left",fontsize=7)
ax.axvline(0,color="k",lw=1); ax.axvspan(-2,2,color="gray",alpha=.1)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([lab(*c) for c in rows],fontsize=7.5); ax.set_xlim(-12,4)
ax.set_xlabel("과거변동(RW, 같은 과거 길이) 대비 분위수 손실 개선 % (오른쪽 = TSFM이 나음)\n진한 막대 = Holm 보정 유의, 옅은 막대 = 유의하지 않음, 회색 띠 = 실질 기준 ±2%")
fig.tight_layout(); fig.savefig(F+"fig5_2_RW손실.png"); plt.close()
# Fig 5-3 econ
E1=pd.read_pickle(str(_R/"04_실험코드/results_v4_t5fix_econ/E1_curves.pkl")); E2=pd.read_pickle(str(_R/"04_실험코드/results_v4_t5fix_econ/E2_ports.pkl"))
fig,axs=plt.subplots(1,2,figsize=(12,4.3),sharey=True)
def cum(r): return np.cumprod(1+r.values), r.index
for key,ax,title in [(None,axs[0],"방향 매매 (비용 반영)"),(1,axs[1],"비중 조절 (보정 구간, 비용 반영)")]:
    if key is None:
        for nm,r in E1.items():
            if nm=="계속 보유": continue
            m=[k for k,v in NM.items() if nm.startswith(v)][0]
            if m in COL: y,x=cum(r); ax.plot(x,y,color=COL[m],lw=.8,alpha=.7)
        y,x=cum(E1["과거변동(RW) 1년·수익률"]); ax.plot(x,y,color="k",lw=1.6,ls="--",label="과거변동(RW) 1년")
    else:
        for kk,r in E2.items():
            if kk=="보유" or kk[3]!="보정": continue
            if kk[0] in COL: y,x=cum(r); ax.plot(x,y,color=COL[kk[0]],lw=.8,alpha=.7)
        y,x=cum(E2[("rw",252,"return","보정")]); ax.plot(x,y,color="k",lw=1.6,ls="--",label="과거변동(RW) 1년")
    y,x=cum(E1["계속 보유"]); ax.plot(x,y,color="goldenrod",lw=2,label="계속 보유")
    ax.set_yscale("log"); ax.set_title(title); ax.grid(alpha=.3)
axs[0].set_ylabel("누적 배수 (로그 눈금, 시작 = 1)")
h=[Line2D([],[],color=c,label=NM[m]) for m,c in COL.items()]+[Line2D([],[],color="k",ls="--",lw=1.6,label="과거변동(RW) 1년"),Line2D([],[],color="goldenrod",lw=2,label="계속 보유")]
fig.legend(handles=h,loc="lower center",ncol=6,frameon=False,fontsize=8)
fig.tight_layout(rect=(0,.07,1,1)); fig.savefig(F+"fig5_4_경제적가치.png"); plt.close()
# Fig 6-1 calibration dumbbell (real) + synthetic range
t4=pd.read_csv(T+"T4_H5_synth.csv"); rows=CO[:19][::-1]
fig,axs=plt.subplots(1,2,figsize=(12,6),sharey=True)
for i,(m,L,k) in enumerate(rows):
    col=COL.get(m,"k")
    g=t4[(t4.model==m)&(t4.L==L)&(t4.input==k)]
    a=t6[(t6.model==m)&(t6.L==L)&(t6.input==k)&(t6.panel=="ALL")].iloc[0]
    for ax,(b0,b1,c0,c1) in [(axs[0],(g["cov"].min(),g["cov"].max(),g.cal.min(),g.cal.max())),(axs[1],(a["cov"],a["cov"],a.cal,a.cal))]:
        x0=100*(b0+b1)/2; x1=100*(c0+c1)/2
        ax.annotate("",xy=(max(x1,0),i),xytext=(max(x0,0),i),arrowprops=dict(arrowstyle="->",color=col,lw=1.2))
        ax.plot([100*b0,100*b1],[i,i],color=col,lw=5,alpha=.3,solid_capstyle="butt"); ax.plot([100*c0,100*c1],[i,i],color=col,lw=5,solid_capstyle="butt")
        ax.plot(x0,i,"o",mfc="white",mec=col,ms=4); ax.plot(x1,i,"o",color=col,ms=4)
for ax,t in zip(axs,["합성 17개 시나리오 (막대 = 시나리오 범위)","실제 10종목 (2017~2026)"]):
    ax.axvline(80,color="k",lw=1); ax.axvspan(77,83,color="gray",alpha=.1); ax.set_title(t); ax.set_xlim(70,92)
    ax.set_xlabel("커버리지 % (빈 점 = 보정 전, 찬 점 = 보정 후, 회색 띠 = 판정 범위 77~83%)")
axs[0].set_yticks(range(len(rows))); axs[0].set_yticklabels([lab(*c) for c in rows],fontsize=7.5)
fig.tight_layout(); fig.savefig(F+"fig6_1_보정전후.png"); plt.close()
print("ok")
