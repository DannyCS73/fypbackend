from datetime import datetime as _dt
import hashlib
import hashlib as _hashlib
import json as _json


class Blockchain:
    def __init__(self):
        self.chain = list()
        genesis_block = Block(index=1, timestamp=str(_dt.now()), data="genesis",
                          previous_hash=0, address="0")
        genesis_block.validate_block()
        self.chain.append(genesis_block)

    def get_previous_block(self):
        return self.chain[-1]

    def add_block(self):
        index = len(self.chain) + 1
        validator = "sdknjfbhjdkls"
        new_Block = Block(index=index, timestamp=str(_dt.now()),data="test data",
                          previous_hash=self.get_previous_block().hash, address=validator)
        new_Block.validate_block()
        self.chain.append(new_Block)
        return new_Block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            b1 = self.chain[i-1]
            b2 = self.chain[i]

            if b2.hash != b2.calculateHash():
                return False

            if b2.previous_hash != b1.calculateHash():
                return False
        return True

    def display_chain(self):
        for block in self.chain:
            display = ""
            block_display = f"{block.index}£{block.timestamp}£" \
                            f"{block.hash}£{block.previous_hash}£" \
                            f"{block.address}£#"
            display += block_display
        return display

class Block:
    def __init__(self, index, timestamp, data, previous_hash, address):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.address = address
        self.hash = ''

    def calculateHash(self) -> str:
        block = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "validator": self.address
        }
        encoded_block = _json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def validate_block(self):
        self.hash = self.calculateHash()
        print("Block has been validated")
        return True


class Transaction:
    def __init__(self, receiver, amt):
        self.receiver = receiver
        self.amt = amt


def main():
    bc = Blockchain()
    bc.add_block()
    bc.add_block()

    print(bc.display_chain())

    print(bc.is_chain_valid())

if __name__ == "__main__":
    main()
