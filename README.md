# Retrospective analysis of Covid-19 hospitalization modelling scenarios which guided policy response in France

This is the code supporting the results in the article "Retrospective analysis of Covid-19 hospitalization modelling scenarios which guided policy response in France". 
![](https://github.com/maxime-langevin/retrospective_analysis/blob/main/graphs/all_ICU_scenarios_reality.png)
## Data preparation 

To run our analysis, we need (a) data from published modelling scenarios and (b) ground truth data. 

For (a), since both Pasteur Institute and INSERM's modelling scenarios' underlying data were not public, we extracted them manually from the reports figures, using WebPlotDigitizer. 
The detailed process for each report is described in the "Prepare Scenarios ICU" and "Prepare Scenarios Hospitalizations" paragraphs of the [data_preparation.Rmd](data_preparation/data_preparation.Rmd). 
For each report we indicate its original URL source. Then :
- in the "Original" tab, we provide the screenshot of the original scenarios figures from which data are extracted.
- in the "Reproduced" tab, we reproduce the original figures from our extracted data. In some rare cases, we horizontally or vertically offset the data for better alignment, based on comparison to reality data before report publication.

For (b), we use either :
- ground truth data from one of Pasteur Institutes’s modelling team paper (Paireau et al 2022), which has its own cleaning and smoothing process of the government raw data. This dataset stops on July 2021.
- beyond this date, we use data from multiple sources (extraction of ground truth from Pasteur Institue’s subsequent reports, government data) and combine them to produce one unique and coherent dataset


## Retrospective analysis 

Using those data sources, we compute several error and uncertainty metrics in the [get_results.py](retrospective_analysis/get_results.py) script. 


## Results

From those metrics, we generate within the file [graph_errors.Rmd](graph_errors.Rmd) all the figures reported in the article, and store them within the "graphs" folder. An  .html version of the file is also given, for readers that easily want to see the code and the figures generated side-by-side. 




