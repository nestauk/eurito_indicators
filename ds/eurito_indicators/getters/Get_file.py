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
# Import libraries needed
import pandas as pd


# %%
# Open and read in input excel file
def read_excel_file():
    df = pd.read_excel('https://www.ukcdr.org.uk/wp-content/uploads/2021/06/COVID-19-Research-Project-Tracker-18-JUN-2021.xlsx',
                      sheet_name='Funded Research Projects', usecols='A:AQ')
    return df

# %%
