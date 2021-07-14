import matplotlib.pyplot as plt 

from eurito_indicators import PROJECT_DIR

FIG_PATH = f"{PROJECT_DIR}/outputs/figures"

def save_matplot(name):
    plt.tight_layout()
    plt.savefig(FIG_PATH+f"/{name}.pdf")

def save_lookup(file, name):
    with open(f"{PROJECT_DIR}/inputs/data/{name}.json", 'w') as outfile:
        json.dump(file,outfile)
