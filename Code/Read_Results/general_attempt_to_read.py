import pandas as pd 
from matplotlib import pyplot as plt
from clean_SCIP_results import *

"""
Tries to read results of a specific type. Can either read tables like this

N Years | Objective Value | Dual Bound | Time | Gap
1       |    28.8     |    28.8    | 0.15 | 0.00
2       |    56.1     |    56.1    | 0.32 | 0.00
3       |    82.4     |    82.4    | 0.68 | 0.00

or SCIP (8) logs

time | node  | left  |LP iter|LP it/n|mem/heur|mdpt |vars |cons |rows |cuts |sepa|confs|strbr|  dualbound   | primalbound  |  gap   | compl.
o 6.0s|     1 |     0 | 19611 |     - |feaspump|   0 |5179 |3707 |  10k|   0 |  0 |   0 |   0 | 3.891981e+02 | 3.475789e+02 |  11.97%| unknown
  6.3s|     1 |     0 | 21326 |     - |    84M |   0 |5179 |3707 |  11k| 952 |  1 |   0 |   0 | 3.849358e+02 | 3.475789e+02 |  10.75%| unknown
  6.3s|     1 |     0 | 21656 |     - |    86M |   0 |5179 |3707 |  12k|1593 |  2 |   0 |   0 | 3.844127e+02 | 3.475789e+02 |  10.60%| unknown
  6.4s|     1 |     0 | 22000 |     - |    88M |   0 |5179 |3707 |  12k|1959 |  3 |   0 |   0 | 3.841999e+02 | 3.475789e+02 |  10.54%| unknown

although some care is needed in the later case (some things have to be manually removed, but not many)

"""


def get_data(file):
    df = pd.read_csv(file, sep="|")
    df.reset_index(drop=True, inplace=True)
    df.replace(" ","", inplace=True)
    df.columns = df.columns.str.replace(" ", "")
    return df

def get_data_from_scip(file, clean_df=False):
    # you may need to manually remove some things
    
    if clean_df:
        remove_presolve(file)
    df = pd.read_csv(file, sep="|")
    df.replace(" ", "", inplace=True)
    df.columns = df.columns.str.replace(" ","")
    df = df[["time", "primalbound", "gap"]]
    df = df[~df["primalbound"].astype(str).str.contains("--")] # trying to remove lines with no incumbent
    df["time"] = df["time"].map(lambda x: x.lstrip('L*ropd').rstrip('s')).astype(float)
    df["primalbound"] = df["primalbound"].astype(str).map(lambda x: x.rstrip('+02')).astype(float)
    df["primalbound"] = df["primalbound"].astype(str).map(lambda x: x.rstrip('+03')).astype(float)
    return df

def get_relevant_files(files):
    root = "/home/dionisio/Desktop/Doutoramento/Trabalho/Models/PySCIPOpt/Results/"
    return [root + i for i in files]

def get_relevant_logs(files):
    root = "/home/dionisio/Desktop/Doutoramento/Trabalho/Models/PySCIPOpt/Results/"
    end = "_log.txt"
    return [root + i + end for i in files]

def join_iterative_iterations(df):
    """
    Picks up a run of iterative refinement (for just one year) and combines all iterations into one dataframe
    """
    shifts = [(df.index[0],0)]
    for i in range(df.index[1], len(df)):
        if df.loc[i,"time"] < df.loc[i-1,"time"] or df.loc[i,"gap"] > df.loc[i-1,"gap"]:
            shifts.append((i,df.loc[i-1,"time"] + shifts[-1][1]))
    shifts.append((float("inf"),float("inf")))
    counter = 0
    i = df.index[0]
    while i <= len(df):
        if i >= shifts[counter+1][0]:
            counter+=1
        df.loc[i,"time"] += shifts[counter][1]
        i+=1 
    return [df, shifts]

def plot_log_evolution(file_names = [["create_20y","iterative_20y"], ["create_50y","iterative_50y"], ["create_100y","iterative_100y"]]):
    for index, file_names in enumerate(file_names):
        file_names = get_relevant_logs(file_names)
        max_time = -1
        max_primalbound = -1
        min_primalbound = float("inf")
        for file in file_names:
            df = get_data_from_scip(file, clean_df=True)
            #return df
            if "iterative" in file:
                df, shifts = join_iterative_iterations(df)
                label = "iterative refinement"
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
                    print(df)
            else:
                label = "original model"
            time = df["time"]
            incumbent = df["primalbound"]
            gap = df["gap"]
            plt.plot(time, incumbent, label=label)
            max_time = max(max_time,max(df["time"]))
            max_primalbound = max(max_primalbound,max(df["primalbound"]))
            min_primalbound = min(min_primalbound, max(min(df["primalbound"]),0))
        plt.xlim(0,max_time)
        plt.ylim(0.75*min_primalbound, 1.1*max_primalbound)
        plt.xlabel("Time (s)")
        plt.ylabel("Incumbent")

        handles, labels = plt.gca().get_legend_handles_labels()
        #handles.append(plt.Line2D([], [], color="red", label="Iteration start", marker="x", linewidth=0))

        plt.legend(handles = handles, loc = (0.6,0.4))
        if "20" in file:
            plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/create_vs_iterative_20y.png",bbox_inches='tight')
        elif "50" in file:
            plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/create_vs_iterative_50y.png",bbox_inches='tight')
        elif "100" in file:
            plt.savefig("/home/dionisio/Desktop/Doutoramento/Trabalho/Media/create_vs_iterative_100y.png",bbox_inches='tight')
        plt.show()
    return 

   

if __name__ == "__main__":
    plot_log_evolution([["create_50y","iterative_50y"],["create_100y","iterative_100y"]])