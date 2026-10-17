import pandas as pd, numpy as np, json
df=pd.read_pickle('df.pkl'); g=pd.read_csv('genres.csv'); co=pd.read_csv('countries.csv')
fin=df[(df.budget>=10000)&(df.revenue>=10000)].copy(); fin['roi']=fin.revenue/fin.budget; fin['fr']=fin.belongs_to_collection.notna()
fin['h2']=fin.roi>=2
out={}
out['funnel']=[['Raw rows',45466],['Valid unique films',len(df)],['Budget reported (≥$10K)',int((df.budget>=10000).sum())],['Revenue reported (≥$10K)',int((df.revenue>=10000).sum())],['Both reported (analysis set)',len(fin)]]
def st(s,name,unit=''):
    s=s.dropna(); q1,q3=s.quantile([.25,.75]); i=q3-q1
    return dict(var=name,n=int(len(s)),mean=float(s.mean()),median=float(s.median()),sd=float(s.std()),skew=float(s.skew()),out=int(((s<q1-1.5*i)|(s>q3+1.5*i)).sum()),outpct=float(((s<q1-1.5*i)|(s>q3+1.5*i)).mean()))
out['stats']=[st(fin.budget,'Budget ($)'),st(fin.revenue,'Revenue ($)'),st(fin.roi,'ROI (rev ÷ budget)'),st(fin.runtime[fin.runtime>0],'Runtime (min)'),st(fin.vote_average[fin.vote_count>0],'Vote average'),st(fin.vote_count,'Vote count'),st(fin.popularity,'Popularity')]
out['stats_all']=[st(df.budget[df.budget>0],'Budget'),st(df.revenue[df.revenue>0],'Revenue'),st(df.runtime[df.runtime>0],'Runtime'),st(df.vote_average[df.vote_count>0],'Vote avg'),st(df.vote_count,'Vote count')]
def hist(s,bins,labels):
    c=pd.cut(s,bins,labels=labels,right=False).value_counts().reindex(labels).fillna(0); return [str(l) for l in labels],[int(x) for x in c]
