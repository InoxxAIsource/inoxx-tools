"""Smart contract development utilities."""
from pathlib import Path
import json
from typing import Dict, Any, Optional
from solcx import compile_standard, install_solc
from web3 import Web3

class SmartContractDeveloper:
    """Utility class for smart contract development."""
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
        self._ensure_solc_installed()

    def _ensure_solc_installed(self, version: str = "0.8.0") -> None:
        """Ensure the specified version of solc is installed."""
        try:
            install_solc(version)
        except Exception as e:
            print(f"Warning: Could not install solc {version}: {e}")

    def compile_contract(self, source_code: str, contract_name: str) -> Dict[str, Any]:
        """Compile a Solidity smart contract."""
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {
                f"{contract_name}.sol": {
                    "content": source_code
                }
            },
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["metadata", "evm.bytecode", "evm.sourceMap", "abi"]
                    }
                }
            }
        })
        return compiled_sol

    def deploy_contract(self, compiled_contract: Dict[str, Any], contract_name: str) -> Dict[str, Any]:
        """Deploy a compiled contract to the blockchain."""
        try:
            # Get contract data
            contract_data = compiled_contract['contracts'][f"{contract_name}.sol"][contract_name]
            bytecode = contract_data['evm']['bytecode']['object']
            abi = json.loads(contract_data['metadata'])['output']['abi']

            # Get deployment account
            accounts = self.w3.eth.accounts
            if not accounts:
                raise ValueError("No accounts available for deployment")
            deployer_account = accounts[0]

            # Create contract instance
            Contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

            # Build and send deployment transaction
            transaction = Contract.constructor().build_transaction({
                'from': deployer_account,
                'nonce': self.w3.eth.get_transaction_count(deployer_account),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key='your-private-key')
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                "success": True,
                "contract_address": tx_receipt.contractAddress,
                "transaction_hash": tx_hash.hex(),
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def save_contract_artifacts(self, 
                              compiled_contract: Dict[str, Any], 
                              contract_name: str, 
                              output_dir: str = "contracts") -> None:
        """Save compiled contract artifacts."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        with open(output_path / f"{contract_name}.json", "w") as f:
            json.dump(compiled_contract, f, indent=2)

    def verify_contract(self, source_code: str) -> Dict[str, Any]:
        """Verify contract syntax and return any errors."""
        try:
            # Attempt to compile the contract
            result = self.compile_contract(source_code, "VerificationTest")
            return {"valid": True, "errors": None}
        except Exception as e:
            return {"valid": False, "errors": str(e)}

    def estimate_gas(self, compiled_contract: Dict[str, Any]) -> Optional[int]:
        """Estimate gas cost for contract deployment."""
        try:
            bytecode = compiled_contract["contracts"]["contract"]["bytecode"]
            return self.w3.eth.estimate_gas({"data": bytecode})
        except Exception as e:
            print(f"Error estimating gas: {e}")
            return None

    def get_contract_interface(self, source_code: str) -> Dict[str, Any]:
        """Generate a contract interface description."""
        try:
            compiled = self.compile_contract(source_code, "Interface")
            abi = compiled["contracts"]["Interface.sol"]["Interface"]["metadata"]
            return json.loads(abi)
        except Exception as e:
            print(f"Error generating interface: {e}")
            return {}