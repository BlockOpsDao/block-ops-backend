import pytest


def test_contract_address_is_returned(nft):
    contract_address = None
    if nft.contractAddress():
        contract_address = nft.contractAddress()
    assert (
        contract_address is not None
    ), f"contractAddress is not returning a valid address."
