---
bibliography: ./sdg_bibliography.bib
---


## Mapping research related to the Sustainable Development Goals {#subsec:sdg}

In our data science pilots we explored themes of diversity and mission oriented R&I. One emerging theme from the discussions and events around these pilots was the degree to which research funded by the European Commission was addressing broader issues of sustainability. Following this, we developed a programme of work focused on identifying and mapping research efforts related to the United Nations Sustainable Development Goals.

Social and environmental sustainability are covered by many competing definitions and frameworks that have emerged from a variety of geographic, political and policy settings. Sustainability itself is a highly contested term, yielding an array of interpretations depending on the individual or institution that invokes it. To make an attempt at mapping sustainability issues being tackled by R&I activities, we chose to use the framework offered by the United Nations Sustainable Development Goals (SDGs). This was mentioned specifically by stakeholders who attended our pilot events and also has the advantages that it is internationally recognised and agreed as one universal set of objectives for countries to achieve. The individual goals that it contains targets relate to a broad spectrum of sustainability dimensions and attempts are made to measure progress against these for the majority of countries on an annual basis [@sachs_sustainable_2021]. 

Many institutions, inlcuding the United Nations itself, have asserted the role that R&I can play in acheiving the Goals [@borowiecki_oecd_2019, @unstats_sustainable_2021, @nature_science_ sdgs_2021]. At the same time, researchers, particularly in the field of science and technology studies, have stressed the role of institutions in directing R&I efforts towards sustainability goals [@XXX]. In response, there are now a number of academic and commercial initiatives that aim to identify research activities that are related to the Goals [@XX]. Here, we describe our own attempt to map the research that is relevant to the SDGs, with specific attention paid to the European context and the values openness and trust that are centred in this programme of work. We will additionally present some analyses that highlight interesting aspects of the related research activity and draw comparisons between our approach and the existing initiatives.

The solution that we designed for identifying SDG related research relies on a supervised machine learning approach. Ultimately, we constructed a model that is trained to take the title and abstract of a project as inputs and predict whether the it is related to any of the first sixteen SDGs independently.[^1] In this way, the model attempts to detect whether a project is related to one Goal, several, or none at all. Several other pieces of work in this space aim to identify the goals using expert defined keywords or complicated boolean queries, however these can never exhaustively capture all of the concepts embedded within a complex concept such as a SDG. State-of-the-art natural language processing (NLP) techniques on the other hand are able to infer the semantic meaning of words and phrases that are not included in the training data, meaning that the final algorithm is able to capture a more comprehensive range of expressions that may relate to one of the Goals.

[^1]: Our model was not trained to predict Goal 17. Partnerships for the Goals as it was considered that in the context of R&I, this related more to the operational and organisational characteristics of a project than the content of the project.

The capabilities of modern machine learning methods do not necessarily give licence to allow loose definitions of the concepts that are trying to be learned. It remains highly important to define the semantic space that captures the concepts of interest, as the initial attempt to create a classification model in this project demonstrates.

The first methodology that was tested used training data scraped from the web. Guided by the programme's aim to use novel data sources, we identified two websites that contained articles labelled with SDGs. The first of these was the RELX SDG Resource Centre which describes itself as a website that "showcases the latest in science, law, business, events and more that can help drive forward the SDGs" [@relx_about]. SDG Knowledge Hub by the International Institute for Sustainable Development, which describes itself as "an online resource center for news and commentary regarding the implementation of the United Nations’ 2030 Agenda for Sustainable Development and the Sustainable Development Goals (SDGs)" [@iisd_about]. On both sites, each article contains original articles or other content including publication summaries, event descirptions, news items or policy highlights, with each item being tagged with one or more SDGs. After scraping and filtering content (e.g. removing very short article stubs) and their associated SDG labels from these websites, we obtained a dataset of over 10,000 labelled articles.

A model pipeline that encoded


- web data
- didn't work great
- 

At Nesta More than 20 employees took part in the data annotation exercise over several weeks. A dedicated messaging channel was established



- defining the SDGs
- related vs contributing
- annotation with codebooks

Challenges of annotation
