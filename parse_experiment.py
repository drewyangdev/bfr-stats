import os
from pathlib import Path

from log import logger
import hpf_parser

## a directory with folders of experiment
data_dir = "./data/"
## a directory for output with folders of experiment
output_dir = "./output/"
## experiment folder name that contains folders of subject data
experiment = "PB TT Tennis no BFR ALL TRIALs"

## options
if_export = True
# if_export = False

if __name__ == "__main__":
    # find subject dirs in experiment folder
    subject_paths = [
        os.path.join(data_dir, experiment, subject) 
        for subject in os.listdir(os.path.join(data_dir, experiment))
        if os.path.isdir(os.path.join(data_dir, experiment, subject))
    ]
    
    # run HPF parser per subject folder
    for subject_path in subject_paths:
        sessions = [ fname for fname in os.listdir(subject_path) if fname.endswith(".hpf")]
        # each subject has multiple sessions
        for fname in sessions:
            fpath = os.path.join(subject_path, fname)
            # parse
            logger.info(f"Parsing {fpath}")
            with open(fpath, 'rb') as f:
                try:
                    header, ch_info, ch_df = hpf_parser.parse(f)
                except hpf_parser.UnknownHPFChunkTypeError as hpf_p_err:
                    logger.error(f"{fpath} not parsable")
                    logger.error(hpf_p_err)
                    continue
                except hpf_parser.DataChunkNotFound as hpf_data_err:
                    logger.error(f"{fpath} missing data chunk")
                    logger.error(hpf_data_err)
                    continue
                except:
                    logger.error(exc_info=True)
            # export
            if if_export:
                parsed_dir = Path(subject_path.replace(data_dir, output_dir))
                if not parsed_dir.exists():
                    parsed_dir.mkdir(parents=True)
                
                with open(os.path.join(parsed_dir, f"{fname}-header.xml"), "w", encoding="utf-8") as out:
                    out.write(header)
                with open(os.path.join(parsed_dir, f"{fname}-ch_info.xml"), "w", encoding="utf-8") as out:
                    out.write(ch_info)
                ch_df.to_csv(os.path.join(parsed_dir, f"{fname}-ch_data.csv"), index=False, encoding='utf-8-sig') # for degree symbols
                # TODO - validation with Delsys File Utility cmd on Windows
            # break
        
            # TODO Normalizaer
            
            # TODO Stat