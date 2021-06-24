# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
from eurito_indicators.getters.cord.get_cord import get_cord_articles
from eurito_indicators.getters.cord.orm_utils import get_mysql_engine

# %% [markdown]
# * [x] What is the diversity of fields by country?
#     * [ ] What disciplinary dimensions set those countries apart? (specialisation)
# * [x] Which countries are more highly represented in pre-prints?
#     * [x] Expand this to the top 5 - 10 journals
# * [x] Which EU countries have research profiles more similar to each other and which have profiles more similar to outside?
# * [ ] Where have the collaborations happened?
# * [ ] Which countries are more internationally collaborative?
# * [ ] Which countries have the most diverse research according to the titles?
#

# %%
db_path = '/home/ubuntu/mysqldb_team.config'
engine = get_mysql_engine(db_path)

# %%
import pandas as pd

# %%
query = "SELECT * FROM arxiv_articles WHERE article_source = 'cord'"
articles = pd.read_sql(query, engine)
# articles = articles.merge(institutes, how='inner', left_on='institute_id', right_on='id')

# %%
query = "SELECT * FROM arxiv_article_institutes"
arxiv_article_institutes = pd.read_sql(query, engine)

# %%
arxiv_article_institutes = arxiv_article_institutes[arxiv_article_institutes['article_id'].isin(articles['id'])]

# %%
from collections import defaultdict

# %%
article_insts = defaultdict(list)

for art, inst in zip(arxiv_article_institutes['article_id'], arxiv_article_institutes['institute_id']):
    article_insts[art].append(inst)

# %%
institute_query = "SELECT * FROM grid_institutes"
institutes = pd.read_sql(institute_query, engine)
institutes_dict = institutes.set_index('id').to_dict('index')

# %%
article_countries = dict()

for art, inst_ids in article_insts.items():
    countries = [institutes_dict[i]['country_code'] for i in inst_ids]
    article_countries[art] = [c for c in countries if c is not None]

# %%
from collections import Counter
from itertools import chain
import numpy as np
import matplotlib.pyplot as plt

# %%
top_country_counts = np.array(Counter(chain(*article_countries.values())).most_common(20))

# %%
fig, ax = plt.subplots(figsize=(6, 4))

ax.barh(top_country_counts[:, 0][::-1], [int(i) for i in top_country_counts[:, 1]][::-1])
ax.set_xlabel('N Papers')
ax.set_ylabel('Country')
plt.show()

# %%
query = """SELECT A.article_id, A.fos_id 
FROM arxiv_article_fields_of_study A
LEFT JOIN arxiv_articles B ON A.article_id = B.id
WHERE B.article_source = 'cord'
"""
article_fos = pd.read_sql(query, engine)

# %%
article_fos_lookup = defaultdict(list)

for art_id, fos_id in zip(article_fos['article_id'], article_fos['fos_id']):
    article_fos_lookup[art_id].append(fos_id)

# %%
query = "SELECT * FROM mag_fields_of_study"
mag_fos = pd.read_sql(query, engine)

# %%
fos_lookup = mag_fos.set_index('id').to_dict('index')


# %%
def get_fos_at_level(fos_ids, min_level, max_level, field='name'):
    fos_features = []
    for fos_id in fos_ids:
        fos = fos_lookup[fos_id]
        if (fos['level'] <= max_level) and (fos['level'] >= min_level):
            if field in fos:
                fos_features.append(fos[field])
            else:
                fos_features.append(fos_id)
    return fos_features   


# %%
article_disciplines = {k: get_fos_at_level(v, 1, 1) for k, v in article_fos_lookup.items()}

# %%
from sklearn.feature_extraction.text import CountVectorizer


# %%
def preprocessor(text):
    return text

def tokenizer(text):
    return text


# %%
cv = CountVectorizer(preprocessor=preprocessor, tokenizer=tokenizer)
article_disciplines_cv = cv.fit_transform(article_disciplines.values())

