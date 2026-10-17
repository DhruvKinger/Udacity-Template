import pandas as pd, numpy as np
pd.set_option('display.width',200); pd.set_option('display.max_columns',30)
df=pd.read_pickle('/home/claude/work/df.pkl')
g=pd.read_csv('/home/claude/work/genres.csv'); co=pd.read_csv('/home/claude/work/countries.csv'); cm=pd.read_csv('/home/claude/work/companies.csv'); lg=pd.read_csv('/home/claude/work/langs.csv')
df=df[df.status=='Released'] if False else df
fin=df[(df.budget>=10000)&(df.revenue>=10000)].copy()
fin['roi']=fin.revenue/fin.budget; fin['profit']=fin.revenue-fin.budget
print('analysis set',len(fin), 'of',len(df), len(fin)/len(df))
print(fin[['budget','revenue','roi','profit','runtime','vote_average','vote_count','popularity']].agg(['count','mean','median','std','min','max']).T)
print('fin roi >=1 share', (fin.roi>=1).mean(), 'median roi',fin.roi.median())
# genre
gm=g[g.movie_id.isin(fin.id)].drop(columns='id').merge(fin[['id','budget','revenue','roi','vote_average','profit']],left_on='movie_id',right_on='id')
gs=gm.groupby('name').agg(n=('movie_id','count'),med_roi=('roi','median'),mean_roi=('roi','mean'),med_rev=('revenue','median'),med_bud=('budget','median'),rating=('vote_average','mean'),hit=('roi',lambda s:(s>=1).mean()),med_profit=('profit','median')).sort_values('med_roi',ascending=False)
print(gs.round(2))
# overall genre counts in full dataset
print(g.name.value_counts().head(10), g.name.value_counts(normalize=True).head(5))
# budget bands
bins=[0,1e6,5e6,15e6,30e6,60e6,100e6,1e9]; lab=['<1M','1-5M','5-15M','15-30M','30-60M','60-100M','100M+']
fin['band']=pd.cut(fin.budget,bins,labels=lab)
print(fin.groupby('band',observed=True).agg(n=('id','count'),med_roi=('roi','median'),hit=('roi',lambda s:(s>=1).mean()),med_rev=('revenue','median'),p25=('roi',lambda s:s.quantile(.25)),p75=('roi',lambda s:s.quantile(.75)),rating=('vote_average','mean')).round(2))
# correlations (spearman)
print(fin[['budget','revenue','roi','runtime','vote_average','vote_count','popularity']].corr(method='spearman').round(2))
# month
fin['month']=fin.release_date.dt.month
print(fin.groupby('month').agg(n=('id','count'),med_roi=('roi','median'),med_rev=('revenue','median'),hit=('roi',lambda s:(s>=1).mean())).round(2))
# decade presence
df['decade']=(df.year//10*10)
print(df.groupby('decade').agg(n=('id','count'),bud_missing=('budget',lambda s:(s==0).mean()),rev_missing=('revenue',lambda s:(s==0).mean())).round(2).tail(12))
# franchise
fin['fr']=fin.belongs_to_collection.notna()
print(fin.groupby('fr').agg(n=('id','count'),med_roi=('roi','median'),med_rev=('revenue','median'),med_bud=('budget','median'),hit=('roi',lambda s:(s>=1).mean())))
# runtime bands
fin['rt']=pd.cut(fin.runtime,[0,90,105,120,140,400],labels=['<90','90-105','105-120','120-140','140+'])
print(fin.groupby('rt',observed=True).agg(n=('id','count'),med_roi=('roi','median'),rating=('vote_average','mean'),med_rev=('revenue','median')).round(2))
# language
print(df.original_language.value_counts(normalize=True).head(8).round(3))
print(fin.original_language.value_counts(normalize=True).head(5).round(3))
print(fin.groupby(fin.original_language=='en').agg(n=('id','count'),med_roi=('roi','median'),med_rev=('revenue','median')))
# country
cs=co.name.value_counts(normalize=True).head(8).round(3); print(cs)
cf=co[co.movie_id.isin(fin.id)].name.value_counts(normalize=True).head(5).round(3); print(cf)
print('US involvement all', co[co.name=='United States of America'].movie_id.nunique()/co.movie_id.nunique(), 'fin', co[(co.name=='United States of America')&co.movie_id.isin(fin.id)].movie_id.nunique()/co[co.movie_id.isin(fin.id)].movie_id.nunique())
# companies
cmf=cm[cm.movie_id.isin(fin.id)].drop(columns='id').merge(fin[['id','roi','revenue']],left_on='movie_id',right_on='id')
top=cmf.groupby('name').agg(n=('id','count'),med_roi=('roi','median'),rev=('revenue','sum')).query('n>=25').sort_values('rev',ascending=False).head(10); print(top.round(2))
print('companies total',cm.name.nunique(),'top10 share of company-credits', cm.name.value_counts().head(10).sum()/len(cm))
# votes
v=df[df.vote_count>0]; print('votes<10 share', (v.vote_count<10).mean(), 'median votecount',v.vote_count.median())
print('rating among >=100 votes', df[df.vote_count>=100].vote_average.describe())
print('vote_count>=100 share', (df.vote_count>=100).mean())
print('unique genres per movie', g.groupby('movie_id').size().describe())
