import brownie
import pytest
from brownie import Contract, exceptions

from scripts.deploy import deploy_ops_nft, safe_mint_ops_nft
from scripts.utils import Utils


def test_can_create_ops_nft():
    utils = Utils()
    account = utils.get_account()

    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    ops_nft = deploy_ops_nft(account)
    assert isinstance(ops_nft, brownie.network.contract.ProjectContract)


def test_owner_can_mint_ops_nft(token_metadata_uri, amount_to_escrow_in_nft):
    utils = Utils()
    account = utils.get_account()

    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    ops_nft = deploy_ops_nft(account)
    safe_mint_tx = ops_nft.safeMint(
        token_metadata_uri, 
        {"from": account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    assert isinstance(safe_mint_tx, brownie.network.transaction.TransactionReceipt)

def test_non_owner_cannot_mint_ops_nft(token_metadata_uri, amount_to_escrow_in_nft):
    utils = Utils()
    account = utils.get_account()
    non_owner = utils.get_account(index=1)

    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    ops_nft = deploy_ops_nft(account)
    with pytest.raises(exceptions.VirtualMachineError):
        safe_mint_tx = ops_nft.safeMint(
            token_metadata_uri, 
            {"from": non_owner, "value": amount_to_escrow_in_nft}
        )
        safe_mint_tx.wait(1)
    

def test_nft_is_minted_to_proper_user(token_metadata_uri, amount_to_escrow_in_nft):
    utils = Utils()
    account = utils.get_account()
    second_account = utils.get_account(index=1)

    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    ops_nft = deploy_ops_nft(account)
    safe_mint_tx = ops_nft.safeMint(
        token_metadata_uri, 
        {"from": account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    owner_of_nft = ops_nft.ownerOf(0)

    with pytest.raises(AssertionError):
        assert (
            owner_of_nft == second_account
        ), f"Owner of the NFT was set to the incorrect account: owner_of_nft: {owner_of_nft}\naccount: {second_account}"

    assert (
        owner_of_nft == account
    ), f"Owner of the NFT was set to the incorrect account: owner_of_nft: {owner_of_nft}\naccount: {account}"


def test_nft_can_only_be_minted_by_owner(token_metadata_uri, amount_to_escrow_in_nft):
    utils = Utils()
    account = utils.get_account()
    second_account = utils.get_account(index=1)

    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    ops_nft = deploy_ops_nft(account)
    with pytest.raises(exceptions.VirtualMachineError):
        safe_mint_tx = ops_nft.safeMint(
            token_metadata_uri, 
            {"from": second_account, "value": amount_to_escrow_in_nft}
        )
        safe_mint_tx.wait(1)
    safe_mint_tx = ops_nft.safeMint(
        token_metadata_uri, 
        {"from": account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    assert isinstance(safe_mint_tx, brownie.network.transaction.TransactionReceipt) 


def test_token_uri_properly_set(token_metadata_uri, amount_to_escrow_in_nft):
    utils = Utils()
    account = utils.get_account()
    second_account = utils.get_account(index=1)

    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    ops_nft = deploy_ops_nft(account)
    safe_mint_tx = ops_nft.safeMint(
        token_metadata_uri, 
        {"from": account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    nft_token_id = 0
    nft_token_uri_metadata = ops_nft.tokenURI(nft_token_id)
    assert nft_token_uri_metadata == token_metadata_uri, "tokenURI was improperly set"

def test_token_id_properly_increments(token_metadata_uri, amount_to_escrow_in_nft):
    utils = Utils()
    account = utils.get_account()
    if utils.active_network not in utils.local_blockchain_environments:
        pytest.skip()

    ops_nft = deploy_ops_nft(account)
    safe_mint_tx = ops_nft.safeMint(
        token_metadata_uri, 
        {"from": account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)