// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin-upgradeable/contracts/token/ERC721/ERC721Upgradeable.sol";
import "@openzeppelin-upgradeable/contracts/token/ERC721/extensions/ERC721EnumerableUpgradeable.sol";
import "@openzeppelin-upgradeable/contracts/token/ERC721/extensions/ERC721URIStorageUpgradeable.sol";
import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
import "@openzeppelin-upgradeable/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin-upgradeable/contracts/utils/CountersUpgradeable.sol";

contract OpsNFTUpgradeable is Initializable, ERC721Upgradeable, ERC721EnumerableUpgradeable, ERC721URIStorageUpgradeable, OwnableUpgradeable {
    using CountersUpgradeable for CountersUpgradeable.Counter;

    CountersUpgradeable.Counter private _tokenIdCounter;
    bool public initialized = false;
    
    // maps tokenId to amount of ETH stored in NFT
    mapping(uint256 => uint256) public amountOfEthInNFT;

    event NFTMinted(address _to, string _tokenMetadata, uint256 _escrowValue, uint256 _tokenId);
    event Redeemed(address _redeemer, uint256 _tokenId, uint256 _amount);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() initializer {}

    modifier isInitialized() {
        require(initialized, "Contract is not yet initialized");
        _;
    }

    function initialize() initializer public {
        __ERC721_init("OpsNFTUpgradeable", "OPS");
        __ERC721Enumerable_init();
        __ERC721URIStorage_init();
        __Ownable_init();
    }

    function safeMint(string memory tokenMetadataURI) public onlyOwner payable {
        require(msg.value > 0, "You cannot escrow 0 ETH.");
        require(msg.value < msg.sender.balance, "Insufficient ETH to Escrow.");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, tokenMetadataURI);
        amountOfEthInNFT[tokenId] = msg.value;
        initialized = true;
        emit NFTMinted(msg.sender, tokenMetadataURI, msg.value, tokenId);
    }

    function tokenDetails(uint256 _tokenId) public view returns (address, string memory, uint256, bool) {
        require(_exists(_tokenId), "NFT tokenId does not exist.");
        string memory tokenMetadata = tokenURI(_tokenId);
        uint256 amount = amountOfEthInNFT[_tokenId];
        address nftOwner = ownerOf(_tokenId);
        return (nftOwner, tokenMetadata, amount, initialized);
    }

    function contractAddress() public view returns (address) {
        return address(this);
    }

    function redeemEthFromNFT(uint256 _tokenId) external isInitialized {
        (address nftOwner, string memory tokenMetadata, uint256 amount, bool initialized) = tokenDetails(_tokenId);
        require(nftOwner == msg.sender, "Only the owner of the NFT can redeem the rewards.");
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer Failed.");
        emit Redeemed(msg.sender, _tokenId, amount);
    }

    // The following functions are overrides required by Solidity.

    function _beforeTokenTransfer(address from, address to, uint256 tokenId)
        internal
        override(ERC721Upgradeable, ERC721EnumerableUpgradeable)
    {
        super._beforeTokenTransfer(from, to, tokenId);
    }

    function _burn(uint256 tokenId)
        internal
        override(ERC721Upgradeable, ERC721URIStorageUpgradeable)
    {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721Upgradeable, ERC721URIStorageUpgradeable)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721Upgradeable, ERC721EnumerableUpgradeable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}