cv = CountVectorizer(preprocessor=preprocessor, tokenizer=tokenizer)
article_countries_cv = cv.fit_transform(pd.Series(article_countries))

# %% [markdown]
# DateTime
# Complicated indexing

# %%
article_country_disc = pd.concat([pd.Series(article_countries), pd.Series(article_disciplines)], axis=1).dropna()

# %%
disc_cv = CountVectorizer(preprocessor=preprocessor, tokenizer=tokenizer)
article_disciplines_cv = disc_cv.fit_transform(article_country_disc[1])

country_cv = CountVectorizer(preprocessor=preprocessor, tokenizer=tokenizer)
article_countries_cv = country_cv.fit_transform(article_country_disc[0])

# %%
country_discipline_df = pd.DataFrame(
    article_disciplines_cv.T.dot(article_countries_cv).todense(), 
    columns=country_cv.get_feature_names(),
    index=disc_cv.get_feature_names())

# %%
countries_top = country_discipline_df.columns[country_discipline_df.sum() >= 50]
country_discipline_df = country_discipline_df[countries_top]

# %%
eu_countries = [
  {"isoCode": "AT", "name": "Austria"},
  {"isoCode": "BE", "name": "Belgium"},
  {"isoCode": "BG", "name": "Bulgaria"},
  {"isoCode": "HR", "name": "Croatia"},
  {"isoCode": "CY", "name": "Cyprus"},
  {"isoCode": "CZ", "name": "Czech Republic"},
  {"isoCode": "DK", "name": "Denmark"},
  {"isoCode": "EE", "name": "Estonia"},
  {"isoCode": "FI", "name": "Finland"},
  {"isoCode": "FR", "name": "France"},
  {"isoCode": "DE", "name": "Germany"},
  {"isoCode": "GR", "name": "Greece"},
  {"isoCode": "HU", "name": "Hungary"},
  {"isoCode": "IE", "name": "Ireland, Republic of (EIRE)"},
  {"isoCode": "IT", "name": "Italy"},
  {"isoCode": "LV", "name": "Latvia"},
  {"isoCode": "LT", "name": "Lithuania"},
  {"isoCode": "LU", "name": "Luxembourg"},
  {"isoCode": "MT", "name": "Malta"},
  {"isoCode": "NL", "name": "Netherlands"},
  {"isoCode": "PL", "name": "Poland"},
  {"isoCode": "PT", "name": "Portugal"},
  {"isoCode": "RO", "name": "Romania"},
  {"isoCode": "SK", "name": "Slovakia"},
  {"isoCode": "SI", "name": "Slovenia"},
  {"isoCode": "ES", "name": "Spain"},
  {"isoCode": "SE", "name": "Sweden"},
]

eu_alpha_2 = [c['isoCode'] for c in eu_countries]

# %%
country_discipline_norm_df = country_discipline_df.divide(country_discipline_df.sum(axis=0), axis=1)

# %%
import seaborn
from skbio.diversity.alpha import shannon

# %%
from pycountry

# %%
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE

# %%
discipline_diversity = country_discipline_norm_df.apply(shannon, axis=0)

# %%
tsne = TSNE(n_components=2)
tsne_vecs = tsne.fit_transform(country_discipline_norm_df.T)

plt.scatter(tsne_vecs[:, 0], tsne_vecs[:, 1], c=discipline_diversity)

# %%
import pycountry

# %%
pycountry.countries.get(name='brazil')

# %%
comparator_countries = eu_alpha_2 + ['US', 'RU', 'CN', 'CA', 'IN', 'BR', 'GB']

# %%
eu_diversity = discipline_diversity[discipline_diversity.index.intersection(comparator_countries)].sort_values()
colours = ['C0' if c in eu_alpha_2 else 'C1' for c in eu_diversity.index]

fig, ax = plt.subplots(figsize=(12, 4))
ax.scatter(eu_diversity.index, eu_diversity.values, c=colours)
ax.axhline(discipline_diversity.mean(), linestyle='--', color='gray')
ax.set_xlabel('Country')
ax.set_ylabel('Shannon Diversity Index')
plt.show()