out['h_budget']=hist(fin.budget,[1e4,1e5,1e6,1e7,1e8,1e9,1e10],['$10K-100K','$100K-1M','$1M-10M','$10M-100M','$100M-1B','$1B+'])
out['h_rev']=hist(fin.revenue,[1e4,1e5,1e6,1e7,1e8,1e9,1e10],['$10K-100K','$100K-1M','$1M-10M','$10M-100M','$100M-1B','$1B+'])
out['h_roi']=hist(fin.roi,[0,.5,1,2,4,8,16,1e9],['<0.5x','0.5-1x','1-2x','2-4x','4-8x','8-16x','16x+'])
out['h_run']=hist(fin.runtime,[1,80,90,100,110,120,140,400],['<80','80-89','90-99','100-109','110-119','120-139','140+'])
v=fin.vote_average[fin.vote_count>0]; out['h_vote']=hist(v,[0,4,5,5.5,6,6.5,7,7.5,8,11],['<4','4-5','5-5.5','5.5-6','6-6.5','6.5-7','7-7.5','7.5-8','8+'])
out['h_vc']=hist(fin.vote_count,[0,10,50,100,500,1000,5000,1e6],['<10','10-49','50-99','100-499','500-999','1K-5K','5K+'])
bins=[0,1e6,5e6,15e6,30e6,60e6,100e6,1e9]; lab=['<$1M','$1-5M','$5-15M','$15-30M','$30-60M','$60-100M','$100M+']
fin['band']=pd.cut(fin.budget,bins,labels=lab)
b=fin.groupby('band',observed=True).agg(n=('id','count'),med=('roi','median'),h2=('h2','mean'),p25=('roi',lambda s:s.quantile(.25))).round(3)
out['band']=b.reset_index().astype({'band':str}).to_dict('list')
bf=fin.groupby(['band','fr'],observed=True).roi.median().unstack().round(2); out['band_fr']={'band':[str(x) for x in bf.index],'non':bf[False].tolist(),'fr':bf[True].tolist()}
out['fr']={k:dict(n=int(len(x)),med=float(x.roi.median()),h2=float(x.h2.mean()),mrev=float(x.revenue.median())) for k,x in [('fr',fin[fin.fr]),('non',fin[~fin.fr])]}
gm=g[g.movie_id.isin(fin.id)].drop(columns='id').merge(fin[['id','roi','h2','budget','revenue']],left_on='movie_id',right_on='id')
gs=gm.groupby('name').agg(n=('id','count'),med=('roi','median'),h2=('h2','mean'),mbud=('budget','median'),mrev=('revenue','median')).query('n>=100').sort_values('med',ascending=False).round(3)
out['genre']=gs.reset_index().to_dict('list')
fin['m']=fin.release_date.dt.month
ms=fin.groupby('m').agg(n=('id','count'),med=('roi','median'),h2=('h2','mean')).round(3); out['month']=ms.reset_index().to_dict('list')
# horror low budget
hh=gm[gm.name=='Horror']; out['horror']=dict(low=dict(n=int((hh.budget<15e6).sum()),med=float(hh[hh.budget<15e6].roi.median()),h2=float(hh[hh.budget<15e6].h2.mean())),hi=dict(n=int((hh.budget>=15e6).sum()),med=float(hh[hh.budget>=15e6].roi.median())))
# segments for rec
def seg(x): return dict(n=int(len(x)),med=float(x.roi.median()),h2=float(x.h2.mean()),p25=float(x.roi.quantile(.25)),mrev=float(x.revenue.median()))
tent=fin[(fin.budget>=1e8)]; out['tent']=seg(tent); out['tent_fr']=seg(tent[tent.fr])
fam=gm[gm.name.isin(['Animation','Family','Adventure'])].drop_duplicates('movie_id'); out['afa_tent']=seg(fam[fam.budget>=6e7])
out['mid_nonfr']=seg(fin[(fin.budget>=5e6)&(fin.budget<30e6)&(~fin.fr)])
out['lowhorror']=seg(fin[fin.id.isin(hh[hh.budget<15e6].movie_id)])
out['seasons']=dict(peak=seg(fin[fin.m.isin([6,7,12])]),sep=seg(fin[fin.m==9]))
# expected vs actual
alll=df.original_language.value_counts(normalize=True); 
out['bias_cmp']={'lang_en_all':float((df.original_language=='en').mean()),'lang_en_fin':float((fin.original_language=='en').mean()),
 'us_all':float(co[co.name=='United States of America'].movie_id.nunique()/co.movie_id.nunique()),'us_fin':float(co[(co.name=='United States of America')&co.movie_id.isin(fin.id)].movie_id.nunique()/co[co.movie_id.isin(fin.id)].movie_id.nunique()),
 'doc_all':float(g[g.name=='Documentary'].movie_id.nunique()/len(df)),'doc_fin':float(g[(g.name=='Documentary')&g.movie_id.isin(fin.id)].movie_id.nunique()/len(fin)),
 'post1980_all':float((df.year>=1980).mean()),'post1980_fin':float((fin.year>=1980).mean()),
 'votes10_all':float(((df.vote_count<10)).mean()),'votes10_fin':float((fin.vote_count<10).mean()),
 'nonen_n_fin':int((fin.original_language!='en').sum())}
print(json.dumps(out['bias_cmp'],indent=1))
yr=df.year.value_counts().sort_index(); out['year_dist']={'dec':[str(int(k)) for k in sorted((df.year.dropna()//10*10).unique()) if 1900<=k<=2010],}
dd=(df.year//10*10).value_counts().sort_index(); out['decade']={'lab':[f"{int(k)}s" for k in dd.index if 1900<=k<=2010],'n':[int(dd[k]) for k in dd.index if 1900<=k<=2010]}
dfin=(fin.year//10*10).value_counts().sort_index(); out['decade_fin']=[int(dfin.get(k,0)) for k in dd.index if 1900<=k<=2010]
out['totals']=dict(all=len(df),fin=len(fin),hit_all=float(fin.h2.mean()),med_roi=float(fin.roi.median()),yrmin=int(df.year.min()),pre1980=float((df.year<1980).mean()))
json.dump(out,open('data.json','w'),indent=1,default=float)
for k in ['band','genre','month']: print(k,pd.DataFrame(out[k]).to_string())
for k in ['fr','tent','tent_fr','afa_tent','mid_nonfr','lowhorror','seasons','horror','totals']: print(k,out[k])
print(out['stats']); print(out['funnel'])
