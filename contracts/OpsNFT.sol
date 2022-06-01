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
    address public _royaltyAddress = 0x2615e4520418848893f9F0d69Ecc84084119D0E5;
    uint8 public royaltyNumerator = 100;
    uint16 public royaltyDenominator = 10000;
    uint256 public totalEthPaidOut = 0;
    uint256 public totalBountyAmount = 0;
    enum PROJECT_STATE {
        NEW,
        ACTIVE,
        CLOSED
    }
    struct Submission {
        address submitter;
        string metadataURI;
    }
    
    mapping(uint256 => uint256) public amountOfEthInNFT;
    mapping(uint256 => address) public tokenIdToNftCreators;
    mapping(address => uint256[]) public openNftsFromCreators;
    mapping(uint256 => PROJECT_STATE) public tokenIdToProjectState;
    mapping(uint256 => Submission[]) public tokenIdToSubmissions;
    mapping(uint256 => Submission) public tokenIdToWinningSubmission;

    event NFTMinted(address _to, string _tokenMetadata, uint256 _escrowValue, uint256 _tokenId);
    event SubmissionMade(address _submitter, uint256 _tokenId, string _submissionString, address _nftOwner);
    event Redeemed(address _redeemer, uint256 _tokenId, uint256 _amount);
    event RoyaltyPaid(address _to, uint256 _amount);
    
    constructor() ERC721("BLOCK", "OPS") {
        _setDefaultRoyalty(_royaltyAddress, royaltyNumerator);
    }

    modifier isInitialized() {
        require(initialized, "Contract is not yet initialized");
        _;
    }

    function safeMint(string memory tokenMetadataURI) public payable {
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
        tokenIdToProjectState[tokenId] = PROJECT_STATE.NEW;

        uint256 amountToEscrow = msg.value - _payOutRoyalty(tokenId, msg.value);
        amountOfEthInNFT[tokenId] = amountToEscrow;
        tokenIdToNftCreators[tokenId] = msg.sender;
        openNftsFromCreators[msg.sender].push(tokenId);

        totalBountyAmount += amountToEscrow;
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

    function tokenDetails(uint256 _tokenId) public view returns (address, string memory, uint256, address, uint256, PROJECT_STATE, Submission[] memory) {
        require(_exists(_tokenId), "NFT tokenId does not exist.");
        return (
            ownerOf(_tokenId), 
            tokenURI(_tokenId), 
            amountOfEthInNFT[_tokenId], 
            tokenIdToNftCreators[_tokenId], 
            _tokenId, 
            tokenIdToProjectState[_tokenId], 
            tokenIdToSubmissions[_tokenId]
        );
    }

    function contractAddress() public view returns (address) {
        return address(this);
    }

    function redeemEthFromNFT(uint256 _tokenId) external isInitialized {
        (
            address nftOwner, 
            string memory tokenMetadata, 
            uint256 amount, 
            address nftCreator, 
            uint256 tokenId, 
            PROJECT_STATE projectState, 
            Submission[] memory submissionsMade
        ) = tokenDetails(_tokenId);
        require(nftOwner == msg.sender, "Only the owner of the NFT can redeem the rewards.");
        require(projectState != PROJECT_STATE.CLOSED, "Cannot redeem a project has already been closed.");

        uint256 royaltyAmount = _payOutRoyalty(_tokenId, amount);
        uint256 amountToPayOut = amount - royaltyAmount;

        (bool success, ) = msg.sender.call{value: amountToPayOut}("");
        require(success, "Transfer Failed.");

        totalEthPaidOut += amountToPayOut;
        totalBountyAmount -= amountToPayOut;
        tokenIdToProjectState[_tokenId] = PROJECT_STATE.CLOSED;
        emit Redeemed(msg.sender, _tokenId, amountToPayOut);
    } 

    function makeSubmission(uint256 _tokenId, string memory submissionMetadataURI) external isInitialized {
        (
            address nftOwner, 
            string memory tokenMetadata, 
            uint256 amount, 
            address nftCreator, 
            uint256 tokenId, 
            PROJECT_STATE projectState, 
            Submission[] memory submissionsMade
        ) = tokenDetails(_tokenId);
        require(projectState != PROJECT_STATE.CLOSED, "Project is already closed");
        tokenIdToProjectState[_tokenId] = PROJECT_STATE.ACTIVE;
        
        Submission memory _submission;
        _submission.submitter = msg.sender;
        _submission.metadataURI = submissionMetadataURI; 

        tokenIdToSubmissions[_tokenId].push(_submission);
        emit SubmissionMade(msg.sender, _tokenId, submissionMetadataURI, nftOwner);
    }

    function declareWinningSubmission(uint256 _tokenId, uint256 _submissionId) external isInitialized {
        (
            address nftOwner, 
            , 
            , 
            , 
            , 
            PROJECT_STATE projectState, 
            Submission[] memory submissionsMade
        ) = tokenDetails(_tokenId);
        require(nftOwner == msg.sender, "Only the owner of the NFT can declare a winner.");
        require(projectState != PROJECT_STATE.CLOSED, "Project is already closed.");

        tokenIdToWinningSubmission[_tokenId] = submissionsMade[_submissionId];
        safeTransferFrom(nftOwner, submissionsMade[_submissionId].submitter, _tokenId);
    }

    function getAmountStoredInNFT(uint256 _tokenId) public view returns (uint256) {
        return amountOfEthInNFT[_tokenId];
    }

    function getNFTCreator(uint256 _tokenId) public view returns (address) {
        return tokenIdToNftCreators[_tokenId];
    }

    function getRoyaltyNumeratorAndDenominator() public view returns (uint8, uint16) {
        return (royaltyNumerator, royaltyDenominator);
    }

    function getArrayOfNFTsFromCreator(address _nftCreator) public view returns (uint256[] memory) {
        uint256[] memory arrayOfNfts = openNftsFromCreators[_nftCreator];
        return arrayOfNfts;
    }

    function getTotalEthPaidOut() public view returns (uint256) {
        return totalEthPaidOut;
    }

    function getTotalBountyAmount() public view returns (uint256) {
        return totalBountyAmount;
    }

    function getSubmissionsForTokenId(uint256 _tokenId) public view returns (Submission[] memory) {
        return tokenIdToSubmissions[_tokenId];
    }

    function getWinningSubmissionForTokenId(uint256 _tokenId) public view returns (Submission memory) {
        return tokenIdToWinningSubmission[_tokenId];
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

