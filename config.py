# config.py

# Bloom Filter parameters
NUM_ITEMS = 1000          # default estimate; will be overwritten based on actual dataset size
FALSE_POSITIVE_RATE = 0.01

# Matching thresholds
HAMMING_THRESHOLD = 10      # maximum Hamming distance to consider a match
JACCARD_THRESHOLD = 0.8    # minimum Jaccard similarity (0 to 1) to consider a match

# Logging configuration
LOG_FILE = 'app.log'
