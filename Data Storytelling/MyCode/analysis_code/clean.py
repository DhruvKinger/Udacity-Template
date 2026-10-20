import pandas as pd, ast, numpy as np
raw = pd.read_csv('/home/claude/data/movies-metadata.csv', low_memory=False)
n0=len(raw)
# 1 malformed rows (shifted columns)
bad = pd.to_numeric(raw['id'],errors='coerce').isna()
df = raw[~bad].copy(); print('malformed removed',bad.sum())
df['id']=df['id'].astype(int)
for c in ['budget','popularity']: df[c]=pd.to_numeric(df[c])
# 2 duplicates
dups = df.duplicated('id',keep='first').sum(); df=df.drop_duplicates('id'); print('dup ids removed',dups)
df['release_date']=pd.to_datetime(df['release_date'],errors='coerce')
df['year']=df.release_date.dt.year
print('after',len(df))
def parse(s):
    try: return ast.literal_eval(s)
    except: return []
def explode(col, key_cols):
    rows=[]
    for i,s in zip(df['id'],df[col]):
        if isinstance(s,str):
            for d in parse(s):
                rows.append({'movie_id':i, **{k:d.get(k) for k in key_cols}})
    return pd.DataFrame(rows)
genres=explode('genres',['id','name']); countries=explode('production_countries',['iso_3166_1','name'])
companies=explode('production_companies',['id','name']); langs=explode('spoken_languages',['iso_639_1','name'])
for n,t in [('genres',genres),('countries',countries),('companies',companies),('langs',langs)]:
    t.to_csv(f'/home/claude/work/{n}.csv',index=False); print(n,len(t),t.movie_id.nunique())
# financial
df['has_budget']=df.budget>0; df['has_rev']=df.revenue>0
df['has_both']=df.has_budget&df.has_rev
print('budget=0',(df.budget==0).mean(),'rev=0',(df.revenue==0).mean(),'both>0',df.has_both.sum(), df.has_both.mean())
print('runtime=0',(df.runtime==0).sum(),'vote_count=0',(df.vote_count==0).sum(), 'no genres', (~df.id.isin(genres.movie_id)).sum())
df['roi']=np.where(df.has_both, df.revenue/df.budget, np.nan)
df.to_pickle('/home/claude/work/df.pkl')
# distributions
cols=['budget','revenue','runtime','popularity','vote_average','vote_count','roi']
d=df[cols].copy()
print(d.describe().T[['count','mean','50%','std','min','max']])
fin=df[df.has_both]
print('--- financial subset (both>0)')
print(fin[['budget','revenue','runtime','popularity','vote_average','vote_count','roi']].describe().T[['count','mean','50%','std','min','max']])
print(df[df.vote_count>0].vote_average.describe())
# outliers IQR
def iqr(s):
    s=s.dropna(); q1,q3=s.quantile([.25,.75]); i=q3-q1; return ((s<q1-1.5*i)|(s>q3+1.5*i)).sum(), len(s)
for c in ['budget','revenue','runtime','popularity','vote_average','vote_count']:
    s=df[c]; s=s[s>0] if c in('budget','revenue','runtime') else s
    print(c,'IQR outliers',iqr(s), 'skew',round(s.skew(),2))
print('roi outliers',iqr(fin.roi), 'roi>100', (fin.roi>100).sum(), 'roi<0.01',(fin.roi<0.01).sum())
print(fin.sort_values('roi',ascending=False)[['title','budget','revenue','roi']].head(8))
print(fin[fin.budget<1000][['title','budget','revenue']].shape)
print('budget<1000 (nonzero)',((df.budget>0)&(df.budget<1000)).sum(),'rev<1000 nonzero',((df.revenue>0)&(df.revenue<1000)).sum())
print('runtime>300',(df.runtime>300).sum(),'max',df.runtime.max())
print('year range',df.year.min(),df.year.max(), 'null year',df.year.isna().sum())
