from bitarray import bitarray
import pandas as pd
import numpy as np
from multiprocessing import Pool
from tqdm import tqdm
import logging
import math
from bloom_filter import BloomFilter, jaccard_similarity
from config import HAMMING_THRESHOLD, JACCARD_THRESHOLD, FALSE_POSITIVE_RATE

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# def create_bloom_filters(df):
#     """
#     Create Bloom filters for each record.
#     :param df: DataFrame containing records
#     :return: Dictionary mapping record ID to Bloom filter bit array
#     """
#     num_items = len(df)
#     bloom_filters = {}

#     for _, row in df.iterrows():
#         bf = BloomFilter(num_items=num_items)
#         record_str = f"{row['Name']}{row['Email']}"
#         bf.add(record_str)
#         bloom_filters[row['ID']] = bf.bit_array.copy()

#     logging.info("Created Bloom filters for %d records", num_items)
#     return bloom_filters
def create_bloom_filters(df, fixed_size=None):
    num_items = len(df)
    bloom_filters = {}

    # Use a fixed Bloom filter size for both datasets
    size = fixed_size if fixed_size else int(-num_items * math.log(FALSE_POSITIVE_RATE) / (math.log(2) ** 2))

    for _, row in df.iterrows():
        bf = BloomFilter(num_items=num_items)
        bf.size = size  # Override size to make it consistent
        bf.bit_array = bitarray(size)  # Ensure the same length
        bf.bit_array.setall(0)

        record_str = f"{row['Name']}{row['Email']}"
        bf.add(record_str)
        bloom_filters[row['ID']] = bf.bit_array.copy()

    return bloom_filters

def hamming_distance(bf1, bf2):
    """
    Calculate Hamming distance between two bit arrays.
    """
    return sum(b1 != b2 for b1, b2 in zip(bf1, bf2))

def process_comparison(args):
    """
    Process a single comparison between two bloom filters.
    Returns tuple (id1, id2, hamming_distance, jaccard_similarity)
    """
    id1, bf1, id2, bf2 = args
    ham_dist = hamming_distance(bf1, bf2)
    jaccard = jaccard_similarity(bf1, bf2)
    return (id1, id2, ham_dist, jaccard)

def match_records(df1, df2):
    """
    Match records from two datasets using both Hamming distance and Jaccard similarity.
    Returns list of tuples: (ID1, ID2, hamming_distance, jaccard_similarity)
    """
    fixed_size = int(-max(len(df1), len(df2)) * math.log(FALSE_POSITIVE_RATE) / (math.log(2) ** 2))
    
    bf_dict1 = create_bloom_filters(df1, fixed_size=fixed_size)
    bf_dict2 = create_bloom_filters(df2, fixed_size=fixed_size)

    tasks = [(id1, bf1, id2, bf2) for id1, bf1 in bf_dict1.items() for id2, bf2 in bf_dict2.items()]

    logging.info("Starting matching: comparing %d pairs", len(tasks))

    matches = []
    with Pool() as pool:
        for result in tqdm(pool.imap(process_comparison, tasks), total=len(tasks), desc="Matching records"):
            id1, id2, ham_dist, jaccard = result
            if ham_dist <= 100 or jaccard >= JACCARD_THRESHOLD:
                matches.append((id1, id2, ham_dist, jaccard))

    logging.info("Finished matching. Found %d matches.", len(matches))
    return matches