# %% [markdown]
# - All EU countries are high diversity countries in comparison to the rest of the world.
# - On a similar diversity with respect to comparator countries.
# - Russia has the most diverse research profile

# %%
country_discipline_norm_df['RO'].sort_values()[-5:]

# %%
country_discipline_norm_df['HU'].sort_values()[-5:]

# %%
country_discipline_norm_df['IT'].sort_values()[-5:]

# %%
top_journals = ['bioRxiv', 'PLoS One', 'BMJ', 'Int J Environ Res Public Health', 'Sci Rep', 'Nature', 'Lancet',
               'Cureus']
articles_top = articles[articles.journal_ref.isin(top_journals)]

# %%
articles_top_set = (articles_top
                    .set_index('id')
                    .join(pd.Series(article_countries, name='countries'))
                    .dropna(subset=['countries']))

# %%
journals = pd.get_dummies(articles_top_set['journal_ref'])

# %%
cv = CountVectorizer(preprocessor=preprocessor, tokenizer=tokenizer)
top_article_countries_cv = cv.fit_transform(articles_top_set['countries'])

# %%
countries_by_journal = pd.DataFrame(top_article_countries_cv.T.dot(journals),
                                   index=cv.get_feature_names(),
                                   columns=journals.columns)

# %%
countries_by_journal_norm = countries_by_journal.divide(countries_by_journal.sum(axis=1), axis=0).loc[comparator_countries].sort_values(by='bioRxiv')

# %%
fig, ax = plt.subplots(figsize=(12, 4))
(countries_by_journal_norm * 100).plot.bar(stacked=True, ax=ax)
ax.set_xlabel('Country')
ax.set_ylabel('% Papers in Top Journals')
plt.show()

# %%
from operator import itemgetter

# %%
from sklearn.metrics import silhouette_samples

# %%
country_discipline_norm_df = country_discipline_norm_df.T

# %%
s = silhouette_samples(
    country_discipline_norm_df.T, 
    labels=[0 if c in eu_alpha_2 else 1 for c in country_discipline_norm_df.T.index],
    metric='cosine'
)

# %%
pd.Series(s, index=country_discipline_norm_df.T.index)[eu_alpha_2].sort_values().plot.barh()

# %%
svd = TruncatedSVD(n_components=30)
svd_vecs = svd.fit_transform(country_discipline_norm_df.T)

tsne = TSNE(n_components=2)
tsne_vecs = tsne.fit_transform(svd_vecs)

# %%
fig, ax = plt.subplots(figsize=(12, 9))
plt.scatter(tsne_vecs[:, 0], tsne_vecs[:, 1], 
            c=['C0' if c in eu_alpha_2 else 'C1' for c in country_discipline_norm_df.T.index],
            s=50,
            alpha=.7)

for point, country in zip(tsne_vecs, country_discipline_norm_df.T.index):
    if country in eu_alpha_2:
        ax.text(point[0]+.1, point[1]+.1, country)

# %%
pycountry.countries.get(alpha_2='QA')

# %%
seaborn.clustermap(1 - pairwise_distances(country_discipline_norm_df.T, metric='cosine'))

# %%

# %%
from itertools import combinations

# %%
edges = defaultdict(int)

for group in article_countries.values():
    for combo in combinations(sorted(group), 2):
        edges[combo] += 1

# %%
import networkx as nx

# %%
g = nx.Graph()

g.add_weighted_edges_from([(k[0], k[1], v) for k, v in edges.items() if v > 100])

# %%
nx.draw(nx.maximum_spanning_tree(g), node_size=20)

# %%
nx.cluster.clustering(g, weight='weight')

# %%
nx.draw(g, node_size=10)

# %%
edges[('GB', 'GB')]

# %%
np.sum(np.array([len(set(e)) for e in article_countries.values()]) == 1) / len(article_countries)

# %%
