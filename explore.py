def readhpf(fname):
    with open(fname, 'rb') as f:
        chunkID = int.from_bytes(f.read(8), byteorder='little')
        h_chunkSize = int.from_bytes(f.read(8), byteorder='little')
        creatorID = f.read(4).decode('CP437')
        file_version =  int.from_bytes(f.read(8), byteorder='little')
        index_chunk_offset =  int.from_bytes(f.read(8), byteorder='little')
        print(chunkID, h_chunkSize, creatorID, file_version, index_chunk_offset)
        
        header_xml = f.read(h_chunkSize - f.tell()).decode('CP437')
        # print(header_xml)
        
        chunkID = int.from_bytes(f.read(8), byteorder='little')
        c_chunkSize = int.from_bytes(f.read(8), byteorder='little')
        groupID = int.from_bytes(f.read(4), byteorder='little')
        num_channels = int.from_bytes(f.read(4), byteorder='little')
        print(chunkID, c_chunkSize, groupID, num_channels)
        
        ch_info_xml = f.read(h_chunkSize+c_chunkSize - f.tell()).decode('CP437')
        # print(ch_info_xml)
        
        chunkID = int.from_bytes(f.read(8), byteorder='little')
        e_def_chunkSize = int.from_bytes(f.read(8), byteorder='little')
        def_count = int.from_bytes(f.read(4), byteorder='little')
        print(chunkID, e_def_chunkSize, def_count)
        
        # TODO - not in xml format
        # print(e_def_xml)
        e_def_xml = f.read(h_chunkSize+c_chunkSize+e_def_chunkSize - f.tell()).decode('CP437')
        
        chunkID = int.from_bytes(f.read(8), byteorder='little')
        d1_chunkSize = int.from_bytes(f.read(8), byteorder='little')
        groupID = int.from_bytes(f.read(4), byteorder='little')
        data_start_idx = int.from_bytes(f.read(8), byteorder='little')
        chan_data_count = int.from_bytes(f.read(4), byteorder='little')
        print(chunkID, d1_chunkSize, groupID, data_start_idx, chan_data_count)
        
        # TODO - skip data chunk
        f.read(h_chunkSize+c_chunkSize+e_def_chunkSize+d1_chunkSize - f.tell())
        
        chunkID = int.from_bytes(f.read(8), byteorder='little')
        d2_chunkSize = int.from_bytes(f.read(8), byteorder='little')
        groupID = int.from_bytes(f.read(4), byteorder='little')
        data_start_idx = int.from_bytes(f.read(8), byteorder='little')
        chan_data_count = int.from_bytes(f.read(4), byteorder='little')
        print(chunkID, d2_chunkSize, groupID, data_start_idx, chan_data_count)
        
        # TODO - skip data chunk
        f.read(h_chunkSize+c_chunkSize+e_def_chunkSize+d1_chunkSize+d2_chunkSize - f.tell())
        
        chunkID = int.from_bytes(f.read(8), byteorder='little')
        idx_chunkSize = int.from_bytes(f.read(8), byteorder='little')
        idxCount = int.from_bytes(f.read(8), byteorder='little')
        print(chunkID, idx_chunkSize, idxCount)
        
        # TODO - skip index chunk
        f.read(h_chunkSize+c_chunkSize+e_def_chunkSize+d1_chunkSize+d2_chunkSize+idx_chunkSize - f.tell())
        
        chunkID = int.from_bytes(f.read(8), byteorder='little')
        print(chunkID)
        
if __name__ == "__main__":
    readhpf("./data/subject4/Subject_#4_BF_Rep_1.3.hpf")