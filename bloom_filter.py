import hashlib
import math
from bitarray import bitarray
from config import FALSE_POSITIVE_RATE

class BloomFilter:
    def __init__(self, num_items, false_positive_rate=FALSE_POSITIVE_RATE):
        """
        Initialize Bloom Filter with optimal size and hash functions.
        :param num_items: Expected number of items
        :param false_positive_rate: Desired false positive rate
        """
        self.size = int(-num_items * math.log(false_positive_rate) / (math.log(2) ** 2))
        self.hash_count = max(1, int(self.size / num_items * math.log(2)))
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

    def _hashes(self, item):
        """
        Generate multiple hash values for an item.
        """
        return [int(hashlib.sha256((item + str(i)).encode()).hexdigest(), 16) % self.size for i in range(self.hash_count)]

    def add(self, item):
        """
        Add an item to the Bloom filter.
        """
        for index in self._hashes(item):
            self.bit_array[index] = 1

    def check(self, item):
        """
        Check if an item is possibly in the set.
        """
        return all(self.bit_array[index] for index in self._hashes(item))

def jaccard_similarity(bf1, bf2):
    """
    Compute Jaccard similarity between two bitarrays.
    Jaccard = (Intersection) / (Union)
    """
    intersection = (bf1 & bf2).count()
    union = (bf1 | bf2).count()
    return intersection / union if union != 0 else 0

# Example Usage
if __name__ == "__main__":
    bf = BloomFilter(num_items=1000)
    bf.add("Alice Johnson")
    print("Exists?", bf.check("Alice Johnson"))
