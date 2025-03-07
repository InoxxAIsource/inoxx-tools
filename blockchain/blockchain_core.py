"""Core blockchain functionality for the IDE."""
from datetime import datetime
import hashlib
import json
from typing import List, Dict, Any

class Block:
    """Represents a block in the blockchain."""
    def __init__(self, index: int, transactions: List[Dict], timestamp: str, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the hash of the block."""
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """Mine the block with proof of work."""
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    """Simple blockchain implementation."""
    def __init__(self):
        self.chain: List[Block] = []
        self.difficulty = 2
        self.pending_transactions: List[Dict] = []
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create the first block in the chain."""
        genesis_block = Block(0, [], datetime.now().isoformat(), "0")
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain."""
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float) -> None:
        """Add a new transaction to pending transactions."""
        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })

    def mine_pending_transactions(self, miner_reward_address: str) -> Block:
        """Mine pending transactions and add them to a new block."""
        block = Block(
            len(self.chain),
            self.pending_transactions,
            datetime.now().isoformat(),
            self.get_latest_block().hash
        )
        block.mine_block(self.difficulty)
        self.chain.append(block)

        # Reset pending transactions and add miner reward
        self.pending_transactions = [{
            "sender": "network",
            "recipient": miner_reward_address,
            "amount": 1.0,  # Mining reward
            "timestamp": datetime.now().isoformat()
        }]
        
        return block

    def is_chain_valid(self) -> bool:
        """Verify the integrity of the blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verify chain linking
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_balance(self, address: str) -> float:
        """Get the balance of an address."""
        balance = 0.0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction["recipient"] == address:
                    balance += transaction["amount"]
                if transaction["sender"] == address:
                    balance -= transaction["amount"]
        return balance
