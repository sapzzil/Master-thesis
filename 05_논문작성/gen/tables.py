# 표 생성: results_v4/tables(T1~T8)와 results_v4_econ 사용. TAB62의 폭 배율(연속 보정)은 real_all.parquet(20MB, git 제외 — src_v4_econ/econ_v4.py로 재생성)이 필요하다.
import pandas as pd, numpy as np
import pathlib
_V=pathlib.Path(__file__).resolve().parents[1]; _R=_V.parent
T=str(_R/"04_실험코드/results_v4_t5fix/tables")+"/"   # 95차: Chronos-T5 top_k 해제 재실행 결과(본문 기준)
E=str(_R/"04_실험코드/results_v4_t5fix_econ")+"/"
NM={"chronos_t5_base":"Chronos-T5","chronos2":"Chronos-2","timesfm25":"TimesFM-2.5","moirai2":"Moirai-2","rw":"과거변동(RW)","garch_t":"GARCH-t","oracle":"오라클 모형"}
ORD=["chronos_t5_base","chronos2","timesfm25","moirai2","rw","garch_t","oracle"]
def lab(m,L,k):
    if m=="oracle": return "오라클 모형 | -"
    return f"{NM[m]} | {'한 달' if L==21 else '1년'}·{'수익률' if k=='return' else '가격'}"
def sg(x):
    """부호 붙인 소수 1자리. 반올림 결과가 0.0이면 부호 없이 0.0"""
    t=f"{x:+.1f}"; return "0.0" if t in ("+0.0","-0.0") else t
def srt(d): d=d.copy(); d["_o"]=d.model.map({m:i for i,m in enumerate(ORD)}); return d.sort_values(["_o","L","input"],ascending=[True,True,False])
pc=lambda x:f"{100*x:.1f}"
out=[]
t1=pd.read_csv(T+"T1_synth_scenarios.csv"); print(t1.model.unique())
# 4-1 L1 baseline + range over all scenarios
rows=[]
for (m,L,k),g in srt(t1).groupby(["model","L","input"],sort=False):
    l1=g[g.scenario=="L1"].iloc[0]
    rows.append(f"| {lab(m,L,k)} | {pc(l1['cov'])} [{pc(l1.cov_lo)}, {pc(l1.cov_hi)}] | {pc(g['cov'].min())}~{pc(g['cov'].max())} | {100*l1.width:.2f} |")
out.append("TAB41\n| 모델 | 조건 | L1 커버리지(%)<br>[95% 구간] | 17개 시나리오<br>범위(%) | L1 평균 폭(%p) |\n|---|---|---|---|---|\n"+"\n".join(rows))
# 4-2 H1-H3b L5-L1
t2=pd.read_csv(T+"T2_H1_H3_levels.csv"); t2=t2[t2.comparison=="L5-L1"]
mk={"지지":"▼","유의하나 작음":"▽","미지지":"","반대":"▲"}
rows=[]
for (m,L,k),g in srt(t2).groupby(["model","L","input"],sort=False):
    c=[]
    for h in ["H1","H2","H3a","H3b"]:
        r=g[g.hyp==h].iloc[0]; j=r["판정"]
        sym="" 
        if isinstance(r.p_holm,float) and not np.isnan(r.p_holm) and r.p_holm<0.05:
            sym = ("▼" if abs(r.dcov)>=0.02 else "▽") if r.dcov<0 else ("▲" if abs(r.dcov)>=0.02 else "△")
        c.append(f"{sg(100*r.dcov)}{sym}")
    rows.append(f"| {lab(m,L,k)} | "+" | ".join(c)+" |")
out.append("TAB42\n| 모델 | 조건 | H1 군집 | H2 꼬리 | H3a 전환빈도 | H3b 전환크기 |\n|---|---|---|---|---|---|\n"+"\n".join(rows))
print(t2["판정"].unique())
# 4-3 H4
t3=pd.read_csv(T+"T3_H4_friedman.csv"); rows=[]
for _,r in srt(t3).iterrows():
    d=[r.deficit_CL,r.deficit_TL,r.deficit_RF,r.deficit_RS]; big=["군집","꼬리","전환빈도","전환크기"][int(np.argmax(d))]
    ph="-" if pd.isna(r.p_holm) else f"{r.p_holm:.1e}"
    rows.append(f"| {lab(r.model,r.L,r.input)} | "+" | ".join(sg(100*x) for x in d)+f" | {100*r.range:.1f} | {big} | {ph} | {'-' if r['판정']=='(기준모형·서술)' else r['판정']} |")
