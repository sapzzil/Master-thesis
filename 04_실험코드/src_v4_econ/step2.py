from econ_v4 import *
df=pd.read_parquet(OUT/"real_all.parquet")
rows=[]; curves={}; ports={}
base=df[(df.model=="rw")&(df.L==21)]
sr=strat_returns(base, lambda s: np.ones(len(s))); p=portfolio(sr); ports["보유"]=p
rows.append({"전략":"계속 보유","구간":"-",**metrics(p,sr),"실현변동/목표":(sr.r.std()/TARGET)})
for (m,L,k),g in df.groupby(["model","L","input"]):
    for kind,(lo,hi) in [("원래",("q1","q9")),("보정",("cal_lo","cal_hi"))]:
        wf=lambda s,lo=lo,hi=hi: np.minimum(1.0, TARGET/np.maximum((s[hi].values-s[lo].values)/Z80,1e-6))
        sr=strat_returns(g, wf); p=portfolio(sr); ports[(m,L,k,kind)]=p
        # 실현변동/목표: 종목별 전략 일수익률 표준편차 평균 / 1%
        rv=sr.groupby("unit").r.std().mean()/TARGET
        rows.append({"전략":label(m,L,k),"구간":kind,**metrics(p,sr),"실현변동/목표":rv})
t=pd.DataFrame(rows)
# 샤프 차이 vs RW(같은 L, 같은 구간 종류)
d=[]
for r in t.itertuples():
    if r.전략=="계속 보유": d.append((np.nan,np.nan,np.nan)); continue
    key=[k for k in ports if k!="보유" and label(*k[:3])==r.전략 and k[3]==r.구간][0]
    m,L,k,kind=key
    if m=="rw": d.append((np.nan,np.nan,np.nan)); continue
    ref=("rw",L if m!="garch_t" else 252,"return",kind)
    d.append(boot_sharpe_diff(ports[key], ports[ref]))
t["샤프차_vsRW"],t["차_lo"],t["차_hi"]=zip(*d)
t.to_csv(OUT/"E2_voltarget.csv",index=False,encoding="utf-8-sig"); pd.to_pickle(ports,OUT/"E2_ports.pkl")
pd.set_option("display.width",250)
print(t.round(3).to_string(index=False))
