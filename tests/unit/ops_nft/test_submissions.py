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

def test_everyone_can_get_winning_submission(
    nft,
    valid_account,
    invalid_account,
    token_metadata_uri,
    submission_metadata_uri,
    amount_to_escrow_in_nft,
):
    project_creator = valid_account
    developer_submitter = invalid_account
    token_id = 0

    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": project_creator, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    submission_tx = nft.makeSubmission(
        token_id, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": project_creator, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    new_metadata_uri = "https://block-ops.io/ipfs/hereissomecool.stuff"
    submission_tx = nft.makeSubmission(
        token_id, new_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    winning_submission = nft.getWinningSubmissionForTokenId(
        token_id,
        {"from": project_creator}
    )

    winning_submission = nft.getWinningSubmissionForTokenId(
        token_id,
        {"from": developer_submitter}
    )
    

def test_owner_can_declare_winning_submission(
    nft,
    valid_account,
    invalid_account,
    token_metadata_uri,
    submission_metadata_uri,
    amount_to_escrow_in_nft,
):
    project_creator = valid_account
    developer_submitter = invalid_account
    token_id = 0

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
        tokenId,
        project_state,
        submissions
    ) = nft.tokenDetails(token_id)
    assert token_id == tokenId, "Failed to grab the correct tokenId."
    assert project_state == 0, "Project failed to enter project state New."

    submission_tx = nft.makeSubmission(
        token_id, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    new_metadata_uri = "https://block-ops.io/ipfs/hereissomecool.stuff"
    submission_tx = nft.makeSubmission(
        token_id, new_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        tokenId,
        project_state,
        submissions
    ) = nft.tokenDetails(token_id)
    assert token_id == tokenId, "Failed to grab the correct tokenId."
    assert project_state == 1, "Project failed to enter project state Active."

    submission_id = 0
    winning_submission_tx = nft.declareWinningSubmission(
        token_id, 
        submission_id,
        {"from": project_creator}
    )
    winning_submission_tx.wait(1)

    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        tokenId,
        project_state,
        submissions
    ) = nft.tokenDetails(token_id)
    assert token_id == tokenId, "Failed to grab the correct tokenId."
    
    with pytest.raises(exceptions.VirtualMachineError):
        winning_submission_tx = nft.declareWinningSubmission(
            token_id, 
            submission_id,
            {"from": developer_submitter}
        )
        winning_submission_tx.wait(1)

    winning_submission = nft.getWinningSubmissionForTokenId(
        token_id,
        {"from": project_creator}
    )
    
    assert winning_submission[0] == developer_submitter, f'Incorrect submission chosen, submitter: {winning_submission[0]}'
    assert winning_submission[1] == submission_metadata_uri, f'Incorrect submission chosen, metadeata: {winning_submission[1]}'
    assert winning_submission[0] != project_creator, f'Incorrect submission chosen, submitter: {winning_submission[0]}'
    assert winning_submission[1] != new_metadata_uri, f'Incorrect submission chosen, metadeata: {winning_submission[1]}'

def test_ownership_transferred_after_submission(
    nft,
    valid_account,
    invalid_account,
    token_metadata_uri,
    submission_metadata_uri,
    amount_to_escrow_in_nft,
):
    project_creator = valid_account
    developer_submitter = invalid_account
    token_id = 0

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
        tokenId,
        project_state,
        submissions
    ) = nft.tokenDetails(token_id)
    assert token_id == tokenId, "Failed to grab the correct tokenId."
    assert project_state == 0, "Project failed to enter project state New."

    submission_tx = nft.makeSubmission(
        token_id, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    new_metadata_uri = "https://block-ops.io/ipfs/hereissomecool.stuff"
    submission_tx = nft.makeSubmission(
        token_id, new_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    assert "SubmissionMade" in submission_tx.events.keys()

    submission_id = 0
    winning_submission_tx = nft.declareWinningSubmission(
        token_id, 
        submission_id,
        {"from": project_creator}
    )
    winning_submission_tx.wait(1)

    (
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        tokenId,
        project_state,
        submissions
    ) = nft.tokenDetails(token_id)
    assert token_id == tokenId, "Failed to grab the correct tokenId."
    
    winning_submission = nft.getWinningSubmissionForTokenId(
        token_id,
        {"from": project_creator}
    )

    assert nft_owner == developer_submitter, f'Ownership not properly transferred, {nft_owner} | {developer_submitter}'
    assert nft_owner == winning_submission[0], f'Ownership not properly transferred, {nft_owner} | {developer_submitter}'

    initial_developer_balance = developer_submitter.balance()
    redemption_tx = nft.redeemEthFromNFT(
        token_id,
        {"from": developer_submitter}
    )
    redemption_tx.wait(1)
    new_developer_balance = developer_submitter.balance()
    (numerator, denominator) = nft.getRoyaltyNumeratorAndDenominator()
    expected_amount_after_royalty = amount * (1 - (numerator / denominator))
    assert new_developer_balance == initial_developer_balance + expected_amount_after_royalty, f'balance not properly transferred'

    (   
        nft_owner,
        token_metadata,
        amount,
        nft_creator,
        tokenId,
        project_state,
        submissions
    ) = nft.tokenDetails(token_id)
    assert token_id == tokenId, "Failed to grab the correct tokenId."
    assert project_state == 2, "Project failed to enter project state Closed. "

def test_address_mappings_are_updated(
    nft,
    valid_account,
    invalid_account,
    token_metadata_uri,
    submission_metadata_uri,
    amount_to_escrow_in_nft,
):

    project_creator = valid_account
    developer_submitter = invalid_account
    token_id = 0
    submissions_for_token_id_zero = []

    safe_mint_tx = nft.safeMint(
        token_metadata_uri,
        {"from": project_creator, "value": amount_to_escrow_in_nft},
    )
    safe_mint_tx.wait(1)

    submission_tx = nft.makeSubmission(
        token_id, submission_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    submissions_for_token_id_zero.append(
        (developer_submitter, submission_metadata_uri)
    )

    new_metadata_uri = "https://block-ops.io/ipfs/hereissomecool.stuff"
    submission_tx = nft.makeSubmission(
        token_id, new_metadata_uri, {"from": developer_submitter}
    )
    submission_tx.wait(1)
    submissions_for_token_id_zero.append(
        (developer_submitter, new_metadata_uri)
    )

    token_ids_worked_on = nft.getTokenIdsWithSubmissionsFromAddress(
        developer_submitter,
        {"from": developer_submitter}
    )
    assert token_ids_worked_on == (0,0), f'getTokenIdsWithSubmissionsFromAddress not updating correctly: {token_ids_worked_on}'

    developer_submissions = nft.getSubmissionsFromAddressForTokenId(
        developer_submitter,
        token_id,
        {"from": developer_submitter}
    )

    assert developer_submissions == submissions_for_token_id_zero, f'getSubmissionsFromAddressForTokenId is not properly returning submissions: {developer_submissions} |  {submissions_for_token_id_zero}'

    developer_submissions = nft.getSubmissionsFromAddressForTokenId(
        developer_submitter,
        1,
        {"from": developer_submitter}
    )
    assert developer_submissions == ()