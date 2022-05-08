import pytest


def test_get_nft_creator_returns_proper_owner(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    token_id = 0
    original_nft_creator = nft.getNFTCreator(token_id)
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    nft_creator = nft.getNFTCreator(token_id)
    assert (
        original_nft_creator != nft_creator
    ), f"nftCreators is not being properly updated\noriginal_nft_creator: {original_nft_creator}\nnft_creator: {nft_creator}"

    assert (
        nft_creator == valid_account
    ), f"nftCreators is not being properly updated\nvalid_account: {valid_account}\nnft_creator: {nft_creator}"
