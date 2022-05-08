import brownie
import pytest


def test_can_create_ops_nft(nft):
    assert isinstance(nft, brownie.network.contract.ProjectContract)
