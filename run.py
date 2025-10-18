import os

from log import logger
import hpf_parser

subject_dir = "./data/subject4/"
parsed_dir = "./output/subject4/"
if_export = True
# if_export = False

if __name__ == "__main__":
    # HPF parser
    entries = [ fname for fname in os.listdir(subject_dir) if fname.endswith(".hpf")]
    for fn in entries:
        # fn = "Subject_#4_BF_Rep_1.3.hpf"
        # fn = "Subject_#4_BFR_80bpm_1_Rep_1.12.hpf"
        fpath = os.path.join(subject_dir, fn)
        logger.info(f"Parsing {fpath}")
        with open(fpath, 'rb') as f:
            try:
                header, ch_info, ch_df = hpf_parser.parse(f)
            except hpf_parser.UnknownHPFChunkTypeError as hpf_p_err:
                logger.error(f"{fpath} not parsable")
                logger.error(hpf_p_err)
                continue
            except:
                logger.error(exc_info=True)
        if if_export:
            with open(f"{parsed_dir}{fn}-header.xml", "w", encoding="utf-8") as out:
                out.write(header)
            with open(f"{parsed_dir}{fn}-ch_info.xml", "w", encoding="utf-8") as out:
                out.write(ch_info)
            ch_df.to_csv(f"{parsed_dir}{fn}-ch_data.csv", index=False, encoding='utf-8-sig') # for degree symbols
            # TODO - validation with Delsys File Utility cmd on Windows
        # break
    
        # TODO Normalizaer
        
        # TODO Stat