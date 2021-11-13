from os import chdir, join
from param file import *
from ndl_tense.data_analysis import prepare_data, plots
import logging
logging.basicConfig(level=logging.INFO)


def prepare():
    file_tools.manage_directories(WD_ANALYSIS_PREP, False)
    chdir(WD_ANALYSIS_PREP)
    file_tools.manage_directories(DATA_ANALYSIS_FILES, True)

    # required file paths + verbose parameter (set to True)
    prepare_data.run(DATA_ANALYSIS_FILES, True)

def plot_plots():
    file_tools.manage_directories(DATA_ANALYSIS_PLOTS_DIR, False)
    chdir(DATA_ANALYSIS_PLOTS_DIR)
    file_tools.manage_directories(DATA_ANALYSIS_PLOTS_FILES, True)

    # required file paths + verbose parameter (set to True)
    plots.run(DATA_ANALYSIS_PLOTS_FILES, True)

def main():
    prepare()
    plot_plots()

if __name__ == "__main__":
    main()