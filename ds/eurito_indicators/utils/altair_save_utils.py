# Scripts to save altair charts

import os

import altair as alt
from altair_saver import save
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from eurito_indicators import PROJECT_DIR

FIG_PATH = f"{PROJECT_DIR}/outputs/figures"

# Checks if the right paths exist and if not creates them when imported
os.makedirs(f"{FIG_PATH}/png", exist_ok=True)
os.makedirs(f"{FIG_PATH}/html", exist_ok=True)


def google_chrome_driver_setup():
    # Set up the driver to save figures as png
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver

<<<<<<< HEAD
def make_altair_save_dirs(path):
    os.makedirs(path + "/png", exist_ok=True)
    os.makedirs(path + "/html", exist_ok=True)

=======
>>>>>>> added altair save utils script

def save_altair(fig, name, driver, path=FIG_PATH):
    """Saves an altair figure as png and html
    Args:
        fig: altair chart
        name: name to save the figure
        driver: webdriver
        path: path to save the figure
    """
    save(
        fig,
        f"{path}/png/{name}.png",
        method="selenium",
        webdriver=driver,
        scale_factor=5,
    )
    fig.save(f"{path}/html/{name}.html")


def altair_text_resize(chart: alt.Chart, sizes: list) -> alt.Chart:
    """Resizes font sizes in labels / legends of altair chart
    Args:
        chart: altair chart
        sizes: list where first element is label size and second argument is
            title size
    """

<<<<<<< HEAD
    ch = (chart.
          configure_axis(
                         labelFontSize=sizes[0], titleFontSize=sizes[1])
          .configure_legend(labelFontSize=sizes[0], titleFontSize=sizes[1])
          .configure_header(labelFontSize=sizes[0], titleFontSize=sizes[1])
          )

    return ch

def ch_resize(chart):
    '''Resizes altair charts with a set size for labels and titles
    '''
    
    return altair_text_resize(chart, [12,12])

=======
    ch = chart.configure_axis(
        labelFontSize=sizes[0], titleFontSize=sizes[1]
    ).configure_legend(labelFontSize=sizes[0], titleFontSize=sizes[1])
    return ch

>>>>>>> added altair save utils script

if __name__ == "__main__":
    google_chrome_driver_setup()
