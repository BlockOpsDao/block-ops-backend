import brownie
import pytest
from web3 import Web3

from scripts.utils import Utils


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.12.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture
def amount_to_escrow_in_nft():
    return Web3.toWei(1, "ether")


@pytest.fixture
def token_metadata_uri():
    return "https://my-nft.metadata/here-is-some-cool-metadata.json"


@pytest.fixture
def submission_metadata_uri():
    return "https://my-submission.metadata/here-is-a-submission.json"


@pytest.fixture(scope="module")
def zero_address():
    return "0x0000000000000000000000000000000000000000"
    # return brownie.accounts.at(_zero_address, force=True)


@pytest.fixture(scope="module")
def valid_account():
    utils = Utils()
    account = utils.get_account()
    return account


@pytest.fixture(scope="module")
def invalid_account():
    utils = Utils()
    account = utils.get_account(1)
    return account


@pytest.fixture(scope="module")
def royalty_account():
    utils = Utils()
    royalty_account = utils.get_royalty_account()
    return royalty_account


@pytest.fixture(scope="module")
def nft(OpsNFT):
    utils = Utils()
    account = utils.get_account()
    return OpsNFT.deploy({"from": account})


@pytest.fixture(scope="module")
def utils():
    return Utils()
