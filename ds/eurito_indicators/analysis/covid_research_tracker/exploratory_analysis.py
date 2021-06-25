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
from bertopic import BERTopic
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
research.shape # df size

# %%
data_types = pd.DataFrame(research.dtypes, columns=['Data Type']) # Data types
percent_missing = research.isnull().sum() * 100 / len(research) # Percent missing
missing_values = pd.DataFrame({'column_name': research.columns, 'percent_missing': percent_missing})
missing_values.sort_values('percent_missing', ascending=True, inplace=True)


# %%
def df_plot(plot, size_x, size_y, rotate, title, x_label, y_label, filename):
    plt.rcParams["figure.figsize"] = (size_x, size_y)
    plot 
    plt.xticks(rotation=rotate)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/"+filename, format='svg', dpi=1200)
    plt.show()


# %%
plot = plt.plot(missing_values.column_name, missing_values.percent_missing)
df_plot(plot, 16, 10, 90, 'Percentage missing per column', 'Columns', 'Percentage', 'Count-of-missing-values.svg')

# %%
unique_values = pd.DataFrame(columns=['Unique Values'])
for row in list(research.columns.values): unique_values.loc[row] = [research[row].nunique()]

# %%
dq_report = data_types.join(missing_values).join(unique_values)

# %%
dq_report.head(1)

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
research.drop(['Countries clean2', 'Continent clean2'], axis=1, inplace=True)

# %%
cont_count = dict(Counter(it.chain(*map(set, research['Continent'].tolist()))).most_common()) # Count of continents
cont_count

# %%
plt.rcParams.update({'font.size': 12})
colors = ['#3754b3','#ed5a58','#3754b3','#3754b3','#3754b3','#3754b3']
plot = plt.bar(cont_count.keys(), cont_count.values(), width=0.8, color=colors) # Plot
df_plot(plot, 10, 7, 0, 'Count of Research Projects by Continent', 'Continents', 'Count', 'Count-of-research-projects-by-continent.svg')

# %%
countries_count = Counter(it.chain(*map(set, research['Countries clean'].tolist()))) # Count of continents
countries_count_top = dict(countries_count.most_common(10))

# %%
plot = plt.bar(countries_count_top.keys(), countries_count_top.values(),color='#3754b3') # Plot
df_plot(plot, 10, 7, 90, 'Top 10 countries by project count', 'Country', 'Count', 'Top-ten-countries-by-project-count.svg')

# %% [markdown]
# ###### EU Countries

# %%
eu = EUROPEAN_UNION.names # EU list
eu.append('United Kingdom') # Adding United Kingdom


# %%
# True where country list has eu country in it
def lists_overlap(a, b):
    eu_countries = list(set(a).intersection(b))
    eu_true = bool(set(a) & set(b))
    return eu_countries, eu_true


# %%
# Apply above function to countries column
eu_bool= []
eu_countries_list = []
for c in research['Countries clean']:
    eu_countries, eu_true = lists_overlap(c, eu)
    eu_bool.append(eu_true)
    eu_countries_list.append(eu_countries)
research['eu_country'] = eu_bool
research['eu_countries'] = eu_countries_list

# %%
EU = research.loc[research['eu_country']==True].copy() # segment df by eu countries

# %%
# Count of eu countries
countries_count = Counter(it.chain(*map(set, EU['eu_countries'].tolist())))
countries_count = dict(sorted(countries_count.items(), key=lambda pair: pair[1], reverse=True))

# %%
plot = plt.bar(countries_count.keys(), countries_count.values(), color='#3754b3') # Plot # Plot
df_plot(plot, 12, 8, 90, 'Count of Research Projects by EU countries (Including UK)', 'Country','Count', 'Count-project-eu-countries.svg')

# %%
EU['Start date clean']= pd.to_datetime(EU['Start Date'], errors='coerce' ) # Remove errors start date
EU['Start date clean'].isnull().sum()/len(research)*100 # 23% missing

# %%
# Index by start time
eu_time = EU[EU['Start date clean'].notna()].copy()
eu_time.sort_values(by='Start date clean', inplace=True)
eu_time = eu_time[['Start date clean','eu_countries']]
eu_time = eu_time.explode('eu_countries').reset_index(drop=True)
eu_time.set_index('Start date clean', inplace=True)

# %%
# Group by 1 month count
eu_time = eu_time.groupby([pd.Grouper(freq='1M'), 'eu_countries'])
eu_time = eu_time['eu_countries'].count().unstack()
eu_time.replace(np.nan, 0, inplace=True)

# %%
plt.rcParams["figure.figsize"] = (15,10)
fig = plt.figure()
eu_time.plot(ax=plt.gca()) # Plot timeseries

# %%
eu_time_covid = eu_time[eu_time.index >'2020-03-30']

