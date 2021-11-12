from os import chdir, join
from param file import *
import logging
logging.basicConfig(level=logging.INFO)


DATA_ANALYSIS_PARAMS 

def step_1():
    file_tools.manage_directories(WD_ANALYSIS_PREP, False)
    chdir(WD_ANALYSIS_PREP)
    file_tools.manage_directories(DATA_ANALYSIS_PARAMS, True)

    # required file paths + verbose parameter (set to True)
    prepare_data.run(DATA_ANALYSIS_PARAMS, True)

def main():
    step_1()

if __name__ == "__main__":
    main()