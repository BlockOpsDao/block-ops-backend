import os

from brownie import Contract, accounts, config, network, web3
from web3 import Web3

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]
OPENSEA_TESTNET_URL = "https://testnets.opensea.io/assets"


class Utils:
    def __init__(
        self,
        non_forked_local_blockchain_environments: list = [
            "hardhat",
            "development",
            "ganache",
        ],
        local_blockchain_environments: list = [
            "hardhat",
            "development",
            "ganache",
            "mainnet-fork",
            "binance-fork",
            "matic-fork",
        ],
        opensea_testnet_url: str = "https://testnets.opensea.io/assets",
    ):
        self.non_forked_local_blockchain_environments = (
            non_forked_local_blockchain_environments
        )
        self.local_blockchain_environments = local_blockchain_environments
        self.opensea_testnet_url = opensea_testnet_url

        self.active_network = network.show_active()

    def get_account(self, index: int = None, id: int = None):
        """
        Given an optional index or id, this method checks to see
        what environment our code is running on and either grabs
        a dummy account or pulls a specified account given either
        the index or id.

        Arguments:
            index (int): Index of an account to return from the
                         accounts array.
            id (int): The id of an account to be loaded and returned.

        Returns:
            brownie.network.accounts: Brownie account.

        """
        if index:
            return accounts[index]
        if self.active_network in self.local_blockchain_environments:
            return accounts[0]
        if id:
            return accounts.load(id)
        return accounts.add(config["wallets"]["from_key"])

    def get_royalty_account(self, royalty_account_env_var: str = "PUBLIC_KEY"):
        """
        Given the name of an environment variable, retrieves
        the value of that variable and returns it.

        Arguments:
            royalty_account_env_var (str): The environment variable that holds
                                           the value of the royalty accounts
                                           public key.

        Returns:
            str: The public key of the royalty account.
        """

        royalty_address = os.getenv(royalty_account_env_var)
        royalty_account = accounts.at(royalty_address, force=True)
        return royalty_account

    def get_contract(self, contract_name: str):
        """If you want to use this function, go to the brownie config and add a new entry for
        the contract that you want to be able to 'get'. Then add an entry in the variable 'contract_to_mock'.
        You'll see examples like the 'link_token'.
            This script will then either:
                - Get a address from the config
                - Or deploy a mock to use for a network that doesn't have it

        Arguments:
            contract_name (str): This is the name that is referred to in the
            brownie config and 'contract_to_mock' variable.

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictionary. This could be either
            a mock or the 'real' contract on a live network.
        """
        contract_type = contract_to_mock[contract_name]
        if self.active_network in self.non_forked_local_blockchain_environments:
            if len(contract_type) <= 0:
                # TODO: Add deploy_mocks() method
                # self.deploy_mocks()
                print("Deployed Mocks")

            contract = contract_type[-1]
        else:
            try:
                contract_address = config["networks"][self.active_network][
                    contract_name
                ]
                contract = Contract.from_abi(
                    contract_type._name, contract_address, contract_type.abi
                )
            except KeyError:
                print(
                    f"{self.active_network} address not found, perhaps you should add it to the config or deploy mocks?"
                )
                print(
                    f"brownie run scripts/deploy_mocks.py --network {self.active_network}"
                )
        return contract
