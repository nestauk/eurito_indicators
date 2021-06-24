# -*- coding: utf-8 -*-
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

# %% [markdown]
# ### Exploratory analysis

# %% [markdown]
# Exploratory analysis of the covid research project tracker data. Looking at:

# %% [markdown]
# #### Focus on EU projects
# - Looking at projects where the funding body is EC or the countries are EU ✔
# - Count of projects by funding body (from EU countries)
# - Which countries produced the most projects? ✔
#     - Over time ✔
# - Collaborating countries – which countries worked together most on projects
# - Which counties received the most funding? ✔
# - Which research area receives the most funding?
#
# #### Comparison of EU verses non-EU projects
# - Count of projects
# - Total amount spent / awarded
# - Over time
# - Top modelling
#     - Looking at the topic present in EU compared to non-EU

# %%
# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import country_converter as coco
import itertools as it
from collections import Counter
from countrygroups import EUROPEAN_UNION
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import sklearn
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pickle

# %%
import eurito_indicators
from eurito_indicators.getters import Get_file as gf

# %%
project_directory = eurito_indicators.PROJECT_DIR

# %%
# Load df
research = gf.read_excel_file()

# %% [markdown]
# #### Data quality check

# %%
research.head(1) # Look at first row

# %%
research.shape

# %%
data_types = pd.DataFrame(research.dtypes, columns=['Data Type'])

# %%
percent_missing = research.isnull().sum() * 100 / len(research)
missing_values = pd.DataFrame({'column_name': research.columns, 'percent_missing': percent_missing})

# %%
missing_values.sort_values('percent_missing', ascending=True, inplace=True)

# %%
plt.rcParams["figure.figsize"] = (16,10)

# %%
plt.plot(missing_values.column_name, missing_values.percent_missing) 
plt.xticks(rotation=90)
plt.title('Percentage missing per column')
plt.xlabel('Columns')
plt.ylabel('Percentage')
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Count-of-missing-values.svg", format='svg', dpi=1200)
plt.show()

# %%
unique_values = pd.DataFrame(columns=['Unique Values'])
for row in list(research.columns.values): unique_values.loc[row] = [research[row].nunique()]

# %%
dq_report = data_types.join(missing_values).join(unique_values)

# %%
dq_report.head(1)

# %%
list(research.columns.values)

# %% [markdown]
# ### EU analysis
# - Looking at projects where the funding body is EC or the countries are EU
# - Count of projects by funding body (from EU countries)
# - Which countries produced the most projects?
#     - Over time
# - Collaborating countries – which countries worked together most on projects
# - Which counties received the most funding?
# - Which research area receives the most funding?

# %% [markdown]
# ###### EC funded
# Only 50 cases

# %%
EC = research.loc[research['Funder(s)'].str.startswith('EC', na=False)]
EC['Funder(s)'].value_counts()

# %%
print("Unique values: ",research['Funder(s)'].nunique())
print(research['Funder(s)'].value_counts().sort_values(ascending=False).head(10)) # Top ten funders by project count

# %% [markdown]
# ###### Countries

# %%
# 1.3% missing
research['Country/ countries research is being are conducted'].isnull().sum()/len(research)*100

# %%
# Recode as blank
research['Country/ countries research is being are conducted'] = research['Country/ countries research is being are conducted'].fillna('')

# %%
countries = []
for i in research['Country/ countries research is being are conducted']:
    i = i.split(',')
    i = ['United Kingdom' if x=='UK' else x for x in i]
    i = ['United States' if x=='USA' else x for x in i]
    countries.append(i)
research['Countries-list'] = countries
research['Countries-list'].head(10)

# %%
research['Countries clean'] = coco.convert(names=countries, to='name_short', not_found='Unknown')
research['Continent'] = coco.convert(names=countries, to = 'continent', not_found='Unknown')

# %%
research['Continent clean2'] = research['Continent'].str.join(', ')
research['Continent'] = research['Continent'].str.strip('[]')
research['Continent'] = research['Continent'].fillna(research['Continent clean2'])
research['Continent'] = research['Continent'].map(lambda x: [i.strip() for i in x.split(",")])

research['Countries clean2'] = research['Countries clean'].str.join(', ')
research['Countries clean'] = research['Countries clean'].str.strip('[]')
research['Countries clean'] = research['Countries clean'].fillna(research['Countries clean2'])
research['Countries clean'] = research['Countries clean'].map(lambda x: [i.strip() for i in x.split(",")])

# %%
research.drop(['Countries clean2', 'Continent clean2'], axis=1, inplace=True)

