"""
Functionality for reading in data and plotting Bar Codes.
"""

__author__ = "Saveliy Yusufov, Helen Jin"
__date__ = "19 March 2019"
__license__ = "GPL"
__maintainer__ = "Saveliy Yusufov"
__email__ = "sy2685@columbia.edu"

import pandas as pd
import matplotlib.pyplot as plt


def read_data_file(file_path):
    """Reads in a CSV file into a DataFrame

    Parameters
    ----------
    file_path: str
        The full path to the CSV file.

    Returns
    -------
    dataframe: pandas DataFrame
        A DataFrame with epsilon values as the index and the corresponding
        first, three Betti numbers as columns. Namely, `B_{0}, B_{1}, B_{2}`.
    """
    betti_nums = pd.read_csv(file_path, header=None, index_col=0)
    betti_nums.columns = ["B_0", "B_1", "B_2"]

    return betti_nums


def plot_barcode(betti_nums):
    """Plots a Bar Code, using Betti Numbers from a DataFrame

    Parameters
    ----------
    betti_nums: pandas DataFrame
        A DataFrame with epsilon values as the index and the corresponding
        first, three Betti numbers as columns. Namely, `B_{0}, B_{1}, B_{2}`.
    """
    _, (ax0, ax1, ax2) = plt.subplots(nrows=3, sharex=True, figsize=(15, 10))

    ax0.set_title("B_0")
    ax0.scatter(betti_nums.index, betti_nums.B_0, data=betti_nums, marker='s')
    ax0.set_ylim(0.5)

    ax1.set_title("B_1")
    ax1.scatter(betti_nums.index, betti_nums.B_1, data=betti_nums, color="purple", marker='s')
    ax1.set_ylim(0.5)

    ax2.set_title("B_2")
    ax2.scatter(betti_nums.index, betti_nums.B_2, data=betti_nums, color="green", marker='s')
    ax2.set_ylim(0.5)

    plt.tight_layout()
    plt.savefig("barcode.png", format="png", dpi=600)


if __name__ == "__main__":
    pass