# %%
fig = plt.figure()
eu_time_covid.plot(ax=plt.gca())
plt.title('Timeseries: EU country by project count from March 30th 2020')
plt.xlabel('Time')
plt.ylabel('Project count')
plt.show()

# %%
fig = plt.figure()
eu_time_covid[['United Kingdom','Germany','France','Spain','Netherlands']].plot()
plt.title('Timeseries: Top 5 EU countries (inc UK) by project start date from March 30th 2020')
plt.xlabel('Time')
plt.ylabel('Project count')
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Timeseries-top-5-eu-project-start-date.svg", format='svg', dpi=1200)
plt.show()

# %% [markdown]
# <b> Amount awarded by funder + EU country </b>

# %%
eu_awarded = EU[EU['Amount Awarded converted to USD'].notna()].copy() # Remove NA

# %%
# Clean amount awarded
eu_awarded['Amount Awarded converted to USD'] = eu_awarded.loc[:, 'Amount Awarded converted to USD'].replace({'\$':''}, regex = True)
eu_awarded['Amount Awarded converted to USD'].replace(',','', regex=True, inplace=True)
eu_awarded['Amount Awarded converted to USD'] = eu_awarded['Amount Awarded converted to USD'].astype(str).astype(float)
eu_awarded['Amount Awarded converted to USD'] = eu_awarded['Amount Awarded converted to USD'].astype(int)

# %%
# By country
eu_awarded_c = eu_awarded[['eu_countries','Amount Awarded converted to USD']].explode('eu_countries').reset_index(drop=True)

# %%
# Top countries by ammount awarded
top_countries_awarded = eu_awarded_c.groupby(['eu_countries']).sum().reset_index().sort_values(by='Amount Awarded converted to USD',ascending=False).head(10)

# %%
plt.xticks(range(len(top_countries_awarded['Amount Awarded converted to USD'])), top_countries_awarded['eu_countries'])
plt.rcParams.update({'font.size': 12})
plot = plt.bar(range(len(top_countries_awarded['Amount Awarded converted to USD'])), top_countries_awarded['Amount Awarded converted to USD'], color='#3754b3') 
df_plot(plot, 10, 7, 90, 'Top ten EU Countries (inc UK) by total funds awarded', 'Country', 'Total $ awarded', 'Top-EU-Countries-total-funds-awarded.svg')

# %%
funders_top_awarded = eu_awarded.groupby(['Funder(s)']).sum().reset_index().sort_values(by='Amount Awarded converted to USD',ascending=False).head(10)

# %%
plt.xticks(range(len(funders_top_awarded['Amount Awarded converted to USD'])), funders_top_awarded['Funder(s)'])
plot = plt.bar(range(len(funders_top_awarded['Amount Awarded converted to USD'])), funders_top_awarded['Amount Awarded converted to USD'], color='#3754b3') 
df_plot(plot, 10, 7, 90, 'Top ten funding bodies by funded ammount awarded (EU countries)', 'Funders', 'Total $ awarded', 'Top-EU-Countries-total-funds-awarded.svg')

# %% [markdown]
# ### Topic modelling

# %%
my_stopwords = nltk.corpus.stopwords.words('english')
word_rooter = nltk.stem.snowball.PorterStemmer(ignore_stopwords=False).stem
my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@'

# Text cleaning function
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

# %% [markdown]
# #### LDA topic modelling

# %%
# the vectorizer object will be used to transform text to vector form
vectorizer = CountVectorizer(max_df=0.9, min_df=25, token_pattern='\w+|\$[\d\.]+|\S+')

# apply transformation
tf = vectorizer.fit_transform(research['clean_text']).toarray()

# tf_feature_names tells us what word each column in the matric represents
tf_feature_names = vectorizer.get_feature_names()

# %%
# Set topic number, define model and fit to vector
number_of_topics = 20
model = LatentDirichletAllocation(n_components=number_of_topics, random_state=0)
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
# Display results with top 10 words per topic
no_top_words = 10
display_topics(model, tf_feature_names, no_top_words)

# %% [markdown]
# #### Bertopic package

# %%
res_text = research['clean_text'].to_list()

# %%
topic_model = BERTopic(embedding_model="paraphrase-MiniLM-L6-v2", language="english", calculate_probabilities=True)
topics, probabilities = topic_model.fit_transform(res_text)

# %%
# Save model
topic_model.save(f"{project_directory}/outputs/topic_model.digital")

# %%
# load pre run model
topic_model.save(f"{project_directory}/outputs/topic_model.digital")
topic_model = BERTopic.load(f"{project_directory}/outputs/topic_model.digital")
topic_model.get_topic_info().head(7)

# %%
topic_info = topic_model.get_topic_info()

# %%
#topic_model.visualize_distribution(probabilities[60]) # This doesn't seem to work well

# %%
topic_model.visualize_barchart()

# %%
topic_model.visualize_topics()

