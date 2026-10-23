#!/usr/bin/env python3
"""Phase 2a preview computations for the TvL multi-domain extension (2026-10-22).
Run from extension-assets/: python prep-diagnostics/prep_previews.py
Produces the numbers recorded in previews.json (modulo library versions)."""
import glob, io, zipfile
import numpy as np, pandas as pd, pyreadr

EA = '.'

# ---- tennis: skill = career point-win share; success = titles ----
fs = [f for f in sorted(glob.glob(f'{EA}/tennis/atp_matches_*.csv'))
      if f[-8:-4].isdigit() and 1991 <= int(f[-8:-4]) <= 2025]
m = pd.concat([pd.read_csv(f, low_memory=False) for f in fs], ignore_index=True)
m = m[m['tourney_level'].isin(['G', 'M', 'A', 'F'])]
st = m.dropna(subset=['w_svpt','l_svpt','w_1stWon','w_2ndWon','l_1stWon','l_2ndWon'])
st = st[(st.w_svpt > 0) & (st.l_svpt > 0)]
rows = []
for side, s, o in [('winner','w','l'), ('loser','l','w')]:
    won = st[f'{s}_1stWon'] + st[f'{s}_2ndWon'] + (st[f'{o}_svpt'] - st[f'{o}_1stWon'] - st[f'{o}_2ndWon'])
    rows.append(pd.DataFrame({'pid': st[f'{side}_id'], 'name': st[f'{side}_name'],
                              'won': won, 'tot': st.w_svpt + st.l_svpt}))
agg = pd.concat(rows).groupby(['pid','name']).agg(won=('won','sum'), tot=('tot','sum'), n=('won','size')).reset_index()
agg = agg[agg.n >= 200]; agg['pwin'] = agg.won / agg.tot
finals = m[m['round'] == 'F']
agg = agg.join(finals.groupby('winner_id').size().rename('titles'), on='pid')
agg['titles'] = agg.titles.fillna(0)
agg['skill_pct'] = agg.pwin.rank(pct=True)
t = np.sort(agg.titles.values)[::-1]
print('tennis n:', len(agg),
      '| #1 success:', agg.sort_values('titles', ascending=False).iloc[0][['name','titles','skill_pct']].tolist(),
      '| spearman:', agg[['pwin','titles']].corr(method='spearman').iloc[0,1],
      '| top20% titles share:', t[:len(t)//5].sum()/t.sum(),
      '| pwin mean/sd/skew:', agg.pwin.mean(), agg.pwin.std(), agg.pwin.skew())
rk = pd.concat([pd.read_csv(f'{EA}/tennis/atp_rankings_{d}.csv') for d in ['10s','20s']])
rk['date'] = pd.to_datetime(rk.ranking_date.astype(str), format='%Y%m%d'); rk['yr'] = rk.date.dt.year
ye = rk.sort_values('date').groupby(['yr','player']).last().reset_index()
cors = []
for y in range(2011, 2025):
    j = ye[(ye.yr==y) & (ye['rank']<=100)][['player','points']].merge(ye[ye.yr==y+1][['player','points']], on='player', suffixes=('_t','_t1'))
    if len(j) > 50: cors.append(j[['points_t','points_t1']].corr(method='spearman').iloc[0,1])
print('tennis top100 y2y spearman mean:', np.mean(cors), 'pairs:', len(cors))

# ---- chess: FIDE jan25 vs jan26 top-100 persistence ----
def fide(z):
    zf = zipfile.ZipFile(z); n = [x for x in zf.namelist() if x.lower().endswith('.txt')][0]
    with zf.open(n) as f:
        txt = io.TextIOWrapper(f, encoding='latin-1'); hdr = txt.readline()
        c = hdr.index('JAN')
        out = {}
        for line in txt:
            fid = line[0:15].strip(); r = line[c:c+4].strip()
            if fid and r.isdigit(): out[fid] = int(r)
    return out
r25, r26 = fide(f'{EA}/chess/standard_jan25frl.zip'), fide(f'{EA}/chess/standard_jan26frl.zip')
top = sorted(r25.items(), key=lambda kv: -kv[1])[:100]
a = pd.DataFrame([(v, r26.get(k)) for k, v in top if r26.get(k)], columns=['t','t1'])
allr = pd.Series(list(r25.values()))
print('chess rated:', len(r25), len(r26), '| top100 y2y spearman:', a.corr(method='spearman').iloc[0,1],
      '| rating mean/sd/skew:', allr.mean(), allr.std(), allr.skew())

# ---- baseball ----
T = pyreadr.read_r(f'{EA}/baseball/lahman_rda/Teams.RData')['Teams']
T = T[T.yearID >= 1961]; T['wpct'] = T.W/(T.W+T.L)
cors = []
for y in range(1961, 2025):
    j = T[T.yearID==y][['teamID','wpct']].merge(T[T.yearID==y+1][['teamID','wpct']], on='teamID', suffixes=('_t','_t1'))
    if len(j) > 15: cors.append(j[['wpct_t','wpct_t1']].corr().iloc[0,1])
rec = T[T.yearID.between(2015,2025) & (T.G > 150)]
print('MLB y2y:', np.mean(cors), '| luck share:', (0.25/162)/rec.groupby('yearID').wpct.var().mean())
S = pyreadr.read_r(f'{EA}/baseball/lahman_rda/Salaries.RData')['Salaries']
v = np.sort(S[S.yearID==2016].groupby('playerID').salary.sum().values)[::-1]
print('salary2016 top20% share:', v[:len(v)//5].sum()/v.sum(), 'n:', len(v))

# ---- science + movies ----
c = pd.read_csv(f'{EA}/science/openalex_2015_article_sample_citations.csv')
v = np.sort(c.cited_by_count.values)[::-1]
print('science top20%:', v[:len(v)//5].sum()/v.sum(), 'zero frac:', (v==0).mean())
r = pd.read_csv(f'{EA}/entertainment/imdb/title.ratings.tsv.gz', sep='\t')
b = pd.read_csv(f'{EA}/entertainment/imdb/title.basics.tsv.gz', sep='\t', usecols=['tconst','titleType'], dtype=str)
j = r.merge(b[b.titleType=='movie'], on='tconst'); j = j[j.numVotes >= 1000]
vv = np.sort(j.numVotes.values)[::-1]
j['qual_pct'] = j.averageRating.rank(pct=True)
print('movies n:', len(j), '| votes top20%:', vv[:len(vv)//5].sum()/vv.sum(),
      '| top-voted quality pct:', j.sort_values('numVotes', ascending=False).qual_pct.iloc[0],
      '| spearman rating-votes:', j[['averageRating','numVotes']].corr(method='spearman').iloc[0,1])
