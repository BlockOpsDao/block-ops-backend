import pytest


def test_get_array_of_nfts_from_creator(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    number_of_nfts_to_mint = 4
    for _ in range(number_of_nfts_to_mint):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": valid_account, "value": amount_to_escrow_in_nft},
        )
        safe_mint_tx.wait(1)

    address = valid_account.address
    list_of_nfts_created = nft.getArrayOfNFTsFromCreator(address)

    assert list_of_nfts_created == tuple(range(number_of_nfts_to_mint))
    assert len(list_of_nfts_created) == number_of_nfts_to_mint

def test_get_array_of_nfts_from__multiple_creators(
    nft, token_metadata_uri, valid_account, invalid_account, amount_to_escrow_in_nft
):
    number_of_nfts_to_mint = 4
    for _ in range(number_of_nfts_to_mint):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": valid_account, "value": amount_to_escrow_in_nft},
        )
        safe_mint_tx.wait(1)

    for _ in range(number_of_nfts_to_mint):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": invalid_account, "value": amount_to_escrow_in_nft},
        )
        safe_mint_tx.wait(1)

    list_of_nfts_created_by_valid_account = nft.getArrayOfNFTsFromCreator(valid_account.address)
    list_of_nfts_created_by_invalid_account = nft.getArrayOfNFTsFromCreator(invalid_account.address)

    assert list_of_nfts_created_by_valid_account == (0, 1, 2, 3)
    assert list_of_nfts_created_by_invalid_account == (4, 5, 6, 7)

    transfer_tx = nft.safeTransferFrom(invalid_account, invalid_account, 0)
    transfer_tx.wait(1)

def test_get_number_of_open_nfts_from_creator(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft, invalid_account
):
    # Minting a batch of tokens
    number_of_nfts_to_mint = 4
    for _ in range(number_of_nfts_to_mint):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": valid_account, "value": amount_to_escrow_in_nft},
        )
        safe_mint_tx.wait(1)

    # Transfering and redeeming a subset of them
    tokens_to_transfer = [1, 3]
    for token_id in tokens_to_transfer:
        transfer_tx = nft.safeTransferFrom(
            valid_account, invalid_account, token_id, {"from": valid_account}
        )
        transfer_tx.wait(1)

        redemption_tx = nft.redeemEthFromNFT(token_id, {"from": invalid_account})
        redemption_tx.wait(1)

    redeemed_nfts = len(tokens_to_transfer)
    unredeemed_nfts = number_of_nfts_to_mint - redeemed_nfts

    number_of_open_nfts_created_by_valid_account = nft.getNumberOfOpenNFTsFromCreator(
        valid_account.address
    )
    assert number_of_open_nfts_created_by_valid_account == unredeemed_nfts

def test_get_nft_creator(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft, invalid_account
):
    # Minting a batch of tokens
    number_of_nfts_to_mint = 4
    for _ in range(number_of_nfts_to_mint):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": valid_account, "value": amount_to_escrow_in_nft},
        )
        safe_mint_tx.wait(1)

    # Transfering and redeeming a subset of them
    tokens_to_transfer = [1, 3]
    for token_id in tokens_to_transfer:
        transfer_tx = nft.safeTransferFrom(
            valid_account, invalid_account, token_id, {"from": valid_account}
        )
        transfer_tx.wait(1)

        redemption_tx = nft.redeemEthFromNFT(token_id, {"from": invalid_account})
        redemption_tx.wait(1)

    # Checking that our tokenIdToNftCreators array is
    # appropriately populated

    for token_id in range(number_of_nfts_to_mint):
        token_creator = nft.getNFTCreator(token_id)
        assert token_creator == valid_account.address