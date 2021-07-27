---
title: EURITO Final Report
author:
    - Juan Mateos-Garcia
    - George Richardson
    - Eva Senra
    - Ramón Xifré
    - Agzam Idrissov
    - Knut Blind
    - Chantale Tippet
date:
    - 30 July 2021
figPrefix:
  - "Figure"
  - "Figures"
tblPrefix:
  - "table"
  - "tables"
secPrefix:
  - "Section"
  - "sections"
bibliography: bibliography.bib
geometry: 
  - margin=3cm
toc-depth: 2
toc: true
secnumdepth: 3
numbersections: True
fontsize: 11pt
---
# Introduction

In EURITO (EU Relevant, Inclusive and Trusted Indicators) we explored the opportunities and challenges for developing indicators based on novel data sources and data science methods with the goal of informing Research and Innovation (R&I) policy. 

Our starting point was that the data revolution - increasing availability of a high volume of data generated at high velocity and with high variety, and of computational methods and tools to extract insights from it [@mayer2013big] - could generate a more detailed, timely and comprehensive view of the economy and its evolution which is relevant for R&I policymakers. Significant concerns around representativity, transparency and ethics are however standing in the way of their wider adoption [@bakhshi2016new]. 

We sought to tackle these issues by following a process that began with a scoping phase where we engaged policymakers to identify gaps in the R&I evidence base and indicator toolkit that could be addressed with new data and methods. We then explored opportunities to address those gaps through data science pilots and scaled up data collection and analysis in those areas that offered greatest promise / feasibility. The resulting indicators were validated qualitatively and quantitatively and distributed through reports and papers, open datasets and interactive visualisations. All our code was made openly available for others to inspect and build on.^[We have released code related to specific papers in individual github repositories. The [Eurito indicators repository](https://www.github.com/nesta_uk/eurito_indicators) contains the code used in the Covid-19 analysis and visualisation frontend.]

This final report describes our activities and outputs throughout the project with a focus on our indicator production methods and results. In those cases where these efforts have resulted in peer-reviewed publications, working papers or EURITO deliverables, we summarise key results and refer the readers to those documents for additional detail. In other cases - particularly the analysis of EU R&I funding data to measure activities related to Sustainable Development Goals, and our analysis of R&I activities related to Covid-19, we provide extensive information about the methods we used to produce and validate indicators.

[@sec:ind1] describes indicator development before Covid-19, This includes our policy scoping activities, the results of our exploratory pilots, our Artificial Intelligence (AI) mapping programme, and our analysis of relatedness to Sustainable Development Goals in a EU R&I funding corpus. 

[@sec:covid] presents the results of our analysis of a programme of research and indicator development about R&I activities related to Covid-19 initiated with the onset of the pandemic. This includes analyses of EU R&I funding data, preprints and peer-reviewed publications and outputs of research projects. 

[@sec:val] describes how we validated our indicators. 

[@sec:outputs] outlines the outputs of the project.

[@sec:org] discusses the organisational implications of our analysis: what activities are required to encourage the adoption of new indicators in the R&I evidence system, and what changes - in terms of capabilities, orgaanisation and culture - are required if R&I agencies are going to realise the value of novel data sources and methods.

[@sec:conclusion] concludes.

# Indicator development before Covid-19 {#sec:ind1}

## Pilot related work and outputs {#subsec:pilots}

In the scoping phase of the project we organised two workshops in Brussels involving representatives from the European Commission, member states and the research and data community. These workshops were attended by XXX people. Our goal with them was to ensure that our indicator development activities were focused on policy-relevant areas, and to assess which features of R&I indicators might encourage or constrain their adoption. The workshops led to the identification of eight areas for further exploration through data science pilots. The detailed results of each pilot are available in **deliverable X** [TO_ADD]. In the list that follows we also indicate additional peer reviewed publications and working papers based on these pilots.

1. **Emerging technology ecosystems:** Here we analysed data about research funding, publications and startups to map activities related to emerging technologies with a case study focusing on Artificial Intelligence.
2. **Advanced research funding analytics:** We explored potential indicators capturing diversity, complexity and novelty in reseaarch with the goal of informing funding decisions. 
3. **Mission-driven innovation indicators:** We developed indicators about the level of activity in R&I missions with an application to the UK government mission to deploy Artificial Intelligence to improve the prevention, diagnisis and treatment of chronic diseases [@mateos2019mapping].
4. **Gender diversity in R&I workforce:** We explored the potential for using semantic analyses of researcher names in order to generate measures of diversity in R&I activities.
5. **Nowcasting R&D investment:** We assessed the feasibility of nowcasting R&D investment using timely web proxies.
6. **Technological transformations:** We developed methods to identify structural changes in technological fields with an application to the biofuel sector [@parraguez2020quantifying].
7. **Knowledge Flow:** We analysed the OpenAIRE database of research outputs to map networks of research collaboration and identify highly productive institutions and projects.
8. **Standards:** We investigated the potential use of data about standard adoption from the International Standards Organisation (ISO) and whether web data might be used to measure the adoption of standards in business [@mirtsch2020exploring].

Pilot results were discussed with policymakers in a follow-up event attended by XX people and an internal session with the Commission and we used the resulting feedback to select four areas to scale up with additional data collection and validation. These areas were:

1. Analysis of emerging technologies including levels of activity, changes in composition of activity and measures of diversity
2. Analysis of innovation activities related to sustainability
3. Use of advanced analytics to analyse research funnding and its impact
4. Nowcasting / triangulation of traditional innovation indicators with indicators emerging from the analyses above

In the rest of this section we summarise the results of the scaled-up analyses of emerging technologies (which became the EURITO AI mapping programme) and the results of our machine learning analysis to classify EC-funded research projects into the Sustainable Development Goals that they relate to. The Advanced Funding Analytics scale-up pivoted towards an analysis of the R&I response to Covid-19 with results that we present in [@sec:covid]. 

## AI research mapping programme {#subsec:ai}

Our AI mapping programme of work built on ideas and methods developed in the pilots about emerging technologies and technological transformation with the goal of developing indicators about levels of activity in AI research, its evolution composition and geography, and diversity in its workforce and the technologies that are explored. 

This research agenda was informed by the perception of a 'geopolitical race' in AI research and concerns about corporate dominance over its trajectory with potentially negative repercussions for equality, fairness and sustainability [@cave2018ai, @bender2021dangers]. In order to address it, we developed a data pipeline that automatically collects and enrichs data about preprints (a widely used channel for the dissemination of AI research) with information about participating institutions and their geography (see [@klinger2021deep] for additional details) and implemented semantic analysis methods to identify AI papers and particular techniques in the resulting corpus. This programme of work yielded the following outputs:

1. **Deep Learning, Deep Change** [@klinger2021deep]: In this paper we analysed preprint's abstracts in order to identify documents related to Deep Learning (DL), a computational technique that has played a central role in recent advances in AI research. Having done this, we analysed to which extent deep learning papers displayed the features of a General Purpose Technology (GPT) in computer science research [@bresnahan1995general], its geography and the local drivers of the emergence of deep learning research clusters. Our analysis supports the idea that deep learning research "behaves like a GPT", with growing levels of activity, diffusion into many different areas of computer science, and overrepresentation amongst highly cited works wherever it is adopted. We also evidenced the emergence of China as an 'AI superpower', with rapid growth in activity and relative specialisation in deep learning research. Finally, we incorporated into our analysis data about technology company activity from CrunchBase, a startup database in order to study the extent to which co-location between deep learning research clusters and industrial activities in related sectors contribute to the development of competitive deep learning clusters. The results of this investigation support the idea that DL research clusters benefit from proximity to industry clusters that provide opportunities for deployment and follow-up innovation. 
2. **Gender diversity in AI research** [@stathoulopoulos2019gender]. Here, we analysed the same corpus that we had developed for *Deep Learning, Deep Change* with the goal of measuring levels of gender diversity in AI research and its evolution, differences across countries and fields and the degree to which research involving more female AI researcher focuses on different topics compared to less diverse AI research efforts. Our analysis confirmed the existence of a persistent 'gender gap' in AI research: only around a quarter of papers involve at least one female researcher, and only around 12% of AI researchers are female. Rather concerningly, female participation in AI research has barely increased since the 1990s in relative terms. We also detect important differences between fields and countries in their level of female participation in AI research. More specifically, applied areas like health as well as research about the social impacts of AI tend to have a higher degree of female involvement while computer science and machine learning disciplines have less diversity. Nordic countries and the Netherlands tend to have more female participation in AI research than countries in Eastern Europe. 
3. **A Narrowing of AI research**[@klinger2020narrowing]. In this paper we analyse the evolution of the composition of AI research and its link with increasing corporate participation and influence in the field. This work is motivated by the idea that powerful deep learning techniques favoured by large technology companies are close to becoming the "dominant design" in AI research, and that this could be a source of concern given increasing evidence about the limitations of these techniques and their risks for fairness and sustainability [@marcus2018deep, @bender2021dangers]. In order to conduct our analysis, we deploy topic modelling methods that allow us to quantify the composition of AI research and use the outputs to calculate measures of thematic diversity derived from the economics, environmental science and innovation studies literature [@stirling2007general, @weitzman1992diversity, @page20101]. Our analysis suggests that there has been stagnation and even decline in the thematic diversity of AI research as deep learning techniques able to analyse large volumes of unstructured data come into the scene. We also show that the research profiles of private sector companies with high levels of participation of AI research are thematically narrower than research in academia, suggesting that the private sector might be playing a role in the loss of diversity in AI research.

Together, these analyses illustrate the potential of novel semantic methods and diversity metrics for shedding light on the trajectory of AI R&D and its dynamics, and to inform R&I policies to mitigate its risks for inclusion and sustainability thus ensuring that this powerful technology evolves in a direction that maximises its public benefits. The pipelines that we have developed also yield a collection of indicators about levels of AI and deep learning research activity and about the level of adoption of AI methods in Covid-19 related research (a topic we come back to in [@sec:covid].

## Sustainable Development Goal Modelling {#subsec:sdg}

# Covid-19 R&D response {#sec:covid}

The Covid-19 pandemic has a complex relationship with R&I: on the one hand, it has elicited a massive R&D&I response culminating in the development of effective vaccines. On the other, it has impacted on how science itself is conducted, creating a digital shift in scientific collaboration and communication and the adoption of open modes for dissemination of results, data and software code [@paunov2020science]. In this section we present the results of our own analysis of research funding and publication activities connected with Covid-19, which we have undertaken as part of a 'pandemic pivot' in response to the pandemic. 

We undertook a short consultation round with EC policymakers and identified a number of areas where semantic methods could add value to those indicators that are already available. We go through them in turn, describing the context for our research, the methods we used, the indicators we developed and their interpretation.

## CORDIS analysis {#subsec:cordis}

We begin with an analysis of the European Commission funded response to Covid-19 under the rubric of the Horizon 2020 Framework Programme.^[We recognise that this does not capture all EC contributions to the R&I fight against the pandemic, for example through the activities of the European Research Council and EC contributions to the [Innovative Medicines Initiative](https://www.imi.europa.eu/apply-funding/closed-calls/imi2-call-21).] There were three areas of interest in this analysis: 

1. What is the composition of the EC response to Covid-19?
2. What are the levels of national participation in different streams of research to tackle Covid-19?
3. What other research activities have taken place in the past / are currently taking place which are (semantically) similar to Covid-19 and might capture investments in societal preparedness and resilience against the current and future crises. 
4. Is there a link between previous research activities in areas related to Covid-19 and current levels of participation in the Covid-19 effort?
5. What is the topical composition of the response to Covid-19 and how does it compare with the wider portfolio of EC-funded research?

### Sentence embedding and document clustering

Our starting point is a labelled dataset including a list of 569 H2020 projects that have been either commissioned directly in response to Covid-19 or pivoted their activities to make their outputs more relevant for tackling Covid-19 (EURITO was itself in this latter category). 

An initial analysis of this corpus suggested that the categories used to label the data ("direct actions", "health emergency" and "resilience") were too broad to inform this analysis so we undertook additionl semantic and clustering analyses. In order to do this, we created a vector representation of Covid-19 related projects in the Cordis data using Specter, a language model trained on scientific research by the Allen Institute for AI [@cohan2020specter] and available from the sentence-transformers Python library [@reimers-2019-sentence-bert]. These high-dimensional vector representations capture semantic similarities and differences between documents that can be used to cluster them. 

We did this robustly through an ensemble clustering approach that draws on a variety of clustering algorithms and parametre sets (including number of clusters) initialised multiple times in order to draw a graph were documents are nodes connected by the number of times they are classified by a clustering algorithm in one of our iterations. We then decomposed the networks into its consituent communities using the Louvain algorithm, which looks for a partition of the network which maximises its modularity [@que2015scalable]. The result could be seen as a "consensus" assignment based on the ensemble of clusters. We implement multiple runs of the community detection algorithm and find that any given pair of documents that are placed together in a cluster once are placed in the same cluster 95% of the times.

This clustering strategy yields six Covid-19 related research streams within the EC response to the pandemic. They are:

1. Diagnosis and prevention (9%)
2. Public health (26%)
3. Systems and networks (12%)
4. Policy (22%)
5. Products and services (11%)
6. Biotechnology (19%)

We present some (randomly) drawn sample projects inside each category in [@tbl:cord] and the distribution of cluster research areas in the categories initially used to classify the data in [@fig:covid_levels]. They illustrate the discplinary and domain expanse of the EC response to Covid-19 and the high degree of thematic crossover in the initial labels we obtained, motivating the use of the more granular and informative categories generated by our cluster analysis.

| Cluster                           | Examples                                                                                                                                                                                  |
|:--------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Cluster 3: Policy                 | Expecting the unexpected and know how to respond                                                                                                                                          |
|                                   |  The First Responder (FR) of the Future: a Next Generation Integrated Toolkit (NGIT) for Collaborative Response, increasing protection and augmenting operational capacity                |
|                                   |  Next generation of AdVanced InteGrated Assessment modelling to support climaTE policy making                                                                                             |
| Cluster 1: Public health          | Development of an intelligent and multi-hospital end-to-end surgical process management system                                                                                            |
|                                   |  COVID-19 infections - Remote Early Detection                                                                                                                                             |
|                                   |  QUantitative Imaging Biomarkers Medicine                                                                                                                                                 |
| Cluster 2: Systems and Networks   | ACCIA programme to foster mobility of researchers with a focus in applied research and technology transfer                                                                                |
|                                   |  Growth Welfare Innovation Productivity                                                                                                                                                   |
|                                   |  New issues in the Analysis of Business Cycles                                                                                                                                            |
| Cluster 5: Biotechnology          | Simulating the dynamics of viral evolution: A computer-aided study toward engineering effective vaccines                                                                                  |
|                                   |  Leveraging Pharmaceutical Sciences and Structural Biology Training to develop 21st Century Vaccines                                                                                      |
|                                   |  Integration of herpesvirus into telomeres: From the mechanism of genome integration and mobilization to therapeutic intervention                                                         |
| Cluster 0: Diagnosis & prevention | SIGNIA: An innovative drug discovery platform for rapid identification and validation of antimicrobial applications in available pharmaceutical resources and drugs open for repurposing. |
|                                   |  AI-based infectious diseases diagnosis in seconds                                                                                                                                        |
|                                   |  conect4children (COllaborative Network for European Clinical Trials For Children)                                                                                                        |
| Cluster 4: Products and Services  | EpiShuttle: Isolation and Transportation of Infectious Disease Patients                                                                                 |
|                                   |  EUropean Vital Medical Supplies and Equipment Resilient and Reliable Repurposing Manufacturing as a Service NetworK for Fast PAndemic Reaction                                           |
|                                   |  Additive Manufacturing of 3D Microfluidic MEMS for Lab-on-a-Chip applications                                                                                                            |
: Examples of CORDIS projects in the research cluster we have identified {#tbl:cord}

![Distribution of covid research clusters over initial labels in the data](final_report_deck/png/covid_levels_clusters.png){#fig:covid_levels}

### National participation and representation in the Covid-19 response

Having classified Covid-response projects in different research clusters, we move to analyse the levels of participation of different countries in the EU Covid-19 research response. 

[@fig:country_spec] presents, for the top 15 countries in terms of project coordination activity, their levels of 'relative specialisation' in a Covid-19 research cluster (in the horizontal axis) and their overall volume of activity (size of the points).^[Levels of specialisation are calculated using a relative comparative advantage index that normalises the share of activity in a cluster in each country by the overall share of activity accounted by that country also including non-Covid 19 related research and restricting our analysis after 2019, when most of the Covid-19 projects started [@balassa1965trade]. Scores above one represent relative positive specialisation in a topic, an scores below one represent relative underspecialisation.] We sort the countries by their average specialisation over all Covid-19 research clusters so that countries at the top of the chart are overrepresented in the Covid-19 research response while countries towards the bottom are underrepresented.

![Level of relative specialisation and overall volumes of activity in streams of the EC Covid-19 research response by nationality of project coordinator](final_report_deck/png/cordis_specialisation.png){#fig:country_spec}

This analysis shows that Israel, Ireland, the Netherlands and Germany are overrepresented in the Covid-19 research respone while Spain, the United Kingdom and Switzerland are underrepresented. We also find that some countries are overrepresented in some Covid-19 research areas and underrepresented in others. For instance, Sweden has a high degree of activity in the Covid-18 research clusters (six times higher than we might have expected given its overall levels of coordination of H2020 projects after 2019). Italy is overrrepresented in Products and Services and Systems and Networks and generally underrepresented in other areas.

There are many possible explanations for these international differences including different levels of agility in national R&I systems, variation in the availability of alternative funding sources (e.g. national or philanthropic) for Covid-19 reponse projects, or presence of established capabilities and networks enabling countries to rapidly coordinate Covid-19 projects in particular areas. We will explore the last mechanism in further detail below.

## Measuring semantic relatedness to Covid-19 research









## Research publications {#subsec:paper}

## Funder benchmarking {#subsec:funder}

## OpenAIRE analysis {#subsec:openaire}

# Validation {#sec:val}

# Outputs {#sec:outputs}

# Organisational implications {#sec:org}

# Conclusions {#sec:conclusion}



# Conclusions


    