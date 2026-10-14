from econ_v4 import *
df=pd.read_parquet(OUT/"real_all.parquet")
rows=[]
for (m,L,k),g in df.groupby(["model","L","input"]):
    for kind,lo in [("원래","q1"),("보정","cal_lo")]:
        x=n=0; pk=pc=0; ps=[]
        for u,s in g.sort_values("date").groupby("unit"):
            v=(s.y.values < s[lo].values); x+=v.sum(); n+=len(v)
            p1=kupiec(v.sum(),len(v)); p2=christoffersen(v)
            pk+= p1>=0.05; pc+= p2>=0.05
        rows.append({"모델·조건":label(m,L,k),"구간":kind,"위반율%":x/n*100,"Kupiec통과(10종목중)":pk,"독립성통과(10종목중)":pc,"합산Kupiec_p":kupiec(x,n)})
t=pd.DataFrame(rows); t.to_csv(OUT/"E3_var.csv",index=False,encoding="utf-8-sig")
pd.set_option("display.width",200); print(t.round(3).to_string(index=False))
