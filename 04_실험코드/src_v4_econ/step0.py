from econ_v4 import *
df=load(); df.to_parquet(OUT/"real_all.parquet")
print(df.groupby(["model","L","input"]).size().to_string()); print(df.date.min(), df.date.max(), df.unit.nunique())
# sanity: continuous calibrated coverage vs T6b
c=((df.y>=df.cal_lo)&(df.y<=df.cal_hi)).groupby([df.model,df.L,df.input]).mean().round(4); print(c.to_string())
