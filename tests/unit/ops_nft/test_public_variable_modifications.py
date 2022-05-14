import pytest

def test_total_eth_paid_out(
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
    total_eth_paid_out = 0
    for token_id in tokens_to_transfer:
        transfer_tx = nft.safeTransferFrom(
            valid_account, invalid_account, token_id, {"from": valid_account}
        )
        transfer_tx.wait(1)
        
        redemption_tx = nft.redeemEthFromNFT(token_id, {"from": invalid_account})
        redemption_tx.wait(1)

        total_eth_paid_out += redemption_tx.events['Redeemed']['_amount']

    nft_total_eth_paid_out = nft.getTotalEthPaidOut()
    assert total_eth_paid_out == nft_total_eth_paid_out


def test_total_bounty_amount(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft, invalid_account
):
    # Minting a batch of tokens
    number_of_nfts_to_mint = 4
    total_amount_escrowed = 0
    for _ in range(number_of_nfts_to_mint):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": valid_account, "value": amount_to_escrow_in_nft},
        )
        safe_mint_tx.wait(1)
        total_amount_escrowed += safe_mint_tx.events['NFTMinted']['_escrowValue']

    nft_total_bounty_amount = nft.getTotalBountyAmount()
    assert nft_total_bounty_amount == total_amount_escrowed

    # Transfering and redeeming a subset of them
    tokens_to_transfer = [1, 3]
    total_eth_paid_out = 0
    for token_id in tokens_to_transfer:
        transfer_tx = nft.safeTransferFrom(
            valid_account, invalid_account, token_id, {"from": valid_account}
        )
        transfer_tx.wait(1)
        
        redemption_tx = nft.redeemEthFromNFT(token_id, {"from": invalid_account})
        redemption_tx.wait(1)

        total_eth_paid_out += redemption_tx.events['Redeemed']['_amount']
        total_amount_escrowed -= redemption_tx.events['Redeemed']['_amount']

    nft_total_bounty_amount = nft.getTotalBountyAmount()
    assert nft_total_bounty_amount == total_amount_escrowed