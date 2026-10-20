import pandas as pd, numpy as np
df=pd.read_pickle('df.pkl'); g=pd.read_csv('genres.csv')
fin=df[(df.budget>=10000)&(df.revenue>=10000)].copy(); fin['roi']=fin.revenue/fin.budget
fin['fr']=fin.belongs_to_collection.notna()
bins=[0,1e6,5e6,15e6,30e6,60e6,100e6,1e9]; lab=['<1M','1-5M','5-15M','15-30M','30-60M','60-100M','100M+']
fin['band']=pd.cut(fin.budget,bins,labels=lab)
print(fin.groupby(['band','fr'],observed=True).agg(n=('id','count'),med=('roi','median'),hit=('roi',lambda s:(s>=1).mean())).round(2).unstack())
print(df.year.value_counts().sort_index().tail(8))
fin['dec']=fin.year//10*10
print(fin.groupby('dec').agg(n=('id','count'),med_bud=('budget','median'),med_rev=('revenue','median'),med_roi=('roi','median')).round(2).tail(7))
hm=g[g.name.isin(['Horror','Animation','Drama'])].drop(columns='id').merge(fin[['id','budget','roi','fr']],left_on='movie_id',right_on='id')
hm['lowb']=hm.budget<15e6
print(hm.groupby(['name','lowb']).agg(n=('id','count'),med=('roi','median'),hit=('roi',lambda s:(s>=1).mean())).round(2))
rng=np.random.default_rng(0)
def boot(a,b):
    d=[np.median(rng.choice(a,len(a)))-np.median(rng.choice(b,len(b))) for _ in range(2000)]; return np.percentile(d,[2.5,97.5]).round(2)
print('franchise diff CI',boot(fin[fin.fr].roi.values,fin[~fin.fr].roi.values))
print('anim vs drama CI',boot(hm[hm.name=='Animation'].roi.values,hm[hm.name=='Drama'].roi.values))
m=fin.release_date.dt.month; summer=fin[m.isin([6,7,12])].roi.values; sep=fin[m==9].roi.values
print('jun/jul/dec vs sep',boot(summer,sep), np.median(summer),np.median(sep))
mid=fin[(fin.budget>=5e6)&(fin.budget<30e6)].roi.values; rest=fin[~((fin.budget>=5e6)&(fin.budget<30e6))].roi.values
print('mid vs rest',boot(mid,rest),np.median(mid),np.median(rest), len(mid))
# franchise share of tentpoles
print('fr share by band',fin.groupby('band',observed=True).fr.mean().round(2))
# full-vs-fin comparison of genre share
allg=g.name.value_counts(normalize=True); fg=g[g.movie_id.isin(fin.id)].name.value_counts(normalize=True)
print(pd.DataFrame({'all':allg,'fin':fg}).round(3).head(8))
print('doc share', allg['Documentary'], fg['Documentary'])
# anomalies: runtime, rating
print('runtime 0',(df.runtime==0).sum(),'>300',(df.runtime>300).sum(), 'rating 0 w/ votes>0',((df.vote_average==0)&(df.vote_count>0)).sum(), 'vote_avg==0 & vc==0',((df.vote_average==0)&(df.vote_count==0)).sum())
print('adult true',(df.adult=='True').sum(),'video true',(df.video==True).sum())
print('status released share', (df.status=='Released').mean(), 'unreleased with revenue', ((df.status!='Released')&(df.revenue>0)).sum())
print('budget<1000 & >0',((df.budget>0)&(df.budget<1000)).sum(),'rev<1000&>0',((df.revenue>0)&(df.revenue<1000)).sum())
print('roi<0.1', (fin.roi<0.1).sum(), 'roi>50',(fin.roi>50).sum())
print('median votes fin',fin.vote_count.median(),'all',df.vote_count.median())
print('lang counts all', df.original_language.nunique())
print(df[df.original_language=='hi'].shape[0], df[df.original_language=='zh'].shape[0], df[df.original_language=='ko'].shape[0], df[df.original_language=='pt'].shape[0])
