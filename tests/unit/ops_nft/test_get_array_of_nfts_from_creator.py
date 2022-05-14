import pytest

def test_get_array_of_nfts_from_creator(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    number_of_nfts_to_mint = 4
    for _ in range(number_of_nfts_to_mint):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
        )
        safe_mint_tx.wait(1)
    
    address = valid_account.address
    list_of_nfts_created = nft.getArrayOfNFTsFromCreator(address)
    # number_of_open_nfts = nft.getNumberOfOpenNFTsFromCreator(address)

    assert len(list_of_nfts_created) == number_of_nfts_to_mint
    