# %%
cont_count = dict(Counter(it.chain(*map(set, research['Continent'].tolist()))).most_common()) # Count of continents
cont_count

# %%
plt.rcParams["figure.figsize"] = (10,7)
plt.rcParams.update({'font.size': 12})

colors = ['#3754b3','#ed5a58','#3754b3','#3754b3','#3754b3','#3754b3']

plt.bar(cont_count.keys(), cont_count.values(), width=0.8, color=colors) # Plot
plt.title('Count of Research Projects by Continent')
plt.xlabel('Continents')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Count-of-research-projects-by-continent.svg", format='svg', dpi=1200)
plt.show()

# %%
countries_count = Counter(it.chain(*map(set, research['Countries clean'].tolist()))) # Count of continents
countries_count_top = dict(countries_count.most_common(10))
plt.bar(countries_count_top.keys(), countries_count_top.values(),color='#3754b3') # Plot
plt.title('Top 10 countries by project count')
plt.xlabel('Country')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Top-ten-countries-by-project-count.svg", format='svg', dpi=1200)
plt.show()

# %% [markdown]
# ###### EU Countries

# %%
eu = EUROPEAN_UNION.names

# %%
eu.append('United Kingdom')


# %%
# True where two lists overlap
def lists_overlap(a, b):
    eu_countries = list(set(a).intersection(b))
    eu_true = bool(set(a) & set(b))
    return eu_countries, eu_true


# %%
eu_bool= []
eu_countries_list = []
for c in research['Countries clean']:
    eu_countries, eu_true = lists_overlap(c, eu)
    eu_bool.append(eu_true)
    eu_countries_list.append(eu_countries)
research['eu_country'] = eu_bool
research['eu_countries'] = eu_countries_list

# %%
# research.to_excel('test22.xlsx', index=False) # Temp check results - delete later

# %%
research['eu_countries']

# %%
EU = research.loc[research['eu_country']==True].copy()

# %%
eu_count = Counter(it.chain(*map(set, EU['eu_countries'].tolist())))
eu_count.most_common(5)

# %%
plt.rcParams["figure.figsize"] = (12,8)

# %%
countries_count = Counter(it.chain(*map(set, EU['eu_countries'].tolist())))
countries_count = dict(sorted(countries_count.items(), key=lambda pair: pair[1], reverse=True))
plt.bar(countries_count.keys(), countries_count.values(), color='#3754b3') # Plot
plt.title('Count of Research Projects by EU countries (Including UK)')
plt.xlabel('Country')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Count-project-eu-countries.svg", format='svg', dpi=1200)
plt.show()

# %%
EU['Start date clean']= pd.to_datetime(EU['Start Date'], errors='coerce' )

# %%
# 23% missing
EU['Start date clean'].isnull().sum()/len(research)*100

# %%
eu_time = EU[EU['Start date clean'].notna()].copy()
eu_time.sort_values(by='Start date clean', inplace=True)
eu_time = eu_time[['Start date clean','eu_countries']]
eu_time = eu_time.explode('eu_countries').reset_index(drop=True)
eu_time.set_index('Start date clean', inplace=True)

# %%
eu_time.head(2)

# %%
grouper = eu_time.groupby([pd.Grouper(freq='1M'), 'eu_countries'])
grouper = grouper['eu_countries'].count().unstack()
grouper.replace(np.nan, 0, inplace=True)

# %%
grouper.head(2)

# %%
plt.rcParams["figure.figsize"] = (15,10)
fig = plt.figure()
grouper.plot(ax=plt.gca())

# %%
grouper_covid = grouper[grouper.index >'2020-03-30']

# %%
fig = plt.figure()
grouper_covid.plot(ax=plt.gca())
plt.title('Timeseries: EU country by project count from March 30th 2020')
plt.xlabel('Time')
plt.ylabel('Project count')
plt.show()

# %%
fig = plt.figure()
grouper_covid[['United Kingdom','Germany','France','Spain','Netherlands']].plot()
plt.title('Timeseries: Top 5 EU countries (inc UK) by project start date from March 30th 2020')
plt.xlabel('Time')
plt.ylabel('Project count')
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Timeseries-top-5-eu-project-start-date.svg", format='svg', dpi=1200)
plt.show()

# %% [markdown]
# <b> Amount awarded by funder + EU country </b>

# %%
EU.head(1)

# %%
eu_awarded = EU[EU['Amount Awarded converted to USD'].notna()].copy()

