import pytest
from brownie import exceptions


def test_total_supply_is_zero(
    nft, valid_account, token_metadata_uri, amount_to_escrow_in_nft
):
    assert nft.totalSupply() == 0, f"totalSupply does not start at 0."
    assert (
        nft.balanceOf(valid_account) == 0
    ), f"balanceOf did not initialize at 0 for valid_account"

    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    assert nft.totalSupply() == 1
    assert nft.balanceOf(valid_account) == 1
    assert nft.ownerOf(0) == valid_account


def test_can_not_call__mint_directly(nft, utils, zero_address):

    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    with pytest.raises(AttributeError):
        nft._mint(zero_address, 0)