out.append("TAB43\n| 모델 | 조건 | 군집 | 꼬리 | 전환빈도 | 전환크기 | 범위(%p) | 최대 결손 | Holm p | 판정 |\n|---|---|---|---|---|---|---|---|---|---|\n"+"\n".join(rows))
t3b=pd.read_csv(T+"T3b_H4_pairs.csv"); t3b=t3b[~t3b.model.isin(["garch_t","rw"])]
print("pair sig counts\n",t3b.assign(s=t3b.p_holm<0.05).groupby("pair").s.sum())
# 5-1 real
t6=pd.read_csv(T+"T6_real_coverage_H5.csv"); rows=[]
c6=pd.read_csv(T+"T6c_real_coverage_by_stock.csv")
for (m,L,k),g in srt(t6).groupby(["model","L","input"],sort=False):
    a=g.set_index("panel"); cs=c6[(c6.model==m)&(c6.L==L)&(c6.input==k)].iloc[0,3:].astype(float)
    rows.append(f"| {lab(m,L,k)} | {pc(a.loc['ALL','cov'])} [{pc(a.loc['ALL','cov_lo'])}, {pc(a.loc['ALL','cov_hi'])}] | {pc(a.loc['US','cov'])} | {pc(a.loc['KR','cov'])} | {pc(cs.min())}~{pc(cs.max())} | {100*a.loc['ALL','width']:.2f} |")
out.append("TAB51\n| 모델 | 조건 | 전체(%)<br>[95% 구간] | 미국(%) | 한국(%) | 종목별 범위(%) | 평균 폭(%p) |\n|---|---|---|---|---|---|---|\n"+"\n".join(rows))
# 5-2 H6
t7=pd.read_csv(T+"T7_H6_real.csv"); rows=[]
for _,r in srt(t7).iterrows():
    rows.append(f"| {lab(r.model,r.L,r.input)} | {100*r.impr_vs_rw:+.1f} | {r.p_holm:.1e} | {'-' if r['판정']=='(기준모형·서술)' else r['판정']} |")
out.append("TAB52\n| 모델 | 조건 | RW 대비 손실 개선(%) | Holm p | 판정 |\n|---|---|---|---|---|\n"+"\n".join(rows))
# 5-3 post-release
t8=pd.read_csv(T+"T8_real_post_release.csv"); rows=[]
for _,r in srt(t8).iterrows():
    full=t7[(t7.model==r.model)&(t7.L==r.L)&(t7.input==r.input)].iloc[0].impr_vs_rw
    fc=t6[(t6.model==r.model)&(t6.L==r.L)&(t6.input==r.input)&(t6.panel=="ALL")].iloc[0]["cov"]
    rows.append(f"| {lab(r.model,r.L,r.input)} | {r.after} | {r.n:,} | {pc(fc)} → {pc(r['cov'])} | {100*full:+.1f} → {100*r.impr_vs_rw:+.1f} |")
out.append("TAB53\n| 모델 | 조건 | 공개 후 시작일 | 예측 수 | 커버리지(%)<br>(전체 → 공개 후) | RW 대비 개선(%)<br>(전체 → 공개 후) |\n|---|---|---|---|---|---|\n"+"\n".join(rows))
# 6-1 synth calibration
t4=pd.read_csv(T+"T4_H5_synth.csv"); rows=[]
for (m,L,k),g in srt(t4).groupby(["model","L","input"],sort=False):
    wr=(g.cal_width/g.width)
    rows.append(f"| {lab(m,L,k)} | {pc(g['cov'].min())}~{pc(g['cov'].max())} | {pc(g.cal.min())}~{pc(g.cal.max())} | {int(g.restored.sum())}/17 | {pc(g.ctl.min())}~{pc(g.ctl.max())} | {wr.min():.2f}~{wr.max():.2f} |")
out.append("TAB61\n| 모델 | 조건 | 보정 전(%) | 보정 후(%) | 복원 시나리오 | 대조군(%) | 폭 배율(보정/원래) |\n|---|---|---|---|---|---|---|\n"+"\n".join(rows))
print("restored total", t4.restored.sum(), len(t4))
# 6-2 real calibration + continuous + width ratio (continuous)
ra=pd.read_parquet(E+"real_all.parquet"); t6b=pd.read_csv(T+"T6b_real_continuous_aux.csv")
ra["w0"]=ra.q9-ra.q1; ra["w1"]=ra.cal_hi-ra.cal_lo
wr=ra.groupby(["model","L","input"]).apply(lambda d:d.w1.mean()/d.w0.mean())
rows=[]
for (m,L,k),g in srt(t6[t6.panel=="ALL"]).groupby(["model","L","input"],sort=False):
    a=g.iloc[0]; cc=t6b[(t6b.model==m)&(t6b.L==L)&(t6b.input==k)].iloc[0].cont_cov
    rows.append(f"| {lab(m,L,k)} | {pc(a['cov'])} | {pc(a.cal)} [{pc(a.cal_lo90)}, {pc(a.cal_hi90)}] | {'복원' if a.restored else '실패'} | {pc(a.ctl)} | {pc(cc)} | {wr.loc[(m,L,k)]:.2f} |")
out.append("TAB62\n| 모델 | 조건 | 보정 전(%) | 보정 후(%)<br>[90% 구간] | 판정 | 대조군(%) | 연속 보정(%) | 폭 배율(연속) |\n|---|---|---|---|---|---|---|---|\n"+"\n".join(rows))
open(str(_V/"gen/tables.md"),"w").write("\n\n".join(out))