# %%
eu_awarded['Amount Awarded converted to USD'] = eu_awarded.loc[:, 'Amount Awarded converted to USD'].replace({'\$':''}, regex = True)
eu_awarded['Amount Awarded converted to USD'].replace(',','', regex=True, inplace=True)
eu_awarded['Amount Awarded converted to USD'] = eu_awarded['Amount Awarded converted to USD'].astype(str).astype(float)
eu_awarded['Amount Awarded converted to USD'] = eu_awarded['Amount Awarded converted to USD'].astype(int)

# %%
eu_awarded_c = eu_awarded[['eu_countries','Amount Awarded converted to USD']].explode('eu_countries').reset_index(drop=True)

# %%
top_countries_awarded = eu_awarded_c.groupby(['eu_countries']).sum().reset_index().sort_values(by='Amount Awarded converted to USD',ascending=False).head(10)

# %%
plt.rcParams["figure.figsize"] = (10,7)
plt.rcParams.update({'font.size': 12})

# %%
plt.xticks(range(len(top_countries_awarded['Amount Awarded converted to USD'])), top_countries_awarded['eu_countries'])
plt.xticks(rotation=90)
plt.xlabel('Countries')
plt.ylabel('Total $ awarded')
plt.title('Top ten EU Countries (inc UK) by total funds awarded')
plt.bar(range(len(top_countries_awarded['Amount Awarded converted to USD'])), top_countries_awarded['Amount Awarded converted to USD'], color='#3754b3') 
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Top-EU-Countries-total-funds-awarded.svg", format='svg', dpi=1200)
plt.show()

# %%
funders_top_awarded = eu_awarded.groupby(['Funder(s)']).sum().reset_index().sort_values(by='Amount Awarded converted to USD',ascending=False).head(10)

# %%
plt.xticks(range(len(funders_top_awarded['Amount Awarded converted to USD'])), funders_top_awarded['Funder(s)'])
plt.xticks(rotation=90)
plt.xlabel('Funders')
plt.ylabel('Total $ awarded')
plt.title('Top ten funding bodies by funded ammount awarded (EU countries only)')
plt.bar(range(len(funders_top_awarded['Amount Awarded converted to USD'])), funders_top_awarded['Amount Awarded converted to USD'], color='#3754b3') 
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Top-funders-total-funds-awarded.svg", format='svg', dpi=1200)
plt.show()

# %% [markdown]
# #### Comparison of EU verses non-EU projects
# - Count of projects
# - Total amount spent / awarded
# - Over time
# - Top modelling
#     - Looking at the topic present in EU compared to non-EU

# %% [markdown]
# #### Topic modelling

# %%
my_stopwords = nltk.corpus.stopwords.words('english')
word_rooter = nltk.stem.snowball.PorterStemmer(ignore_stopwords=False).stem
my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@'

# cleaning master function
def clean_text(text, bigrams=False):
    text = text.lower() # lower case
    text = re.sub('['+my_punctuation + ']+', ' ', text) # strip punctuation
    text = re.sub('\s+', ' ', text) #remove double spacing
    text = re.sub('([0-9]+)', '', text) # remove numbers
    text_token_list = [word for word in text.split(' ')
                            if word not in my_stopwords] # remove stopwords

    text_token_list = [word_rooter(word) if '#' not in word else word
                        for word in text_token_list] # apply word rooter
    if bigrams:
        text_token_list = text_token_list+[text_token_list[i]+'_'+text_token_list[i+1]
                                            for i in range(len(text_token_list)-1)]
    text = ' '.join(text_token_list)
    return text


# %%
research['clean_text'] = research['Project Title'] + ' ' + research['Abstract']
research['clean_text'] = research['clean_text'].astype(str).apply(clean_text)

# %%
research[['clean_text','Project Title']].head(1)

# %%
# the vectorizer object will be used to transform text to vector form
vectorizer = CountVectorizer(max_df=0.9, min_df=25, token_pattern='\w+|\$[\d\.]+|\S+')

# apply transformation
tf = vectorizer.fit_transform(research['clean_text']).toarray()

# tf_feature_names tells us what word each column in the matric represents
tf_feature_names = vectorizer.get_feature_names()

# %%
number_of_topics = 20
model = LatentDirichletAllocation(n_components=number_of_topics, random_state=0)

# %%
model.fit(tf)


# %%
def display_topics(model, feature_names, no_top_words):
    topic_dict = {}
    for topic_idx, topic in enumerate(model.components_):
        topic_dict["Topic %d words" % (topic_idx)]= ['{}'.format(feature_names[i])
                        for i in topic.argsort()[:-no_top_words - 1:-1]]
        topic_dict["Topic %d weights" % (topic_idx)]= ['{:.1f}'.format(topic[i])
                        for i in topic.argsort()[:-no_top_words - 1:-1]]
    return pd.DataFrame(topic_dict)


