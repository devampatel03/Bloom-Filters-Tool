import numpy as np
from multiprocessing import Pool
from bloom_filter import BloomFilter

def create_bloom_filters(df):

    bf = BloomFilter(num_items=len(df))
    bloom_filters = {}
    
    for _, row in df.iterrows():
        record_str = f"{row['Name']}{row['Email']}"  # Combine key fields
        bf.add(record_str)
        bloom_filters[row['ID']] = bf.bit_array.copy()  # Store copy of the bit array
    
    return bloom_filters

def hamming_distance_parallel(args):

    bf1, bf2 = args
    return sum(b1 != b2 for b1, b2 in zip(bf1, bf2))

def match_records_parallel(df1, df2, threshold=5):

    bf_dict1 = create_bloom_filters(df1)
    bf_dict2 = create_bloom_filters(df2)

    matches = []
    pool = Pool()  # Use multiprocessing for efficiency
    comparisons = [(bf1, bf2) for bf1 in bf_dict1.values() for bf2 in bf_dict2.values()]
    distances = pool.map(hamming_distance_parallel, comparisons)
    pool.close()
    pool.join()

    index = 0
    for id1 in bf_dict1.keys():
        for id2 in bf_dict2.keys():
            if distances[index] <= threshold:
                matches.append((id1, id2))  # Store matched record IDs
            index += 1

    return matches
