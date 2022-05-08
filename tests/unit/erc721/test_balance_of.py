import pytest
from brownie import exceptions


def test_balance_of(nft, valid_account, token_metadata_uri, amount_to_escrow_in_nft):
    nft_balance = nft.balanceOf(valid_account)
    assert nft_balance == 0, f"balanceOf does not return the correct number of NFTs."

    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    nft_balance = nft.balanceOf(valid_account)

    assert nft_balance == 1, f"balanceOf does not return the correct number of NFTs."


def test_cannot_get_balance_of_zero_address(nft, zero_address):
    with pytest.raises(exceptions.VirtualMachineError):
        nft.balanceOf(zero_address)
