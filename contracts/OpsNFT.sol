// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/// @custom:security-contact block-ops.eth
contract OpsNFT is ERC721, ERC721Enumerable, ERC721URIStorage, ERC721Royalty, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;
    bool public initialized = false;
    address public royaltyAddress = 0x2615e4520418848893f9F0d69Ecc84084119D0E5;
    uint8 public royaltyNumerator = 100;
    
    // NFT data

    // maps tokenId to amount of ETH stored in NFT
    mapping(uint256 => uint256) public amountOfEthInNFT;
    mapping(uint256 => address) public nftCreators;

    event NFTMinted(address _to, string _tokenMetadata, uint256 _escrowValue, uint256 _tokenId);
    event Redeemed(address _redeemer, uint256 _tokenId, uint256 _amount);
    event RoyaltyPaid(address _to, uint256 _amount);
    
    constructor() ERC721("OpsNFT", "OPS") {
        _setDefaultRoyalty(royaltyAddress, royaltyNumerator);
    }

    modifier isInitialized() {
        require(initialized, "Contract is not yet initialized");
        _;
    }

    function safeMint(string memory tokenMetadataURI) public onlyOwner payable {
        // TODO: Implement way for owner to set a custom royalty value
        //       to satisfy the future use case of providing 
        //       consulting services in exchange for a higher % of the 
        //       total contract value instead of an additional out-of-
        //       pocket fee.
        require(msg.value > 0, "You cannot escrow 0 ETH.");
        require(msg.value < msg.sender.balance, "Insufficient ETH to Escrow.");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, tokenMetadataURI);

        uint256 royaltyAmount = _payOutRoyalty(tokenId, msg.value);
        uint256 amountToEscrow = msg.value - royaltyAmount;
        amountOfEthInNFT[tokenId] = amountToEscrow;
        nftCreators[tokenId] = msg.sender;
        initialized = true;
        emit NFTMinted(msg.sender, tokenMetadataURI, amountToEscrow, tokenId);

    }
    
    function _payOutRoyalty(uint256 _tokenId, uint256 _nftSaleAmount) internal returns (uint256) {
        (address royaltyAddress, uint256 royaltyAmount) = royaltyInfo(_tokenId, _nftSaleAmount);
        (bool success, ) = royaltyAddress.call{value: royaltyAmount}("");
        require(success, "Royalty Transfer Failed.");
        emit RoyaltyPaid(royaltyAddress, royaltyAmount);
        return royaltyAmount;
    }

    function tokenDetails(uint256 _tokenId) public view returns (address, string memory, uint256, address) {
        require(_exists(_tokenId), "NFT tokenId does not exist.");
        string memory tokenMetadata = tokenURI(_tokenId);
        uint256 amount = amountOfEthInNFT[_tokenId];
        address nftOwner = ownerOf(_tokenId);
        address nftCreator = nftCreators[_tokenId];
        return (nftOwner, tokenMetadata, amount, nftCreator);
    }

    function contractAddress() public view returns (address) {
        return address(this);
    }

    function redeemEthFromNFT(uint256 _tokenId) external isInitialized {
        (address nftOwner, string memory tokenMetadata, uint256 amount, address nftCreator) = tokenDetails(_tokenId);
        require(nftOwner == msg.sender, "Only the owner of the NFT can redeem the rewards.");

        uint256 royaltyAmount = _payOutRoyalty(_tokenId, amount);
        uint256 amountToPayOut = amount - royaltyAmount;

        (bool success, ) = msg.sender.call{value: amountToPayOut}("");
        require(success, "Transfer Failed.");
        emit Redeemed(msg.sender, _tokenId, amount);
    } 

    function getAmountStoredInNFT(uint256 _tokenId) public view returns (uint256) {
        return amountOfEthInNFT[_tokenId];
    }

    function getNFTCreator(uint256 _tokenId) public view returns (address) {
        return nftCreators[_tokenId];
    }

    // The following functions are overrides required by Solidity.

    function _beforeTokenTransfer(address from, address to, uint256 tokenId)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._beforeTokenTransfer(from, to, tokenId);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage, ERC721Royalty) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721Royalty)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

