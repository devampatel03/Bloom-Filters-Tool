import hashlib
import math
from bitarray import bitarray

class BloomFilter:
    def __init__(self, num_items, false_positive_rate=0.01):
        
        self.size = int(-num_items * math.log(false_positive_rate) / (math.log(2) ** 2))
        self.hash_count = max(1, int(self.size / num_items * math.log(2)))  # At least 1 hash function
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

    def _hashes(self, item):
        return [int(hashlib.sha256((item + str(i)).encode()).hexdigest(), 16) % self.size for i in range(self.hash_count)]

    def add(self, item):
        for index in self._hashes(item):
            self.bit_array[index] = 1

    def check(self, item):
        return all(self.bit_array[index] for index in self._hashes(item))

if __name__ == "__main__":
    bf = BloomFilter(num_items=1000, false_positive_rate=0.01)
    bf.add("Alice Johnson")
    print("Exists?", bf.check("Alice Johnson"))  # Expected: True
    print("Exists?", bf.check("Bob Smith"))  # Expected: False (unless collision occurs)