# %%
no_top_words = 10
display_topics(model, tf_feature_names, no_top_words)

# %% [markdown]
# #### Bertopic package

# %%
from bertopic import BERTopic

# %%
res_text = research['clean_text'].to_list()

# %%
# Look at dynamic topic modelling
# https://github.com/MaartenGr/BERTopic

# %%
topic_model = BERTopic(embedding_model="paraphrase-MiniLM-L6-v2", language="english", calculate_probabilities=True)
topics, probabilities = topic_model.fit_transform(res_text)

# %%
topic_model.save(f"{project_directory}/outputs/topic_model.digital")

# %%
#loaded_topic_model = BERTopic.load(f"{project_directory}/outputs/topic_model.digital")
#loaded_topic_model.get_topic_info()

# %%
probabilities

# %%
topic_info = topic_model.get_topic_info()
topic_info.head(9)

# %%
topic_model.visualize_barchart()

# %%
topic_model.visualize_topics()

# %%
topic_model_all = topic_model.visualize_topics()

# %%
pickle.dump(topic_model_all, open(f"{project_directory}/outputs/figures/Covid_research_tracker/BERTopic_model_all_data.pickle", 'wb')) 

# %%
research['Topic'] = topics

# %%
research = research.merge(topic_info, how='left', on='Topic')

# %%
europe= []
for c in research['Continent']:
    _, eu_true = lists_overlap(c, ['Europe'])
    europe.append(eu_true)
research['europe'] = europe

row= []
for c in research['Continent']:
    _, row_true = lists_overlap(c, ['America','Asia','Africa','Oceania'])
    row.append(row_true)
research['rest_of_world'] = row

# %%
research['europe'] = research['europe']*1
research['rest_of_world'] = research['rest_of_world']*1

# %%
research.head(2)

# %%
research['count'] = 1
all_projects = research[['Name','count']]
all_projects = all_projects.loc[all_projects['Name']!='-1_immun_individu_decis_treatment']
all_projects = all_projects.groupby(['Name'], as_index=False)['count'].sum().reset_index(drop=True)
all_projects = all_projects.sort_values(by=['count'], ascending=False).head(20)
all_projects.set_index('Name',inplace=True,drop=True)

# %%
all_projects.plot(kind='bar', color='#3754b3', legend=False) # Plot
plt.title('Number of research projects per topic (top 20)')
plt.xlabel('Topic')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Number-project-per-topic.svg", format='svg', dpi=1200)
plt.show()

# %%
countries = research[['Countries clean','Name']]
countries = countries.loc[countries['Name']!='-1_immun_individu_decis_treatment']

# %%
uk_bool= []
for c in countries['Countries clean']:
    _, uk_true = lists_overlap(c, ['United Kingdom'])
    uk_bool.append(uk_true)
countries['UK'] = uk_bool
countries['UK'] = countries['UK']*1

# %%
uk = countries.groupby(['Name'], as_index=False)['UK'].sum().reset_index(drop=True)
uk_top = uk.sort_values(by=['UK'], ascending=False).head(10)
uk_top.set_index('Name',inplace=True,drop=True)

# %%
uk_top.plot(kind='bar')

# %%
continents = research.loc[research['Name']!='-1_immun_individu_decis_treatment']

# %%
continents = continents[['Name', 'europe', 'rest_of_world']]

# %%
continents = continents.groupby(['Name'], as_index=False)['europe', 'rest_of_world'].sum().reset_index(drop=True)

# %%
continents['All'] = continents['europe'] + continents['rest_of_world']

continents['europe'] = (continents['europe'] / continents['europe'].sum()) * 100
continents['rest_of_world'] = (continents['rest_of_world'] / continents['rest_of_world'].sum()) * 100

continents_top = continents.sort_values(by=['All'], ascending=False).head(10)

# %%
continents_top.drop('All', axis=1, inplace=True)

# %%
continents_top.set_index('Name',inplace=True,drop=True)

# %%
continents_top.head(10)

# %%
plt.rcParams["figure.figsize"] = (12,8)
plt.rcParams.update({'font.size': 12})

# %%
continents_top.plot(kind= 'bar' , secondary_y= 'rest_of_world', legend='TRUE',
                    ax=None, mark_right=False, rot=90, color=['#3754b3','#ed5a58'])
