---
title: EURITO Final Report
author:
    - Juan Mateos-Garcia
    - George Richardson
    - Agzam Idrissov
    - Eva Senra
    - Ramón Xifré
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

The Covid-19 pandemic has a complex relationship with R&I: on the one hand, it has elicited a massive R&D&I response culminating in the creation of effective vaccines. On the other, it has impacted on how science itself is conducted, creating a digital shift in scientific collaboration and communication and the wider adoption of open modes for dissemination of results, data and software code [@paunov2020science]. 

In this section we present the results of our own analysis of research funding and publication activities connected with Covid-19, which we have undertaken as part of a 'pandemic pivot'. 

This began with a short consultation round with EC policymakers where we identified several areas where semantic methods could add value to those indicators that are already available. 

We go through them in turn, describing the context for our research, the methods we used, the indicators we developed and their interpretation.

## CORDIS analysis {#subsec:cordis}

We begin with an analysis of the European Commission funded response to Covid-19 under the rubric of the Horizon 2020 Framework Programme using the CORDIS open grant dataset, which includes information about H2020 funded projects and the organisations participating in them.^[We recognise that this does not capture all EC contributions to the R&I fight against the pandemic, for example through the activities of the European Research Council and EC contributions to the [Innovative Medicines Initiative](https://www.imi.europa.eu/apply-funding/closed-calls/imi2-call-21).] We are interested in the following questions: 

1. What is the composition of the EC response to Covid-19?
2. What are the levels of national participation in different streams of research to tackle Covid-19?
3. What other research activities have taken place in the past / are currently taking place which are (semantically) similar to Covid-19 and might capture investments in societal preparedness and resilience against the current and future crises. 
4. Is there a link between previous research activities in areas related to Covid-19 and current levels of participation in the Covid-19 effort?
5. What is the topical composition of the response to Covid-19 and how does it compare with the wider portfolio of EC-funded research?

### Sentence embedding and document clustering

Our starting point is a labelled dataset including a list of 569 H2020 projects that have been either commissioned directly in response to Covid-19 or pivoted their activities to make their outputs more relevant for tackling Covid-19 (EURITO was itself in this last category). 

An initial analysis of this corpus suggests that the categories used to label the data ("direct actions", "health emergency" and "resilience") are too broad and overlapping to inform this analysis so we undertake additionl semantic and clustering analyses. We create a vector representation of Covid-19 related projects in the Cordis data using Specter, a language model trained on scientific research by the Allen Institute for AI [@cohan2020specter] and available from the sentence-transformers Python library [@reimers-2019-sentence-bert]. These high-dimensional vector representations capture semantic similarities and differences between document abstracts that we can use to cluster them. 

We do this robustly through an ensemble clustering approach that draws on a variety of clustering algorithms and parametre sets (including number of clusters) initialised multiple times in order to build a graph where documents are nodes connected by edges with a weight set to the number of times they are classified in the same cluster by one of our clustering iterations. We then decompose the graph into its consituent communities using the Louvain algorithm, which searches for a partition of the network which maximises its modularity [@que2015scalable]. The result can be seen as a "consensus" assignment based on the ensemble of clusters. We run the community detection algorithm multiple times and find that any given pair of documents placed together in a cluster once are placed in the same cluster 95% of the times.

This clustering strategy yields six Covid-19 related research streams / clusters within the EC response to the pandemic. They are:

1. Diagnosis and prevention (9%)
2. Public health (26%)
3. Systems and networks (12%)
4. Policy (22%)
5. Products and services (11%)
6. Biotechnology (19%)

We present some (randomly) drawn sample projects from each category in [@tbl:cord] and the distribution of cluster research areas in the categories initially used to classify the data in [@fig:covid_levels]. They illustrate the discplinary and application range of the EC response to Covid-19 and the high degree of thematic crossover in the initial labels we obtained, motivating the use of the more granular and informative categories generated by our cluster analysis.

| Cluster                           | Examples                                                                                                                                                                                  |
|:--------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
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

Having classified Covid-response projects in different research clusters, we move to analyse the levels of national participation in the EU Covid-19 research response. 

[@fig:country_spec] presents, for the top 15 countries by level of project coordination activity, their 'relative specialisation' in each Covid-19 research cluster (in the horizontal axis) and their overall volume of activity (size of the points).^[We measure specialisation using a Relative Comparative Advantage (RCA) index that normalises the share of activity in a cluster in each country by the overall share of activity accounted for by that country, also including non-Covid 19 related research and restricting our analysis after 2019, comprising most of the Covid-19 activity [@balassa1965trade]. RCA scores above one represent relative positive specialisation in a topic, an scores below one represent relative underspecialisation.] We sort the countries by their mean specialisation over all Covid-19 research clusters so that countries at the top of the chart tend to be overrepresented in the coordination of the Covid-19 research response while countries towards the bottom are underrepresented.

![Level of relative specialisation and overall volumes of activity in streams of the EC Covid-19 research response by nationality of project coordinator](final_report_deck/png/cordis_specialisation.png){#fig:country_spec}

This analysis shows that Israel, Ireland, the Netherlands and Germany are overrepresented in the Covid-19 research response while Spain, the United Kingdom and Switzerland are underrepresented. We also find that some countries are overrepresented in some Covid-19 research areas and underrepresented in others. For instance, Sweden has a high degree of activity in the Covid-19 biotechnology research cluster (six times higher than we might have expected given its overall levels of coordination of H2020 projects after 2019). Italy is overrrepresented in Products and Services and Systems and Networks and generally underrepresented in other areas.

There are many possible explanations for these international differences including different degreses of agility in national R&I systems, variation in the availability of alternative funding sources (e.g. national or philanthropic) for Covid-19 reponse projects across countries, or presence of established capabilities and networks enabling countries to rapidly coordinate Covid-19 projects in particular areas. We will explore the last mechanism in further detail below.

## Measuring semantic relatedness to Covid-19 projects in the CORDIS corpus

We use the Specter language model to create vector representations of H2020 projects that were not included in our Covid-19 labelled dataset. This allows us to identify projects that are semantically similar (close in vector space) to Covid-19 research. We use the resulting information in two ways:

1. To measure levels of EC investment in projects related to societal / economic / health emergency preparedness _before and during_ the pandemic.
2. Measure established research capabilities in research areas related to the pandemic in different countries _before it happened_ which might explain subsequent differences in the levels of national coordination of Covid-19 projects.

We create a semantic signature / "centroid" for each Covid-19 research cluster - the median of the vector representations for all projects classified in a research cluster - and measure the distance of all non-Covid-19 related projects to that semantic signature using the cityblock (Manhattan or L1) distance metric [melter1987some]. 

[@fig:dist_distr] presents the distributions of distances to those clusters signatures from projects inside each Covid-research cluster (in orange) and outside (in blue), 

![Distribution of distances to research cluster centroid. Blue bars represent documents outside of the cluster and orange bars represent observations in a cluster. The green vertical lines represent a distance to a Covid-19 cluster which is two standard deviations lower than the mean for non-Covid-19 projects.](final_report_deck/png/dist_distribution.png){#fig:dist_distr}

The figure shows, unsurprisingly, that projects that are part of a Covid-19 cluster tend to be closer to its centroid than those outside. 

We also see notable differences between Covid-19 research clusters. In the case of cluster 0 (Diagnosis and Prevention) and cluster 5 (Biotechnology) there is a strong degree of separation between Covid-19 and non-Covid-19 projects while cluster 1, 3 and 4 (public health, policy and products and services) present a strong overlap suggesting fuzzier semantic boundaries between both categories and the risk of false positives if we do not adjust the threshold to define relatedness to a Covid-19 research cluster carefully. In order to do this, we draw on a measure of dispersion in the distribution of distances to each of the Covid-19 clusters: any non-Covid project that is two standard deviations closer to the centroid of a Covid-19 research cluster than the mean is defined as "semantically similar" to that cluster. As the green vertical lines in {#fig:dist_distr} show, this thresold is more demanding for fuzzier Covid-19 research clusters.

In total, we identify 6,244 projects related or 'close' to various Covid-19 research clusters. We present some (randomly drawn) examples in table [@#tbl:prox_ex]. It shows that projects related to health and biomedical Covid-19 research clusters are highly related or adjacent to pandemic use cases (e.g. use of AI methods to analyse CT scans, development of testing devices, RNA analysis in plant infections) while the relevance of policy, networking and product and services projects is somewhat looser (tackling energy poverty in urban settings, development of lightweight materials).  

| Cluster                           |    n | Examples                                                                                                                                                      |
|:----------------------------------:|-----:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Cluster 0: Diagnosis & prevention |  467 | AI-based Chest CT Analysis Enabling Rapid Covid Diagnosis And Prognosis, (2020)                                                                               |
|                                   |      |  A Simple Blood Test To Monitor Disease Progression In Patients Undergoing Cancer Therapy, (2015)                                                             |
|                                   |      |  Ser-col; From Finger To Laboratory; Personalized And Automated Serum Collection For Laboratory Diagnostics, (2019)                                           |
| Cluster 1: Public health          |  680 | Pulsehale - A Breakthrough Treatment  For COPD, (2021)                                                                                                      |
|                                   |      |  The Clinical Flexible Analyzer- A New Generation Ivd Testing Device Aimed To Increase The Competitiveness Of Local Healthcare Vs. Large Laboratories, (2018) |
|                                   |      |  Lipiddrive - Lipidomics Cloud Computing Platform And App, (2017)                                                                                             |
| Cluster 2: Systems and Networks   |  980 | Scientific Large-scale Infrastructure For Computing/communication Experimental Studies Starting Community, (2021)                                           |
|                                   |      |  Enhancing Innovation And Key Account Management By Sme2eu, (2019)                                                                                            |
|                                   |      |  Bringing Firmware To The Next Step, (2016)                                                                                                                     |
| Cluster 3: Policy                 | 1671 | Law As Vehicle For Social Change: Mainstreaming Non-extractive Economic Practices, (2020)                                                                     |
|                                   |      |  Improving Health, Wellbeing And Equality By Evidenced-based Urban Policies For Tackling Energy Poverty, (2021)                                               |
|                                   |      |  Urban Terrorism In Europe (2004-2019): Remembering, Imagining, And Anticipating Violence, (2019)                                                             |
| Cluster 4: Products and Services  |  874 | Open Access Single Entry Point For Scale-up Of Innovative Smart Lightweight Composite Materials And Components, (2019)                                        |
|                                   |      |  Smart And Interoperable Thermal Network System Development, (2015)                                                                                           |
|                                   |      |  Development Of A New Gearbox Without Lubricants For Low OM Costs, Higher Efficiency, And Oiless Applications, (2016)                                         |
| Cluster 5: Biotechnology          | 1572 | Genome-wide Analysis Of RNA And Protein Interacting Profiles During A Plant Virus Infection, (2015)                                                           |
|                                   |      |  Control Of Leishmaniasis, From Bench To Bedside And Community, (2015)                                                                                        |
|                                   |      |  Personalised Pancreatic Cancer Vaccination Therapy Derived From Autologous Tumor Cells And Neoantigens, (2018)                                               |
: Examples of research projects that are semantically related to Covid-19 research clusters {#tbl:prox_ex}

[@fig:related_trend] presents the evolution of activity in Covid-19 related projects (excluding projects in the initial labelled set). It shows relative stability in the number of projects in Covid-19 / societal emergency areas over time, although we note some spikes of activity that might be related to specific funding calls in 2019 and 2021 which could be an focus of interest for future research.

![Evolution of activity in Covid-19 related research areas](final_report_deck/png/relatedness_trends.png){#fig:related_trend}

### Measuring national capabilities in Covid-19 related areas before the pandemic.

We use the measures of relatedness to identify corpora of projects related to various Covid-19 research clusters _before the pandemic_. We then calculate relative specialisation of countries in each of those research clusters based on the number of projects that they coordinated within them, which we consider to be a proxy for the presence of established capabilities and networks in those research areas. Are countries with such capabilities more active when the pandemic arrives?

One issue here is that our measures of specialisation might be contingent on the Covid-19 relatedness thresholds that we select. We assess their robustness by estimating the levels of national specialisation in a Covid research cluster under different thresholds (between 1.5 and 2.5 standard deviations closer to the centroid of the covid cluster than the mean for non-Covid projects) and present the results in [#fig:sim_interv]. 

![Pre-Covid-19 specialisation intervals in Covid-19 related areas based on different proximity thresholds. Countries in the vertical axis are sorted by the mean of the midpoint in the confidence interval for all research clusters for a country](final_report_deck/png/specialisation_robustness.png){#fig:sim_interv}

The chart suggests that the measures of specialisation in Covid research clusters such as Products and Services and Policy - where as we noted below there is a higher degree of semantic overlap between Covid and non-Covid projects - are particularly volatile. In contrast, estimates of specialisation in biomedical research clusters such as Diagnosis and Prevention and Biotechnology seem to be more robust.

In [@fig:prep_plot] we compare specialisation in Covid-19 related topics before (horizontal axis) and after the pandemic for the top 15 countries by level of project coordination, with Covid research clusters sorted by the strength of the rank-correlation between specialisation before the pandemic and specialisation afterwards.

![Relative specialisation coordinating Covid-19-cluster related projects before the pandemic (horizontal axis) and Covid-19 related-clusters afterwards (vertical axis). Size of points represents number of coordinated projects in a Covid-19 research area since the beginning of the pandemic.](final_report_deck/png/preparedness_plot.png){#fig:prep_plot}

The chart shows a strong correlation between pre and post coordination specialisation in some research areas such as Biotechnology, Policy and Public Health while the correlation is negative in the Products and Services research cluster (where, as we just pointed out, our measures of specialisation pre-pandemic are noisier). Understanding what drives the differences between research areas and what explains whether countries are able to exploit - or not - their research strenghts in Covid-19 related areas with the arrival of the pandemic are important questions for future research.

### Organisational proximity and participation in Covid-19 related research

The semantic approach we described can also be used to measure organisational relatedness to Covid-19 research. In order to do this, we calculate the mean of the vector representations of all projects involving eaach organisation in the Cordis database before the pandemic, and measure its (cityblock) distance to the centroids of all our Covid-19 research clusters. Our prior, based on the Principle of Relatedness studied in economic geography and economic complexity, is that countries 'closer' to those clusters are more likely to participate in Covid-19 related research when the pandemic arrives because they have the right capabilities to do so [@hidalgo2018principle].

We present the results by Covid-19 research cluster and country in [@fig:org_dist]. The points represent the share of organisations in a country and rank of proximity to the centre of the Covid-19 cluster that did in fact participate (in any role) in Covid-19 projects. One way to think about this is as a proxy for the 'utilisation' of related organisational capabilities in the Covid-19 research respose. 

![Relative specialisation coordinating Covid-19-cluster related projects before the pandemic (horizontal axis) and Covid-19 related-clusters afterwards (vertical axis). Size of points represents number of coordinated projects in a Covid-19 research area since the beginning of the pandemic.](final_report_deck/png/participation_distances.png){#fig:org_dist}

Points towards the right represent organisations that were semantically closer to Covid-19 research clusters - we see that, almost without exception, this group of organisations were more likely to participate in Covid-19 projects, in line with what we would expect. Having said this, the chart also shows important differences between countries and research clusters, suggesting variation in Covid-19 deployment capabilities and perhaps an underutilisation of knowledge that might have been relevant in the fight against the pandemic. For example, when we look at the "Biotechnology" research cluster we find that almost 25%% of the Dutch organisations in the top decile of semantic proximity to that research cluster participated in Covid-19 projects, while less than 10% of Spanish organisations did. 

### Topical composition of the Covid-19 research response.

Having segmented EC-funded research activities to tackle the Covid-19 pandemic into broad research segments, we move to a more finely grained analysis using a hierarchical topic model that uses Bayesian methods to infer the distribution of words over topics (capturing clusters of frequently co-occurring words potentially reflecting a 'theme' or subject) and the distribution of topics over documents (capturing these documents' thematic focus) [@gerlach2018network]. Our goal is to compare the topical composition of Covid-19 oriented EC-funded projects with the broader CORDIS corpus in order to understand what topics are overrepresented and what topics are underrepresented in the EC R&I response captured in the CORDIS dataset.

We train the topic model on a corpus of H2020 projects started since 2019, resulting in the extraction of 289 topics from the data. In order to simplify the presentation of results, we cluster those topics into a smaller set of 17 subjects using a network-based approach.^[This entails creating a topic co-occurrence network connecting those topics that tend to appear in the same documents, and decomposing them through a community detection approach along the lines of what we described earlier. We name the resulting categories after a visual inspection of their constituent topics.] We then regress (using ordinary least squares) each topic's distribution over projects on an indicator variable capturing whether a project was part of the EC Covid-19 research response, and whether it was in one of the Covid-19 research categories we have used in previous subsections. Figures [@fig:covid_topics] and [@fig:cluster_topics] respectively present the estimated regression coefficients and confidence intervals for each topic according to these models.

![Estimated coeffients and confidence intervals for a regression of topic distributions on an indicator variable for whether a project is part of the EC Covid-19 response or not. The colors indicate the topic community that an individual topic belongs to.](final_report_deck/png/topical_focus.png){#fig:covid_topics}

![Covid Estimated coeffients and confidence intervals for a regression of topic distributions on an indicator variable for the research cluster that a projects has been classifed on using the non-Covid corpus as a reference class. The colors indicate the topic community that an individual topic belongs to.](final_report_deck/png/topic_coefficients.png){#fig:cluster_topics}

[@fig:covid_topics] shows that, perhaps unsurprisignly, topics related to biology (topic community 4) and health (topic community 10) are overrepresented in the Covid-19 response compared to the broader corpus. We also find an overrepresentation of topics about networking and SMEs (topic communities 8 and 11), reflecting the Commission support for innovative ventures and research and business collaboration networks during the pandemic. Topics related to the Environment (topic community 0), Humanities (topic community 12) and - perhaps more surprisingly - modelling (topic community 16) appear relatively underrepresented compared to the broader H2020 portfolio. Having said this, the more granular perspective offered by [@fig:cluster_topics] suggests that some of these topics have a presence in particular segments of the Covid-19 research response, as is the case with Humanities topics in the policy research cluster, and Modelling in the systems and networks cluster.

## Research publications {#subsec:paper}

Having analysed the R&I funding activities in response to the pandemic by a key stakeholder for the EURITO project - the European Commission - we turn to an analysis of research publications with a particular focus on preprints, an method for research dissemination that might offer us a particularly timely perspective on the evolution and geography of the response to the pandemic [@fraser2020preprinting, @majumder2020early]. 

Several studies of the role of preprints in the Covid-19 pandemic have recognised their value as an important channel for rapid scientific communication during the crisis [@fraser2021evolving] while highlighting some of their risks, in particular the dissemination of scientific returns that have not been subject to peer-review [@besanccon2020open]. In general, research published via pre-prints is found to achieve wider dissemination and visibility in news and social media [@fraser2021evolving] while it suffers in some cases from low levels of reproducibility and transparency [@besanccon2020open]. 

We are also interested in what these data can tell us about the dynamics of the research response to the pandemic. For example, some studies suggest lower levels of collaboration brought about by the need to "work fast" and locally [@fry2020consolidation], and have also raised concerns about "research races" whcih attract new entrants focused on topics with short-term benefits at the expense of more patient and interdisciplinary research [@bryan2020innovation]. 

### Data sources

We start with a dataset with 2.5 million documents including preprints from arXiv (focusing on Physics, Mathematics and Computer Science), biorXiv (focusing on Biology) and medrXiv (focused on Medical Sciences) and the CORD19 database of Covid-19 related publications compiled by a consortium of research funders and technology companies led by the Allen Institute for AI [@wang2020cord]. We filter this data so that it only includes articles with titles and abstract that mention Covid-19 related terms and finish with a dataset of around 250,000 documents, including 230,000 from CORD-19 (mostly comprising peer-reviewed publications), almost 14,000 preprints from medrXiv, 4,500 from arXiv and 4,300 from biorXiv.^[We exclude from the CORD-19 corpus articles about virus research in general [@colavizza2021scientometric].]. 

### Temporal and thematic differences between preprints and peer-reviewed publications

In [@fig:article_trends] we compare the temporal distribution of activity in our data by article source (type) focusing on the year 2020.^[A large number of CORD-19 articles for 2021 only contain their year of publication so it was not possible to extend the analysis further]. It shows that preprint activity responded faster to the onset of the pandemic that peer-reviewed publications in CORD-19, with arXiv reaching an initial peak followed by medrXiv and biorXiv. This finding is consistent with the idea that preprints played a role in the rapid dissemination of research findings earlier in the pandemic.

![Monthly share of Covid-19 articles in a source 2020](final_report_deck/png/article_trends.png){#fig:article_trends}

In order to compare the thematic composition of preprints and peer-reviewed publications, we fit a Latent Dirichlet Allocation topic model on our whole corpus and, like we did before, regress the resulting topic distributions on an indicator variable for whether a document is a preprint or a peer-reviewed publication from CORD-19 [@blei2003latent].^[We classify topics into disciplines using the fields of study assigned to papers by Microsoft Academic Graph [@wang2020microsoft].] The results, which we present in [@fig:article_topical] show that several biological topics related to genetic analysis of Covid-19 and vaccines, as well as computer vision analysis of medical scans and predictive analyses of the evolution of the pandemic are overrepresented in the preprint corpus, while topics related to policy / Political Science, Economics, Psychology, Sociology and the Humanities tend to be underrepresented.^[We also note that some topics seem to have captured clusters of words in articles that were not written in English in the CORD data.].

![Regression coefficients and confidence intervals of the preprint category on topic distribution with highlights for topics with high / low estimated coefficients. We colour topics based on the disciplines where they are most salient.](final_report_deck/png/topical_focus_chart.png){#fig:article_topical}

These thematic differences between preprints and peer-reviewed publications could be explained by differences in the communities that target different dissemination venues, or by differences in the velocity with which different fields responded to the pandemic, either because their contributions were perceived to be particularly urgent or because they had capabilities to create research and knowledge rapidly in response to the pandemic. We probe this idea further by comparing the publication sequence of papers in topics that were dominant in preprints and papers in topics that were dominant in peer-reviewed publications only focusing on peer reviewed publications in 2021. 

We present the results in {#fig:pub_trends} where we see that papers involving topics overrepresented in preprints also tended to be published earlier in peer-reviewed publications, suggesting that there are topic-specific drivers of publication velocity independent from the venue where a paper is published.

![Monthly share of CORD-19 articles in topics dominant in preprints (orange line) and peer-reviewed publications.](final_report_deck/png/pub_trends.png){#fig:pub_trends}

We have decided to focus the rest of our analysis on the preprints corpus. The reason for this is that the data are more timely (exact publication dates are available for all articles adn not a subset, as is the case with CORD-19) and, as we just showed, the focus of the articles is on topics that are disseminated more rapidly and where access to timely indicators might be more useful. This also allow us to implement more robust (although less scalable) topic modelling algorithms [@gerlach2018network]. Before doing this, we compare the international distribution of publications in order to assess if this brings coverage biases into our analysis.

[@fig:pub_corr] shows the rank correlation between national shares of activity in different publication venues. It shows a strong degree of correlation between national shares of activity, particularly in the case of medrXiv and CORD, suggesting that medical research communities are similarly present in both sources. The rank correlation between national shares of activity is weakest between arXiv and CORD, potentially reflecting differences in national research focus and publication strategies.

![Rank correlation between national shares of publication activity in different sources.](final_report_deck/png/pub_corr.png){#fig:pub_corr}

In [@fig:country_shares] we present the shares of publication activity accounted by different countries in the top 25 by activity. We use a logarithmic scale in the x-axis to increase the visibility of the differences between venue focus in countries that are not on the top 3 (USA, United Kingdom and China). In general, the chart suggests that the use of preprints as a proxy for research activity would not lead to a massive under-representation of specific countries perhaps with the exception of Iran, where the share of Cord19 publications is substantially higher than the share of preprints.

![National shares of activity by publication source for top 25 countries in the corpus with a logarithmic scale in the X axis.](final_report_deck/png/country_shares.png){#fig:country_shares}

### Preprint research themes

We have clustered Covid-19 related articles based on their topical compositions using the SBM topic model [@gerlach2018network] and named each cluster after a visual inspection of its contents and an analysis of its most salient terms compared to the corpus overall. 

[@fig:cluster_sources] presents the number of papers in each cluster and their preprint sources, and [@tbl:cluster_examples] provides some randomly drawn examples of papers in each category. 

We note the sorting of research topics into publication venues: articles related to biological disciplines such as genetic analysis or antiviral drugs were published in arXiv, papers about Covid-19 population and patient impacts and Hospitalisation primarily go into medrXiv and papers that analyse social media data and medical scans using machine learning methods are disseminated via arXiv.

![National shares of activity by publication source for top 25 countries in the corpus with a logarithmic scale in the X axis.](final_report_deck/png/cluster_sources.png){#fig:cluster_sources}

| Cluster                      |    n | Examples                                                                                                                                                                                                                |
|:-----------------------------:|:-------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Lockdown Social Distancing   | 1947 | Do e-scooters fill mobility gaps and promote equity before and during                                                                                                                                                   |
|                              |      |   COVID-19? A spatiotemporal analysis using open big data                                                                                                                                                               |
|                              |      |  Spatially refined time-varying reproduction numbers of SARS-CoV-2 in Arkansas and Kentucky and their relationship to population size and public health policy, March November, 2020                                  |
|                              |      |  COVID-19 pandemic-related lockdown: response time is more important than its strictness                                                                                                                                |
| Prediction                   | 1726 | Sub-epidemic model forecasts for COVID-19 pandemic spread in the USA and European hotspots, February-May 2020                                                                                                           |
|                              |      |  Epilocal: a real-time tool for local epidemic monitoring                                                                                                                                                               |
|                              |      |  Analyzing COVID-19 pandemic with a new growth model for population                                                                                                                                                     |
|                              |      |   ecology                                                                                                                                                                                                               |
| Social Media                 | 1520 | Artificial Intelligence-based Clinical Decision Support for COVID-19 --                                                                                                                                                 |
|                              |      |   Where Art Thou?                                                                                                                                                                                                       |
|                              |      |  Accelerating COVID-19 research with graph mining and transformer-based                                                                                                                                                 |
|                              |      |   learning                                                                                                                                                                                                              |
|                              |      |  Challenges of Equitable Vaccine Distribution in the COVID-19 Pandemic                                                                                                                                                  |
| Genetic Analysis             | 1367 | COVID-19 dominant D614G mutation in the SARS-CoV-2 spike protein desensitizes its temperature-dependent denaturation                                                                                                    |
|                              |      |  The ongoing evolution of variants of concern and interest of SARS-CoV-2 in Brazil revealed by convergent indels in the amino (N)-terminal domain of the Spike protein                                                  |
|                              |      |  Serum Neutralizing Activity of mRNA-1273 against SARS-CoV-2 Variants                                                                                                                                                   |
| Population Impact            | 1229 | Unraveling the Dynamic Importance of County-level Features in Trajectory                                                                                                                                                |
|                              |      |   of COVID-19                                                                                                                                                                                                           |
|                              |      |  Multiple drivers of the COVID-19 spread: role of climate, international mobility, and region-specific conditions                                                                                                       |
|                              |      |  Hospital preparedness in epidemics by using simulation. The case of COVID-19                                                                                                                                           |
| Mental Health                | 1137 | COVID-19 preventive behaviors among people with anxiety and depression: Findings from Japan                                                                                                                             |
|                              |      |  Worsening of pre-existing psychiatric conditions during the COVID-19 pandemic                                                                                                                                          |
|                              |      |  Adenovirus and RNA-based COVID-19 vaccines: perceptions and acceptance among healthcare workers                                                                                                                        |
| Lockdown Social Distancing 2 | 1115 | Successful contact tracing systems for COVID-19 rely on effective quarantine and isolation                                                                                                                              |
|                              |      |  Dark matter, second waves and epidemiological modelling                                                                                                                                                                |
|                              |      |  SYSTEMATIC OBSERVATION OF COVID-19 MITIGATION (SOCOM): ASSESSING FACE COVERING AND DISTANCING IN SCHOOLS                                                                                                               |
| Impact Studies 3             | 1100 | SARS-CoV-2 infection in the Syrian hamster model causes inflammation as well as type I interferon dysregulation in both respiratory and non-respiratory tissues including the heart and kidney                          |
|                              |      |  Increased Expression of Chondroitin Sulfotransferases following AngII may Contribute to Pathophysiology Underlying Covid-19 Respiratory Failure: Impact may be Exacerbated by Decline in Arylsulfatase B Activity      |
|                              |      |  Identification of potential key genes for SARS-CoV-2 infected human bronchial organoids based on bioinformatics analysis                                                                                               |
| Hospitalisation              | 1083 | Is the psychological well-being of a population associated with COVID-19 related survival?                                                                                                                              |
|                              |      |  COVID-19 TARRACO Cohort Study: Development of a predictive prognostic rule for early assessment of COVID-19 patients in primary care settings                                                                          |
|                              |      |  Heterogeneity in COVID-19 severity patterns among age-gender groups: an analysis of 778 692 Mexican patients through a meta-clustering technique                                                                       |
| Impact Studies               |  921 | Differential roles of RIG-I-like receptors in SARS-CoV-2 infection                                                                                                                                                      |
|                              |      |  Recombinant SARS-CoV-2 RBD molecule with a T helper epitope as a built in adjuvant induces strong neutralization antibody response                                                                                     |
|                              |      |  The 2019 coronavirus (SARS-CoV-2) surface protein (Spike) S1 Receptor Binding Domain undergoes conformational change upon heparin binding.                                                                             |
| Serology                     |  815 | Evaluation of Serological SARS-CoV-2 Lateral Flow Assays for Rapid Point of Care Testing                                                                                                                                |
|                              |      |  Evaluation of saliva sampling procedures for SARS-CoV-2 diagnostics reveals differential sensitivity and association with viral load                                                                                   |
|                              |      |  Prevalence of SARS-CoV-2 among high-risk populations in Lom&eacute (Togo) in 2020                                                                                                                                      |
| Antiviral Drugs              |  788 | Structural basis for repurpose and design of nucleoside drugs for treating COVID-19                                                                                                                                     |
|                              |      |  Nonstructural protein 1 of SARS-CoV-2 is a potent pathogenicity factor redirecting host protein synthesis machinery toward viral RNA.                                                                                  |
|                              |      |  Automatic design of novel potential 3CL$^{\text{pro}}$ and                                                                                                                                                             |
|                              |      |   PL$^{\text{pro}}$ inhibitors                                                                                                                                                                                          |
| Variants                     |  785 | An effective COVID-19 response in South America: the Uruguayan Conundrum                                                                                                                                                |
|                              |      |  in-silica Analysis of SARS-CoV-2 viral strain using Reverse Vaccinology Approach: A Case Study for USA                                                                                                                 |
|                              |      |  Nosocomial outbreak of SARS-CoV-2 in a 'non-COVID-19' hospital ward: virus genome sequencing as a key tool to understand cryptic transmission                                                                          |
| Image Detection              |  780 | COVID-19 Infection Localization and Severity Grading from Chest X-ray                                                                                                                                                   |
|                              |      |   Images                                                                                                                                                                                                                |
|                              |      |  COVID-Net S: Towards computer-aided severity assessment via training and                                                                                                                                               |
|                              |      |   validation of deep neural networks for geographic extent and opacity extent                                                                                                                                           |
|                              |      |   scoring of chest X-rays for SARS-CoV-2 lung disease severity                                                                                                                                                          |
|                              |      |  End-to-End AI-Based Point-of-Care Diagnosis System for Classifying                                                                                                                                                     |
|                              |      |   Respiratory Illnesses and Early Detection of COVID-19                                                                                                                                                                 |
| Patient Impact               |  701 | Changes in RT-PCR-positive SARS-CoV-2 rates in adults and children according to the epidemic stages                                                                                                                     |
|                              |      |  COVID-19 infection and subsequent thromboembolism: A self-controlled case series analysis of a population cohort                                                                                                       |
|                              |      |  A New Hematological Prognostic Index For Covid-19 Severity                                                                                                                                                             |
| Education                    |  543 | Years of life lost due to the psychosocial consequences of COVID19 mitigation strategies based on Swiss data                                                                                                            |
|                              |      |  Assessing knowledge, concerns, and risk perceptions among Italian medical students during the SARS-CoV-2 pandemic.                                                                                                     |
|                              |      |  Supply and demand shocks in the COVID-19 pandemic: An industry and                                                                                                                                                     |
|                              |      |   occupation perspective                                                                                                                                                                                                |
| Antibodies                   |  537 | SARS-CoV-2 seroassay optimization and performance in a population with high background reactivity in Mali                                                                                                               |
|                              |      |  Original antigenic sin responses to heterologous Betacoronavirus spike proteins are observed in mice following intramuscular administration, but are not apparent in children following SARS-CoV-2 infection           |
|                              |      |  SARS-CoV-2 antigens expressed in plants detect antibody responses in COVID-19 patients                                                                                                                                 |
| Repurposed Treatments        |  530 | HYDROXICLOROQUINE FOR PRE-EXPOSURE PROPHYLAXIS FOR SARS-CoV-2                                                                                                                                                           |
|                              |      |  Tocilizumab Effect in COVID-19 Hospitalized Patients: A Systematic Review and Meta-Analysis of Randomized Control Trials                                                                                               |
|                              |      |  Beneficial and Harmful Outcomes of Tocilizumab in Severe COVID-19: A Systematic Review and Meta-Analysis                                                                                                               |
| Detection Sequencing         |  530 | High-frequency screening combined with diagnostic testing for control of SARS-CoV-2 in high-density settings: an economic evaluation of resources allocation for public health benefit                                  |
|                              |      |  High sensitivity detection of coronavirus SARS-CoV-2 using multiplex PCR and a multiplex-PCR-based metagenomic method                                                                                                  |
|                              |      |  SARS-COV-2 VIRUS INFECTED PATIENT IDENTIFICATION THROUGH CANINE OLFACTIVE DETECTION ON AXILLARY SWEAT SAMPLES                                                                                                          |
| Airborne                     |  506 | Luminore CopperTouche surface coating effectively inactivates SARS-CoV-2, Ebola and Marburg viruses in vitro                                                                                                            |
|                              |      |  N95 Mask Decontamination using Standard Hospital Sterilization Technologies                                                                                                                                            |
|                              |      |  Seasonal stability of SARS-CoV-2 in biological fluids                                                                                                                                                                  |
| Healthcare                   |  445 | The prevention of nosocomial SARS-CoV2 transmission in endoscopy: a systematic review of recommendations within gastroenterology to identify best practice.                                                             |
|                              |      |  Effects of the COVID-19 pandemic on publication landscape in chimeric antigen receptor-modified immune cell research                                                                                                   |
|                              |      |  Meta-Research: Citation needed? Wikipedia and the COVID-19 pandemic                                                                                                                                                    |
| Detection Diagnosis          |  439 | A Public Website for the Automated Assessment and Validation of                                                                                                                                                         |
|                              |      |   SARS-CoV-2 Diagnostic PCR Assays                                                                                                                                                                                      |
|                              |      |  Comparison of Commercially Available and Laboratory Developed Assays for in vitro Detection of SARS-CoV-2 in Clinical Laboratories                                                                                     |
|                              |      |  Graphene-based optical sensors for the pre-vention of SARS-CoV-2 viral                                                                                                                                                 |
|                              |      |   dissemination                                                                                                                                                                                                         |
| Indirect Impacts             |  395 | The association between lockdown due to COVID-19 epidemic and searches for toothache using Google Trends in Iran                                                                                                        |
|                              |      |  The effect of BMI and physical activity levels on the duration of symptomatic days with Covid-19 infection                                                                                                             |
|                              |      |  Age, gender and COVID-19 infections                                                                                                                                                                                    |
| Impact Studies 2             |  340 | A household case evidences shorter shedding of SARS-CoV-2 in naturally infected cats compared to their human owners.                                                                                                    |
|                              |      |  Defining the Syrian hamster as a highly susceptible preclinical model for SARS-CoV-2 infection                                                                                                                         |
|                              |      |  Susceptibility of tree shrew to SARS-CoV-2 infection                                                                                                                                                                   |
| Vaccination Programmes       |  338 | Impact of vaccination in reducing Hospital expenses, Mortality and Average length of stay among COVID-19 patients: a retrospective cohort study from India                                                             |
|                              |      |  Real-time assessment of COVID-19 impact on global surgical case volumes                                                                                                                                                |
|                              |      |  Fevers Are Rarest in the Morning: Could We Be Missing Infectious Disease Cases by Screening for Fever Then?                                                                                                            |
| Trials                       |  327 | COVID-19 Mortality Following Mass Gatherings                                                                                                                                                                            |
|                              |      |  Outcomes of COVID-19 infection in patients treated with Clozapine                                                                                                                                                      |
|                              |      |  Antibacterial consumption in the context of COVID-19 in Pakistan: an analysis of national pharmaceutical sales data for 2019-20                                                                                        |
| Vaccines                     |  261 | Older age is associated with sustained detection of SARS-CoV-2 in nasopharyngeal swab samples                                                                                                                           |
|                              |      |  Neutralization of Delta variant with sera of Covishield vaccinees and COVID-19 recovered vaccinated individuals                                                                                                        |
|                              |      |  Immunogenicity of COVID-19 Vaccination in Immunocompromised Patients: An Observational, Prospective Cohort Study Interim Analysis                                                                                      |
| Smoking Cancer               |  168 | Association of the Covid-19 lockdown with smoking, drinking, and attempts to quit in England: an analysis of 2019-2020 data.                                                                                            |
|                              |      |  Clinical Characteristics and Severity of COVID-19 Disease in Patients from Boston Area Hospitals                                                                                                                       |
|                              |      |  Association between angiotensin-converting enzyme inhibitors and angiotensin II receptor blockers use and the risk of infection and clinical outcome of COVID-19: a comprehensive systematic review and meta-analysis. |
: Examples of articles in Covid-19 research clusters {#tbl:cluster_examples}

In order to evaluate the robustness of our clustering results, we have compared them with the outputs of an ensemble of K-Means clustering algorithms using different cluster sizes and random initialisations.^[The K-Means algorithm looks for ways to partition the data in K groups in a way that maximises similarities inside groups and differences between groups [@macqueen1967some].] [@fig:cluster_co_occs] displays the number of co-occurrences that had initially been placed in our canonical clusters. We see that each of the cluster has the largest number of co-occurrences in the diagonal (i.e. our test algorithms tend to place together observations that were already together in the original clustering). In those cases where we observe strong overlap between clusters this appears to be driven by semantic and application similarities between clusters, as is the case with "Variants" and "Genetic analysis", between "Prediction" and "Social distancing" or between "Repurposed treatments" and "Hospitalisation". 

This suggests that our clustering results are robust and that overlaps between clusters are explainable.

![Number of co-occurrences in the Kmeans test group between observations in the original cluster categories](final_report_deck/png/cluster_cooccurrences.png){#fig:cluster_co_occs}

![Number of co-occurrences in the Kmeans test group between observations in the original cluster categories](final_report_deck/png/cluster_cooccurrences.png){#fig:cluster_co_occs}

### Thematic evolution of activity

### Geography of Covid-19 research and specialisation

### International evolution of activity

### Comparative analysis of influence and collaboration

## Funder benchmarking {#subsec:funder}

## OpenAIRE analysis {#subsec:openaire}

# Validation {#sec:val}

# Outputs {#sec:outputs}

# Organisational implications {#sec:org}

# Conclusions {#sec:conclusion}



# Conclusions


    