import pytest
from brownie import exceptions


def test_can_not_return_token_uri_on_nonexistent_token(nft):
    token_id = 0
    with pytest.raises(exceptions.VirtualMachineError):
        token_uri = nft.tokenURI(token_id)


def test_can_return_token_uri(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account
):
    token_id = 0
    token_uri = None
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    token_uri = nft.tokenURI(token_id, {"from": valid_account})
    assert isinstance(
        token_uri, str
    ), f"tokenURI does not return a string: {type(token_uri)}"
    assert token_uri is not None, f"tokenURI returned a value."
    assert token_uri == token_metadata_uri, f"tokenURI not set correctly."