plt.title('Percentage of projects assigned to the top ten topics')
plt.xlabel('Area')
plt.ylabel('Percentage')
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Topics-europe-rest-of-world.svg", format='svg', dpi=1200)
plt.show()

# %% [markdown]
# #### Testing active projects

# %%
active_projects = research[['Start date clean','Name']]

# %%
melt = df.melt(id_vars=['id', 'age', 'state'], value_name='date').drop('variable', axis=1)
melt['date'] = pd.to_datetime(melt['date'])

melt = melt.groupby('id').apply(lambda x: x.set_index('date').resample('d').first())\
           .ffill()\
           .reset_index(level=1)\
           .reset_index(drop=True)

# %% [markdown]
# ##### Plotting topics by start date

# %%
res_time = research.copy()
res_time['Start date clean']= pd.to_datetime(res_time['Start Date'], errors='coerce' )
res_time = res_time[res_time['Start date clean'].notna()].copy()

# %%
res_time = res_time[['Start date clean','Name']]
res_time.shape

# %%
res_time = res_time.loc[res_time['Name']!='-1_respiratori_immun_drug_target']
res_time.reset_index(drop=True, inplace=True)
res_time['Month-year'] = pd.to_datetime(res_time['Start date clean']).dt.strftime('%m-%Y')
res_time['Month-year']= pd.to_datetime(res_time['Month-year'], errors='coerce' )
res_time['count'] = res_time.groupby(['Month-year','Name'])['Name'].transform('count')
res_time.drop_duplicates(inplace=True)
res_time_pivot = res_time.pivot_table(index='Month-year', columns='Name', values='count')
res_time_pivot.replace(np.nan, 0, inplace=True)
res_time_pivot = res_time_pivot[res_time_pivot.index >'2020-03-30']

# %%
plt.rcParams["figure.figsize"] = (15,10)
plt.rcParams.update({'font.size': 12})

# %%
topic_info.head(9)

# %%
fig = plt.figure()
res_time_pivot[['0_rna_protein_coronavirus_viral','1_mental_anxieti_psycholog_depress','2_children_child_parent_youth','3_mask_face_protect_visor','4_vaccin_antigen_immun_antibodi']].plot()
plt.title('Timeseries of project start date by topic from March 30th 2020')
plt.xlabel('Time')
plt.ylabel('Project count')
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Timeseries-project-start-date-by-topic.svg", format='svg', dpi=1200)
plt.show()

# %%
res_time.head(10)

# %% [markdown]
# #### Dynamic Topic Modelling

# %%
# Group by month then quarterly....

# %%
res_time = research.copy()

# %%
res_time['Start date clean']= pd.to_datetime(res_time['Start Date'], errors='coerce' )
res_time = res_time[res_time['Start date clean'].notna()].copy()
res_time['clean_text'] = res_time['Project Title'] + ' ' + res_time['Abstract']
res_time['clean_text'] = res_time['clean_text'].astype(str).apply(clean_text)

# %%
#res_time['Start date clean'] = res_time['Start date clean'].clip(lower=pd.Timestamp('2020-03-01'))

# %%
res_time2 = res_time[['clean_text', 'Start date clean']]
res_time2['Month-year'] = pd.to_datetime(res_time2['Start date clean']).dt.strftime('%m-%Y')
res_time2 = res_time2.groupby(['Month-year'])['clean_text'].apply(lambda x: ' '.join(x)).reset_index()

# %%
res_text = res_time2['clean_text'].to_list()
timestamps = res_time2['Month-year'].to_list()

# %% [markdown]
# #### Old version

# %%
res_time = research.copy()
res_time['Start date clean']= pd.to_datetime(res_time['Start Date'], errors='coerce' )
res_time = res_time[res_time['Start date clean'].notna()].copy()

res_time['clean_text'] = res_time['Project Title'] + ' ' + res_time['Abstract']
res_time['clean_text'] = res_time['clean_text'].astype(str).apply(clean_text)

res_time.set_index('Start date clean', inplace=True)
#res_time = res_time[res_time.index >'2020-03-30']
res_time.reset_index(inplace=True)
res_time.head(1)

# %%
res_text = res_time['clean_text'].to_list()
timestamps = res_time['Start date clean'].to_list()

# %%
topic_model = BERTopic(verbose=True)
topics, _ = topic_model.fit_transform(res_text)

# %%
topics_over_time = topic_model.topics_over_time(res_text, topics, timestamps, nr_bins=20)

# %% [markdown]
# Where start date is after March 2020

# %%
topic_model.visualize_topics_over_time(topics_over_time, top_n_topics=6)
