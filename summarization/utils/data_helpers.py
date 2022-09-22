from multiprocessing import Pool
from os import path, mkdir

import numpy as np
import pandas as pd


def parallelize_df_processing(df, func, num_cores=4, num_partitions=20):
    df_split = np.array_split(df, num_partitions)
    pool = Pool(num_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


def make_out_dir_if_not_exists(out_directory):
    if not path.exists(out_directory):
        mkdir(out_directory)
