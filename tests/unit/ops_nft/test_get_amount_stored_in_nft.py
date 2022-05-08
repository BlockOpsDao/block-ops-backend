import pytest


def test_get_amount_stored_in_nft(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    token_id = 0
    _, royalty_amount = nft.royaltyInfo(token_id, amount_to_escrow_in_nft)
    amount_to_escrow_minus_royalty_fee = amount_to_escrow_in_nft - royalty_amount

    amount_escrowed = nft.getAmountStoredInNFT(0)
    assert (
        amount_escrowed == amount_to_escrow_minus_royalty_fee
    ), f"Amount escrowed in NFT is not equal to the submitted amount minus the royalty fee\namount_escrowed: {amount_escrowed}\namount_to_escrow_minus_royalty_fee: {amount_to_escrow_minus_royalty_fee}"
