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

# %%
articles = get_cord_articles('/Users/George/configs/mysqldb_team.config')

# %%
articles

# %%
