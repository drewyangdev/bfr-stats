import os
import numpy as np
import pandas as pd

from log import logger


## a directory for output with folders of experiment
output_dir = "./output/"
## experiment folder name that contains folders of subject data
experiment = "PB TT Tennis no BFR ALL TRIALs"
## subject folder name
subject = "Subject 2 no BFR"
## MVC file name identifier
all_mvc_filename_contains = "EMG_RMS"
## Specific Rep
## TODO - assume all Rep 3 are named with "Rep_3"
specific_rep = "Rep_3"
## Available activities
## TODO - assume all activities are named with below options 
activities = [
    "Pickleball_BH",
    "Pickleball_FH",
    "Pickleball_OH",
    "Table_Tennis_BH",
    "Table_Tennis_FH",
    "Table_Tennis_OH",
    "Tennis_BH",
    "Tennis_FH",
    "Tennis_OH",
]

## Smoothing function - from explore_normaliation.ipynb
## Reference: https://delsys.com/amplitude-analysis-root-mean-square-emg-envelope/
## Use 10 data points rolling window(0.004190s) by default
def rms_smoothing(df: pd.DataFrame, raw_column: str, smoothed_column: str, window_size: int=10):
    df[smoothed_column] = np.sqrt(df[raw_column].pow(2).rolling(window=window_size).mean())

def normalize_subject(output_dir, experiment, subject, all_mvc_filename_contains, specific_rep, activities):
    subject_path = os.path.join(output_dir, experiment, subject)
    sessions = [fname for fname in os.listdir(subject_path) if fname.endswith(".csv")]
    
    # filtering sessions: mvc or activities + specific rep
    ## find mvc - all mvc file name contains "EMG_RMS"
    mvc_sessions = []
    ## find sessions by activities and specific rep
    act_sessions = {act: [] for act in activities}
    for fname in sessions:
        if all_mvc_filename_contains in fname:
            mvc_sessions.append(fname)
        else:
            for act in activities:
                # matching activity
                if act in fname:
                    # if specified rep
                    if specific_rep:
                        # only pick specific rep
                        if specific_rep in fname:
                            act_sessions[act].append(fname)
                    # otherwise take all reps
                    else:
                        act_sessions[act].append(fname)

    # store max smoothed mvc
    max_smoothed_mvc_per_muscle = {}
    ## per muscle
    ## TODO - thought there is only one MVC rep per muscle, but found there are multiple reps for MVC
    for mvc_session in mvc_sessions:
        df_mvc = pd.read_csv(os.path.join(subject_path, mvc_session))
        ## TODO - assuming the MVC EMG is always at the second column, since it's organized by:
        ## X [s] | Biceps Femoris 7: EMG 7 [V] | X [s].1 | Biceps Femoris 7: EMG 7->filter (FilterSlidingRMS51) [V]
        mvc_emg_col_name = df_mvc.columns[1]
        ## smooth mvc
        rms_smoothing(df_mvc, mvc_emg_col_name, "smoothed")
        ## get max smoothed mvc per muscle
        mvc_emg_smoothed_max = df_mvc["smoothed"].max()
        logger.info(f"{mvc_emg_col_name} smoothed max: {mvc_emg_smoothed_max}")
        ## save this muscle's smoothed mvc max in a dict
        ## TODO - assuming MVC EMG column name is matching with the same column name in the regular session EMG column name
        max_smoothed_mvc_per_muscle[mvc_emg_col_name] = mvc_emg_smoothed_max
    logger.info(f"Selected smoothed max MVC: {max_smoothed_mvc_per_muscle}")
    logger.info("===========================")

    stat_result = {}
    ## per activity
    for act, reps in act_sessions.items():
        ## per rep
        for rep in reps:
            logger.info(f"Activity - Rep: {act} - {rep}")
            df_rep = pd.read_csv(os.path.join(subject_path, rep))
            ## per muscle
            ## TODO - same as above assumption, mvc column name matching with regular session column name per muscle
            for muscle in max_smoothed_mvc_per_muscle.keys():
                if muscle in df_rep.columns:
                    # smoothing
                    rms_smoothing(df_rep, muscle, f"{muscle}_smoothed")
                    # normalization
                    df_rep[f"{muscle}_mvc_percentage"] = df_rep[f"{muscle}_smoothed"].apply(lambda x: np.divide(x, max_smoothed_mvc_per_muscle[muscle])*100)
                    # save stat
                    stat_result[muscle] = {
                        "max_mvc_percentage": df_rep[f"{muscle}_mvc_percentage"].max(),
                        "mean_mvc_percentage": df_rep[f"{muscle}_mvc_percentage"].mean()
                    }
                    logger.info(muscle)
                    logger.info(stat_result[muscle])
            logger.info("===========================")

if __name__ == "__main__":
    # find subject dirs in experiment folder
    subjects = [
        subject
        for subject in os.listdir(os.path.join(output_dir, experiment))
        if os.path.isdir(os.path.join(output_dir, experiment, subject))
    ]
    
    for subject in subjects:
        logger.info(subject)
        normalize_subject(output_dir, experiment, subject, all_mvc_filename_contains, specific_rep, activities)
        logger.info("===========================")
        logger.info("===========================")
        logger.info("===========================")