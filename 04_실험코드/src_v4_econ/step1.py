from econ_v4 import *
df=pd.read_parquet(OUT/"real_all.parquet")
rows=[]; curves={}
base=df[(df.model=="rw")&(df.L==21)]
for zero in [False, True]:
    sr=strat_returns(base, lambda s: np.ones(len(s)), zero); p=portfolio(sr)
    rows.append({"전략":"계속 보유","비용":"없음" if zero else "있음",**metrics(p,sr)})
    if not zero: curves["계속 보유"]=p
for (m,L,k),g in df.groupby(["model","L","input"]):
    for zero in [False, True]:
        sr=strat_returns(g, lambda s: (s.q5.values>0).astype(float), zero); p=portfolio(sr)
        rows.append({"전략":label(m,L,k),"비용":"없음" if zero else "있음",**metrics(p,sr)})
        if not zero: curves[label(m,L,k)]=p
t=pd.DataFrame(rows); t.to_csv(OUT/"E1_direction.csv",index=False,encoding="utf-8-sig")
pd.to_pickle(curves, OUT/"E1_curves.pkl")
pd.set_option("display.width",200)
print(t[t.비용=="있음"].round(3).to_string(index=False))
print(t[t.비용=="없음"][["전략","연수익률%","샤프"]].round(3).to_string(index=False))
# per-market buy&hold
for mk,us in [("US",True),("KR",False)]:
    g=base[base.unit.isin(US)==us]; sr=strat_returns(g, lambda s: np.ones(len(s))); print(mk,"계속보유",{k:round(v,3) for k,v in metrics(portfolio(sr)).items()})
