import pytest
from brownie import exceptions


def test_redeem_requires_initialization(nft):
    initialized = nft.initialized()
    assert initialized == False

    with pytest.raises(exceptions.VirtualMachineError):
        nft.redeemEthFromNFT(0)


def test_redeem_can_only_be_called_by_owner(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account, invalid_account
):

    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    token_id = 0
    assert nft.ownerOf(token_id) == valid_account
    with pytest.raises(exceptions.VirtualMachineError):
        redemption_tx = nft.redeemEthFromNFT(token_id, {"from": invalid_account})
        redemption_tx.wait(1)

    redemption_tx = nft.redeemEthFromNFT(token_id, {"from": valid_account})
    redemption_tx.wait(1)

    assert "Redeemed" in redemption_tx.events.keys()


def test_redeems_correct_amount_of_eth(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account, invalid_account
):

    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    token_id = 0
    _, royalty_amount = nft.royaltyInfo(token_id, amount_to_escrow_in_nft)
    amount_to_escrow_minus_royalty_fee = amount_to_escrow_in_nft - royalty_amount
    royalty_fraction = royalty_amount / amount_to_escrow_in_nft
    assert amount_to_escrow_minus_royalty_fee == nft.balance()
    assert royalty_fraction >= 0, f"royalty_fraction is negative: {royalty_fraction}"

    _, royalty_amount_on_redemption = nft.royaltyInfo(token_id, nft.balance())
    amount_of_eth_to_be_redeemed = nft.balance() - royalty_amount_on_redemption

    # amount the redeemer redeems is the original escrowed amount
    # minues 1% at the time of minting and 1% at the time of
    # redemption.
    assert (
        amount_of_eth_to_be_redeemed
        == amount_to_escrow_in_nft * (1 - royalty_fraction) ** 2
    )


def test_account_balances_are_correct(
    nft,
    token_metadata_uri,
    amount_to_escrow_in_nft,
    valid_account,
    invalid_account,
    royalty_account,
):
    # grabbing initial account balances so we can check that
    # the are being changed accordingly.
    minter_beginning_balance = valid_account.balance()
    redeemer_beginning_balance = invalid_account.balance()
    royalty_beginning_balance = royalty_account.balance()
    nft_beginning_balance = nft.balance()

    assert minter_beginning_balance == redeemer_beginning_balance
    assert nft_beginning_balance == 0
    assert royalty_beginning_balance == 0

    # Minting moves funds from the minters account to
    # the NFT.
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    token_id = 0
    _, minted_royalty_amount = nft.royaltyInfo(token_id, amount_to_escrow_in_nft)
    amount_to_escrow_minus_royalty_fee = amount_to_escrow_in_nft - minted_royalty_amount
    royalty_fraction = minted_royalty_amount / amount_to_escrow_in_nft
    assert royalty_fraction >= 0, f"royalty_fraction is negative: {royalty_fraction}"

    # asserting that the minters account has been deducted by
    # amount_to_escrow_in_nft
    assert minter_beginning_balance - valid_account.balance() == amount_to_escrow_in_nft

    # asserting that the nft balance has been increased
    # by amount_to_escrow_in_nft minus the minted_royalty_amount
    assert amount_to_escrow_minus_royalty_fee == nft.balance()

    # asserting that the royalty_address balance has been
    # increased by the royalty amount.
    assert (
        royalty_account.balance() == minted_royalty_amount + royalty_beginning_balance
    )

    # We pretend the job has been completed, so the
    # NFT is transfered to the redeemers account.
    transfer_tx = nft.safeTransferFrom(
        valid_account, invalid_account, token_id, {"from": valid_account}
    )
    transfer_tx.wait(1)
    assert "Transfer" in transfer_tx.events.keys()
    assert nft.ownerOf(token_id) == invalid_account

    # Now we calculate what the new royalty fee is.
    _, redeemed_royalty_amount = nft.royaltyInfo(token_id, nft.balance())

    # Now we redeem the NFT
    redemption_tx = nft.redeemEthFromNFT(token_id, {"from": invalid_account})
    redemption_tx.wait(1)
    assert "RoyaltyPaid" in redemption_tx.events.keys()
    assert "Redeemed" in redemption_tx.events.keys()

    minter_final_balance = valid_account.balance()
    redeemer_final_balance = invalid_account.balance()
    royalty_account_final_balance = royalty_account.balance()
    nft_final_balance = nft.balance()

    # assert that the minter's final balance is equal to
    # their initial balance minus amount_to_escrow_in_eth
    assert minter_final_balance == minter_beginning_balance - amount_to_escrow_in_nft

    # assert that the redeemer's final balance is equal
    # to their starting balance plus the amount_to_escrow_in_eth
    # minus the 1% royalty, minus another 1% royalty.
    assert redeemer_final_balance == redeemer_beginning_balance + (
        amount_to_escrow_in_nft * (1 - royalty_fraction) ** 2
    )
    assert (
        redeemer_final_balance
        == redeemer_beginning_balance
        + amount_to_escrow_in_nft
        - minted_royalty_amount
        - redeemed_royalty_amount
    )

    # assert that the royalty's final balance received both
    # the royalty fee from minting and the royalty fee from
    # redeeming.
    assert (
        royalty_account.balance()
        == royalty_beginning_balance + minted_royalty_amount + redeemed_royalty_amount
    )

    # assert that there are no remaining funds left in the NFT.
    assert nft.balance() == 0

