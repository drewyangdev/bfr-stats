# Most of the logic is referenced from: https://github.com/jogrundy/Read_QuickDAQ_.hpf/blob/master/read_hpf.py
# by following this spec: https://github.com/abougouffa/m2hpf/blob/master/high_performance_file_format_spec.pdf
# Some changes are made for parsing EMGWorks data
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize) 
import pandas as pd
import re
import xml.dom.minidom as minidom

from log import logger

CHUNK_TYPE = {
    4096: "header", # Header chunk ID 0x1000
    8192: "ch_info", # Channel Information chunk ID 0x2000
    12288: "data", # Chunk ID 0x3000
    16384: "event_def", #  chunk ID 0x4000
    20840: "event_data", # Chunk ID 0x5000
    24576: "idx",# ChunkID 0x6000
    # 28672: "undefined", # Chunk ID 0x7000 ? not in documentation.
    # 32768: "undefined", # Chunk ID 0x8000
    # 36864: "undefined", # Chunk ID 0x9000
    # 40960: "undefined", # Chunk ID 0xA000
}

# In case a corrupted hpf file
class UnknownHPFChunkTypeError(Exception):
        def __init__(self, value, message="Chunk ID {chunkID} isn't on the list, known chunk ids are {CHUNK_TYPE}"):
            self.value = value
            self.message = message.format(chunkID=value, CHUNK_TYPE=CHUNK_TYPE)
            super().__init__(self.message)

class DataChunkNotFound(Exception):
        def __init__(self, value, message="'data' chunk is missing from HPF file, only found these chunks: {is_chunk_found}."):
            self.value = value
            self.message = message.format(is_chunk_found=value)
            super().__init__(self.message)

def read_int64(f):
    return int.from_bytes(f.read(8), byteorder='little')

def read_int32(f):
    return int.from_bytes(f.read(4), byteorder='little')

def parse(f):
    chunkID = -1
    chunkHead = 0
    is_chunk_found = dict.fromkeys(CHUNK_TYPE.values(), False)
    while chunkID != 0:
        chunkID = read_int64(f)
        if chunkID == 0:
            # EOF
            break
        if chunkID not in CHUNK_TYPE:
            raise UnknownHPFChunkTypeError(chunkID)
        chunkType = CHUNK_TYPE[chunkID]
        chunkSize = read_int64(f)
        logger.info(f"chunkID {chunkID} {chunkType} chunkSize {chunkSize}")
        
        if chunkType == "header":
            creatorID = f.read(4).decode('CP437')
            file_version =  read_int64(f)
            index_chunk_offset =  read_int64(f)
            header_xml = f.read(chunkHead+chunkSize - f.tell()).decode('utf-8')
            # logger.debug(header_xml)
            header_xml = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", header_xml)
            pretty_header = minidom.parseString(header_xml).toprettyxml(indent="  ")
            # logger.debug(pretty_header)
        elif chunkType == "ch_info":
            groupID = read_int32(f)
            num_channels = read_int32(f)
            raw_ch_info_xml = f.read(chunkHead+chunkSize - f.tell()).decode('utf-8')
            # logger.debug(ch_info_xml)
            raw_ch_info_xml = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", raw_ch_info_xml)
            ch_info_xml = minidom.parseString(raw_ch_info_xml)
            pretty_ch_info = ch_info_xml.toprettyxml(indent="  ")
            # logger.debug(pretty_ch_info)
            
            # ch_info xml -> list
            ch_infos = []
            ch_names = []
            time_col_names = []
            for ch in ch_info_xml.getElementsByTagName("ChannelInformation"):
                info = {}
                for node in ch.childNodes:
                    if node.nodeType == node.ELEMENT_NODE:
                        info[node.tagName] = node.firstChild.nodeValue if node.firstChild else None
                ch_infos.append(info)
                # channel column names
                ch_name = f'{info["Name"]} [{info["Unit"]}]'
                ch_names.append(ch_name)
                # logger.info(f'{ch_name} type:{info["DataType"]} min:{info["RangeMin"]} max:{info["RangeMin"]} sample_rate:{info["PerChannelSampleRate"]}')
                # time column names
                time_col_names.append("X [s]")
                # only seen float32 for now, but check data type for the next arry dtype=np.float32
                if info["DataType"] != "Float":
                    logger.warning(f"{ch_name} isn't in Float, currently hardcoding np.float32, need to improve logic")
            # logger.debug(ch_infos)
            
            # prep for parsing data chunk
            chan_data = [np.empty(0, dtype=np.float32) for i in range(num_channels)] # from ch_info
        elif chunkType == "data":
            groupID = read_int32(f)
            data_start_idx = read_int64(f)
            chan_data_count = read_int32(f)
            ch_des = np.zeros((chan_data_count, 2), dtype='int')
            for count in range(chan_data_count):
                ch_des[count, 0] = read_int32(f) # channel Offset
                ch_des[count, 1] = read_int32(f) # channel length, this length / 4(int32) = num of rows per channel
            # logger.debug(ch_des)
            for count in range(chan_data_count):
                f.seek(chunkHead+ch_des[count, 0])
                # dat = array.array('f',f.read(ch_des[count,1])) # this matches with exported data
                arr = np.frombuffer(f.read(ch_des[count,1]), dtype=np.float32) # 32 bit per data
                chan_data[count] = np.append(chan_data[count], arr)
            # logger.debug(chan_data)
            f.seek(chunkHead)
            f.read(chunkHead+chunkSize - f.tell())
        elif chunkType == "event_def":
            def_count = read_int32(f)
            # not in xml format
            # looks like not very useful, ignore
            e_def_xml = f.read(chunkHead+chunkSize - f.tell()).decode('CP437')
            # logger.debug(e_def_xml)
        elif chunkType == "event_data":
            # didn't find any event data, skip
            f.read(chunkHead+chunkSize - f.tell())
            logger.warning("Skip event_data")
        elif chunkType == "idx":
            idxCount = read_int64(f)
            idxes = []
            for _ in range(idxCount):
                idx = dict(
                    dataStartIndex=read_int64(f), # 18446744073709551615 is -1, means not a data chunk
                    perChDataLengInSample=read_int64(f), # num of rows per channel
                    chunkID=read_int64(f),
                    groupID=read_int64(f),
                    fileOffset=read_int64(f) # chunk start head
                )
                # logger.debug(idx)
                idxes.append(idx)
        else:
            break
        
        is_chunk_found[chunkType] = True
        chunkHead += chunkSize
        # logger.debug(f"chunkHead {chunkHead}")

    if not is_chunk_found["data"]:
        raise DataChunkNotFound(is_chunk_found)
        
    # time is calculated by (1 sec / PerChannelSampleRate) per record in ch_info
    time_col = []
    for i in range(chan_data_count):
        time_step = 1/float(ch_infos[i]["PerChannelSampleRate"])
        rough_time_col = np.arange(0, len(chan_data[i]) * time_step, time_step)
        # numpy: except in some cases where step is not an integer and 
        # floating point round-off affects the length of out
        if len(rough_time_col) > len(chan_data[i]):
            rough_time_col = rough_time_col[:len(chan_data[i])]
        time_col.append(rough_time_col)
    # merge time_col_names, ch_names; time_col, chan_data;
    merged_col_names = []
    merged_data = []
    for i in range(chan_data_count):
        merged_col_names.append(time_col_names[i])
        merged_col_names.append(ch_names[i])
        merged_data.append(time_col[i])
        merged_data.append(chan_data[i])
        
    ch_df = pd.DataFrame(np.column_stack(merged_data), columns=merged_col_names)
    
    return pretty_header, pretty_ch_info, ch_df