import hashlib

class Block:
    ''' Single block on blockchain '''
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash

        # hash func
        self.hash = self.hash_func()

    def hash_func(self):
        ''' hashes block '''
        sha = hashlib.sha256()
        sha.update(str(self.index) + 
                   str(self.timestamp) + 
                   str(self.data) + 
                   str(self.prev_hash))
        return sha.hexdigest()
