import brownie
import pytest
from brownie import exceptions


def test_project_state_opens_on_safe_mint(
    nft, valid_account, token_metadata_uri, amount_to_escrow_in_nft
):
    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": valid_account, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        token_id,
        project_state,
        submissions
    ) = nft.tokenDetails(0)
    assert token_id == 0, "Failed to grab the correct tokenId."
    assert project_state == 0, "Project failed to enter project state New."


def test_project_state_closes_on_redemption(
    nft, valid_account, token_metadata_uri, amount_to_escrow_in_nft
):
    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": valid_account, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        token_id,
        project_state,
        submissions
    ) = nft.tokenDetails(0)
    assert token_id == 0, "Failed to grab the correct tokenId."
    assert project_state == 0, "Project failed to enter project state New."

    redemption_tx = nft.redeemEthFromNFT(token_id, {"from": valid_account})
    redemption_tx.wait(1)

    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        token_id,
        project_state,
        submissions
    ) = nft.tokenDetails(0)
    assert token_id == 0, "Failed to grab the correct tokenId."
    assert project_state == 2, "Project failed to enter project state Closed."

def test_submission_makes_project_active(
    nft,
    valid_account,
    invalid_account,
    token_metadata_uri,
    submission_metadata_uri,
    amount_to_escrow_in_nft,
):
    project_creator = valid_account
    developer_submitter = invalid_account

    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": project_creator, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        token_id,
        project_state,
        submissions
    ) = nft.tokenDetails(0)
    assert token_id == 0, "Failed to grab the correct tokenId."
    assert project_state == 0, "Project failed to enter project state New."
    
    submission_tx = nft.makeSubmission(
        0, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()
    
    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        token_id,
        project_state,
        submissions
    ) = nft.tokenDetails(0)
    assert token_id == 0, "Failed to grab the correct tokenId."
    assert project_state == 1, "Project failed to enter project state Active."