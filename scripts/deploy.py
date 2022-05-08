import brownie
from brownie import OpsNFT, accounts
from web3 import Web3

from scripts.utils import Utils


def deploy_ops_nft(account: brownie.network.account.Account = None):
    if account is None:
        utils = Utils()
        account = utils.get_account()
    ops_nft = OpsNFT.deploy({"from": account})
    return ops_nft


def safe_mint_ops_nft(
    ops_nft: brownie.network.contract.Contract,
    token_uri_metadata: str,
    amount_of_eth_to_escrow: float,
):
    amount_of_wei_to_escrow = Web3.toWei(amount_of_eth_to_escrow, "ether")
    safe_mint_tx = ops_nft.safeMint(
        token_uri_metadata,
        {"from": account_to_mint_from, "value": amount_of_wei_to_escrow},
    )
    safe_mint_tx.wait(1)
    return safe_mint_tx


def main():
    utils = Utils()
    account = utils.get_account()
    second_account = utils.get_account(index=1)
    royalty_account_public_key = utils.get_royalty_account()
    print(f"\n\n\nroyalty_account_public_key: {royalty_account_public_key}\n\n\n")
    royalty_account = accounts.at(royalty_account_public_key, force=True)

    ops_token = OpsNFT.deploy({"from": account})
    eth_to_escrow_in_nft = 1
    amount_to_escrow_in_nft = Web3.toWei(eth_to_escrow_in_nft, "ether")
    ops_token_tx = ops_token.safeMint(
        "https://block-ops.xyz",
        {"from": account, "value": amount_to_escrow_in_nft},
    )
    ops_token_tx.wait(1)

    token_id = 0
    token_details = ops_token.tokenDetails(token_id)
    print(f"token_details: {token_details}")
    (nft_owner, token_metadata, token_value, initialized) = token_details

    owner_of_tx = ops_token.ownerOf(token_id)
    print(f"account: {account}")
    print(f"second_account: {second_account}")
    print(f"owner_of_tx: {owner_of_tx}")

    ### Transferring NFT to second account
    transfer_tx = ops_token.safeTransferFrom(
        account, second_account, token_id, {"from": account}
    )
    transfer_tx.wait(1)

    token_details = ops_token.tokenDetails(token_id)
    (nft_owner, token_metadata, token_value, initialized) = token_details

    nft_balance = Web3.fromWei(ops_token.balance(), "ether")
    first_account_balance = Web3.fromWei(account.balance(), "ether")
    second_account_balance = Web3.fromWei(second_account.balance(), "ether")
    royalty_account_balance = Web3.fromWei(royalty_account.balance(), "ether")

    print("--------------------")
    print("BEFORE REDEEMING NFT")
    print("---------------------")
    print(f"nft_balance: {nft_balance}")
    print(f"first_account_balance: {first_account_balance}")
    print(f"second_account_balance: {second_account_balance}")
    print(f"royalty_account_balance: {royalty_account_balance}")
    print("\n\n")

    redemption_tx = ops_token.redeemEthFromNFT(token_id, {"from": second_account})
    redemption_tx.wait(1)

    print("-------------")
    print("REDEEMED NFT")
    print("-------------")

    nft_balance = Web3.fromWei(ops_token.balance(), "ether")
    first_account_balance = Web3.fromWei(account.balance(), "ether")
    second_account_balance = Web3.fromWei(second_account.balance(), "ether")
    royalty_account_balance = Web3.fromWei(royalty_account.balance(), "ether")

    print(f"new nft_balance: {nft_balance}")
    print(f"new first_account_balance: {first_account_balance}")
    print(f"new second_account_balance: {second_account_balance}")
    print(f"new royalty_account_balance: {royalty_account_balance}")


if __name__ == "__main__":
    main()