# %%
# Save topic model visual to load later
topic_model_all = topic_model.visualize_topics()
pickle.dump(topic_model_all, open(f"{project_directory}/outputs/figures/Covid_research_tracker/BERTopic_model_all_data.pickle", 'wb')) 

# %%
print(len(topics), research.shape) # Check topic / document size matches up

# %%
# Add topics to rearch df
research['Topic'] = topics
research = research.merge(topic_info, how='left', on='Topic')

# %%
# Add columns to indicate if the project has countries in europe and / or the rest of the world
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
# Change from True/False to 1/0
research['europe'] = research['europe']*1
research['rest_of_world'] = research['rest_of_world']*1

# %%
# Group df by topics
research['count'] = 1
all_projects = research[['Name','count']]
all_projects = all_projects.loc[all_projects['Name']!='-1_respiratori_hospit_treatment_individu']
all_projects = all_projects.groupby(['Name'], as_index=False)['count'].sum().reset_index(drop=True)
all_projects = all_projects.sort_values(by=['count'], ascending=False).head(20)
all_projects.set_index('Name',inplace=True,drop=True)

# %%
plot = all_projects.plot(kind='bar', color='#3754b3', legend=False) # Plot
df_plot(plot, 10, 7, 90, 'Number of research projects per topic (top 20)', 'Topic', 'Count', 'Number-project-per-topic.svg')

# %%
countries = research[['Countries clean','Name']]
countries = countries.loc[countries['Name']!='-1_respiratori_hospit_treatment_individu']

# %%
# Country list contains UK
uk_bool= []
for c in countries['Countries clean']:
    _, uk_true = lists_overlap(c, ['United Kingdom'])
    uk_bool.append(uk_true)
countries['UK'] = uk_bool
countries['UK'] = countries['UK']*1

# %%
# Top 10 topics in UK
uk = countries.groupby(['Name'], as_index=False)['UK'].sum().reset_index(drop=True)
uk_top = uk.sort_values(by=['UK'], ascending=False).head(10)
uk_top.set_index('Name',inplace=True,drop=True)

# %%
uk_top.plot(kind='bar') # Plot

# %%
# European countries compared to rest of world
continents = research.loc[research['Name']!='-1_respiratori_hospit_treatment_individu']
continents = continents[['Name', 'europe', 'rest_of_world']]
continents = continents.groupby(['Name'], as_index=False)['europe', 'rest_of_world'].sum().reset_index(drop=True)
continents['All'] = continents['europe'] + continents['rest_of_world']

continents['europe'] = (continents['europe'] / continents['europe'].sum()) * 100
continents['rest_of_world'] = (continents['rest_of_world'] / continents['rest_of_world'].sum()) * 100

continents_top = continents.sort_values(by=['All'], ascending=False).head(10)
continents_top.drop('All', axis=1, inplace=True)
continents_top.set_index('Name',inplace=True,drop=True)

# %%
continents_top.head(10)

# %%
plot = continents_top.plot(kind= 'bar' , secondary_y= 'rest_of_world', legend='TRUE',
                           ax=None, mark_right=False, rot=90, color=['#3754b3','#ed5a58'])
df_plot(plot, 12, 8, 90, 'Percentage of projects assigned to the top ten topics', 'Area', 
        'Percentage','Topics-europe-rest-of-world.svg')

# %% [markdown]
# #### Testing active projects

# %% [markdown]
# Come back to: https://stackoverflow.com/questions/57334097/pandas-convert-dataframe-with-start-and-end-date-to-daily-data

# %%
#active_projects = research[['Start date clean','Name']]

# %%
#melt = df.melt(id_vars=['id', 'age', 'state'], value_name='date').drop('variable', axis=1)
#melt['date'] = pd.to_datetime(melt['date'])

#melt = melt.groupby('id').apply(lambda x: x.set_index('date').resample('d').first())\
#           .ffill()\
#           .reset_index(level=1)\
#           .reset_index(drop=True)

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
res_time = res_time.loc[res_time['Name']!='Topics-europe-rest-of-world.svg']
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
fig = plt.figure()
res_time_pivot[['0_protein_rna_coronavirus_replic','1_vaccin_antibodi_immunogen_immun','2_mental_stress_depress_psycholog','3_children_child_parent_mental','4_ltc_palli_carer_care', '5_mask_face_visor_protect']].plot()
plt.title('Timeseries of project start date by topic from March 30th 2020')
plt.xlabel('Time')
plt.ylabel('Project count')
plt.tight_layout()
plt.savefig(f"{project_directory}/outputs/figures/Covid_research_tracker/Timeseries-project-start-date-by-topic.svg", format='svg', dpi=1200)
plt.show()

# %%
research.to_excel('temp-research.xlsx', index=False) # Save df

# %%
# Save topics
with open("topics.txt", "wb") as fp:
    pickle.dump(topics, fp)

# %%
np.save("probabilities.npy", probabilities) # Save probabilities
