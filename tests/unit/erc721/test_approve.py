import pytest
from brownie import exceptions


def test_no_approver_for_nonexistent_token(nft):
    token_id = 0
    with pytest.raises(exceptions.VirtualMachineError):
        nft.getApproved(token_id)


def test_can_not_approve_a_token_that_does_not_exist(nft, valid_account):
    token_id = 0
    with pytest.raises(exceptions.VirtualMachineError):
        nft.approve(valid_account, token_id)
        approved = True


def test_valid_account_can_approve(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account, invalid_account
):
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    nft.approve(invalid_account, token_id)


def test_default_approver_is_zero_address(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account, zero_address
):
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    default_approver = nft.getApproved(token_id)
    assert (
        default_approver == zero_address
    ), f"""default approver is not the zero address
    default_approver: {default_approver}
    zero_address: {zero_address}
    """


def test_invalid_account_can_not_transfer_without_approval(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account, invalid_account
):
    # Mint a new token
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    # Test that the invalid_account can't transfer the Token
    # from the valid_account to itself without first being
    # set as an approver.
    with pytest.raises(exceptions.VirtualMachineError):
        safe_transfer_from_tx = nft.safeTransferFrom(
            valid_account, invalid_account, token_id, {"from": invalid_account}
        )
        safe_transfer_from_tx.wait(1)


def test_invalid_account_can_transfer_after_approval(
    nft, token_metadata_uri, amount_to_escrow_in_nft, valid_account, invalid_account
):

    # Mint a new token
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    # valid_account sets invalid_account as an approver
    nft.approve(invalid_account, token_id, {"from": valid_account})
    approver = nft.getApproved(token_id)
    assert (
        approver == invalid_account
    ), f"approver was not properly set to invalid_account"

    # Now invalid_account is able to transfer the account from the
    # valid_account to the invalid_account
    safe_transfer_from_tx = nft.safeTransferFrom(
        valid_account, invalid_account, token_id, {"from": invalid_account}
    )
    safe_transfer_from_tx.wait(1)

    assert (
        "Approval" in safe_transfer_from_tx.events.keys()
    ), f"""
    Approval event not emitted.
    """


def test_approve_permissions_reset_after_transfer(
    nft,
    token_metadata_uri,
    amount_to_escrow_in_nft,
    valid_account,
    invalid_account,
    zero_address,
):
    # Mint a new token
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    # valid_account sets invalid_account as an approver
    nft.approve(invalid_account, token_id, {"from": valid_account})
    original_approver = nft.getApproved(token_id)
    assert (
        original_approver == invalid_account
    ), f"approver was not properly set to invalid_account"

    # Now invalid_account is able to transfer the account from the
    # valid_account to the invalid_account
    safe_transfer_from_tx = nft.safeTransferFrom(
        valid_account, invalid_account, token_id, {"from": invalid_account}
    )
    safe_transfer_from_tx.wait(1)

    new_approver = nft.getApproved(token_id)
    assert (
        new_approver != original_approver
    ), f"""
    approver is not being reset after transfer.
    original_approver: {original_approver}
    new_approver: {new_approver}  
    """

    assert (
        new_approver == zero_address
    ), f"""
    new_approver not reset to zero_address:
    new_approver: {new_approver}
    zero_address: {zero_address}
    """


def test_to_can_not_be_owner(
    nft,
    token_metadata_uri,
    amount_to_escrow_in_nft,
    valid_account,
    invalid_account,
    zero_address,
):

    # Mint a new token
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)

    with pytest.raises(exceptions.VirtualMachineError):
        nft.approve(valid_account, token_id, {"from": valid_account})


def test_msg_sender_must_be_owner_or_approved_for_all(
    nft,
    token_metadata_uri,
    amount_to_escrow_in_nft,
    valid_account,
    invalid_account,
):

    # Mint a new token
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    is_approved_for_all = nft.isApprovedForAll(
        valid_account, invalid_account, {"from": invalid_account}
    )
    assert (
        is_approved_for_all == False
    ), f"invalid user was set as ApproveForAll before call."

    with pytest.raises(exceptions.VirtualMachineError):
        nft.approve(valid_account, token_id, {"from": invalid_account})

    nft.approve(invalid_account, token_id, {"from": valid_account})


def test_valid_account_can_set_approval_for_all(
    nft,
    token_metadata_uri,
    amount_to_escrow_in_nft,
    valid_account,
    invalid_account,
):
    # Mint a new token
    token_id = 0
    safe_mint_tx = nft.safeMint(
        token_metadata_uri, {"from": valid_account, "value": amount_to_escrow_in_nft}
    )
    safe_mint_tx.wait(1)
    is_approved_for_all = nft.isApprovedForAll(
        valid_account, invalid_account, {"from": invalid_account}
    )
    assert (
        is_approved_for_all == False
    ), f"invalid user was set as ApproveForAll before call."

    set_approval_for_all_tx = nft.setApprovalForAll(
        invalid_account, True, {"from": valid_account}
    )
    set_approval_for_all_tx.wait(1)

    is_approved_for_all = nft.isApprovedForAll(
        valid_account, invalid_account, {"from": invalid_account}
    )
    assert (
        is_approved_for_all == True
    ), f"invalid user was not set as ApproveForAll before call."
