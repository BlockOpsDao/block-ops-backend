import brownie
import pytest
from brownie import exceptions


def test_can_make_a_submission(
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

    submission_tx = nft.makeSubmission(
        0, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()



def test_submission_event_emits(
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

    submission_tx = nft.makeSubmission(
        0, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    submitter = submission_tx.events['SubmissionMade']['_submitter']
    token_id = submission_tx.events['SubmissionMade']['_tokenId']
    submission_string = submission_tx.events['SubmissionMade']['_submissionString']
    nft_owner = submission_tx.events['SubmissionMade']['_nftOwner']

    assert submitter == developer_submitter, f"Submitter not properly set: {submitter}"
    assert token_id == 0, f"TokenId not properly set: {token_id}"
    assert submission_string == submission_metadata_uri, f"Submission String not properly set: {submission_string}"
    assert nft_owner == project_creator, f"NFTOwner not properly set: {nft_owner}"


    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": project_creator, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    new_metadata_uri = "https://block-ops.io/ipfs/hereissomecool.stuff"
    submission_tx = nft.makeSubmission(
        0, new_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    submitter = submission_tx.events['SubmissionMade']['_submitter']
    token_id = submission_tx.events['SubmissionMade']['_tokenId']
    submission_string = submission_tx.events['SubmissionMade']['_submissionString']
    nft_owner = submission_tx.events['SubmissionMade']['_nftOwner']

    assert submitter == developer_submitter, f"Submitter not properly set: {submitter}"
    assert token_id == 0, f"TokenId not properly set: {token_id}"
    assert submission_string == new_metadata_uri, f"Submission String not properly set: {submission_string}"
    assert nft_owner == project_creator, f"NFTOwner not properly set: {nft_owner}"

def test_get_submissions(
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

    submission_tx = nft.makeSubmission(
        0, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    submitter = submission_tx.events['SubmissionMade']['_submitter']
    token_id = submission_tx.events['SubmissionMade']['_tokenId']
    submission_string = submission_tx.events['SubmissionMade']['_submissionString']
    nft_owner = submission_tx.events['SubmissionMade']['_nftOwner']

    assert submitter == developer_submitter, f"Submitter not properly set: {submitter}"
    assert token_id == 0, f"TokenId not properly set: {token_id}"
    assert submission_string == submission_metadata_uri, f"Submission String not properly set: {submission_string}"
    assert nft_owner == project_creator, f"NFTOwner not properly set: {nft_owner}"

    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": project_creator, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    new_metadata_uri = "https://block-ops.io/ipfs/hereissomecool.stuff"
    submission_tx = nft.makeSubmission(
        0, new_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    submitter = submission_tx.events['SubmissionMade']['_submitter']
    token_id = submission_tx.events['SubmissionMade']['_tokenId']
    submission_string = submission_tx.events['SubmissionMade']['_submissionString']
    nft_owner = submission_tx.events['SubmissionMade']['_nftOwner']

    assert submitter == developer_submitter, f"Submitter not properly set: {submitter}"
    assert token_id == 0, f"TokenId not properly set: {token_id}"
    assert submission_string == new_metadata_uri, f"Submission String not properly set: {submission_string}"
    assert nft_owner == project_creator, f"NFTOwner not properly set: {nft_owner}"

    submissions = nft.getSubmissionsForTokenId(
        0,
        {"from": project_creator}
    )

    assert submissions[0][0] == developer_submitter
    assert submissions[0][1] == submission_metadata_uri
    assert submissions[1][0] == developer_submitter
    assert submissions[1][1] == new_metadata_uri