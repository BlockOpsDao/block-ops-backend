import pytest
from web3 import Web3

@pytest.fixture
def amount_to_escrow_in_nft():
    return Web3.toWei(1, "ether")

@pytest.fixture
def token_metadata_uri():
    return "https://my-nft.metadata/here-is-some-cool-metadata.json"