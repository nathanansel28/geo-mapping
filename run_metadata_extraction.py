from setup import setup_and_fetch_variables
environment_variables = setup_and_fetch_variables()
folder_paths = environment_variables.get('folder_paths', [])

import glob
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


import get_metadata as m

file_paths = glob.glob(os.path.join(folder_paths[0], "*"))  #TODO: expand to include multiple items in te list
df = m.get_media_metadata(file_paths)


