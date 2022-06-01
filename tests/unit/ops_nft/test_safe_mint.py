import brownie
import pytest
from brownie import exceptions


def test_can_not_escrow_negative_eth(nft, valid_account, token_metadata_uri):
    amount_to_escrow_in_nft = -1
    with pytest.raises(ValueError):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": valid_account, "value": amount_to_escrow_in_nft},
        )
        safe_mint_tx.wait(1)


def test_can_not_escrow_more_than_account_balance(
    nft, valid_account, token_metadata_uri
):
    valid_account_balance = valid_account.balance()
    double_valid_account_balance = valid_account_balance * 2
    with pytest.raises(ValueError):
        safe_mint_tx = nft.safeMint(
            token_metadata_uri,
            {"from": valid_account, "value": double_valid_account_balance},
        )
        safe_mint_tx.wait(1)


def test_can_call_safe_mint_with_valid_account(
    nft, valid_account, token_metadata_uri, amount_to_escrow_in_nft
):
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    assert isinstance(safe_mint_tx, brownie.network.transaction.TransactionReceipt)


def test_nft_is_minted_to_proper_user(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account, invalid_account
):

    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    token_id = 0
    owner_of_nft = nft.ownerOf(token_id)

    with pytest.raises(AssertionError):
        assert (
            owner_of_nft == invalid_account
        ), f"Owner of the NFT was set to the incorrect account: owner_of_nft: {owner_of_nft}\naccount: {invalid_account}"

    assert (
        owner_of_nft == valid_account
    ), f"Owner of the NFT was set to the incorrect account: owner_of_nft: {owner_of_nft}\naccount: {valid_account}"


def test_token_id_properly_increments(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account
):

    # Testing that neither tokenId = 0 nor tokenId = 1
    # exist yet
    with pytest.raises(exceptions.VirtualMachineError):
        token_details = nft.tokenDetails(0)

    with pytest.raises(exceptions.VirtualMachineError):
        token_details = nft.tokenDetails(1)

    # Minting tokenId = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    genesis_token_id = 0
    second_token_id = genesis_token_id + 1

    # Testing that tokenId = 0 does exist and tokenId = 1
    # does not exist
    genesis_token_details = nft.tokenDetails(genesis_token_id)
    with pytest.raises(exceptions.VirtualMachineError):
        token_details = nft.tokenDetails(1)

    # Minting tokenId = 1
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    # Testing that tokenId = 1 now exists.
    second_token_details = nft.tokenDetails(1)


def test_token_uri_properly_set(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account
):

    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    nft_token_id = 0
    nft_token_uri_metadata = nft.tokenURI(nft_token_id)
    assert nft_token_uri_metadata == token_metadata_uri, "tokenURI was improperly set"


def test_amount_is_properly_escrowed(
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


def test_transfer_event_is_emitted(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    assert (
        "Transfer" in safe_mint_tx.events.keys()
    ), f"Transfer Event not emitted during safeMint"


def test_nftminted_event_is_emitted(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    assert (
        "NFTMinted" in safe_mint_tx.events.keys()
    ), f"NFTMinted Event not emitted during safeMint"


def test_royaltypaid_event_is_emitted(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    assert (
        "RoyaltyPaid" in safe_mint_tx.events.keys()
    ), f"RoyaltyPaid Event not emitted during safeMint"


def test_amount_of_eth_in_nft_is_updated(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    original_amount_of_eth_in_nft = nft.getAmountStoredInNFT(0)
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    amount_of_eth_in_nft = nft.getAmountStoredInNFT(0)

    assert (
        amount_of_eth_in_nft > original_amount_of_eth_in_nft
    ), f"amountOfEthInNFT is not being updated.\namount_of_eth_in_nft: {amount_of_eth_in_nft}"


def test_safe_mint_initializes_nft(
    nft, token_metadata_uri, valid_account, amount_to_escrow_in_nft
):
    initialized = nft.initialized()
    assert initialized == False, f"Token is initialized before calling safeMint."

    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    initialized = nft.initialized()
    assert initialized == True, f"Token is not initialized after calling safeMint."
