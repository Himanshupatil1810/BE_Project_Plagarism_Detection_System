// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PlagiarismReport
 * @dev Smart contract for storing and verifying plagiarism detection reports
 * @author AI Plagiarism Detection System
 */
contract PlagiarismReport {
    
    // Events
    event ReportStored(
        string indexed reportHash,
        string documentHash,
        uint256 timestamp,
        address indexed submitter
    );
    
    event ReportVerified(
        string indexed reportHash,
        bool isValid,
        address indexed verifier
    );
    
    // Struct to store report data
    struct Report {
        string documentHash;
        uint256 timestamp;
        string metadata;
        address submitter;
        bool exists;
    }
    
    // Mapping from report hash to report data
    mapping(string => Report) public reports;
    
    // Mapping to track report submissions by address
    mapping(address => string[]) public userReports;
    
    // Admin address
    address public admin;
    
    // Modifier to restrict access to admin
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    // Constructor
    constructor() {
        admin = msg.sender;
    }
    
    /**
     * @dev Store a plagiarism report on the blockchain
     * @param reportHash SHA-256 hash of the report data
     * @param documentHash SHA-256 hash of the original document
     * @param metadata JSON string containing report metadata
     */
    function storeReport(
        string memory reportHash,
        string memory documentHash,
        string memory metadata
    ) external {
        require(bytes(reportHash).length > 0, "Report hash cannot be empty");
        require(bytes(documentHash).length > 0, "Document hash cannot be empty");
        require(!reports[reportHash].exists, "Report already exists");
        
        reports[reportHash] = Report({
            documentHash: documentHash,
            timestamp: block.timestamp,
            metadata: metadata,
            submitter: msg.sender,
            exists: true
        });
        
        userReports[msg.sender].push(reportHash);
        
        emit ReportStored(reportHash, documentHash, block.timestamp, msg.sender);
    }
    
    /**
     * @dev Get report details by hash
     * @param reportHash SHA-256 hash of the report
     * @return documentHash Hash of the original document
     * @return timestamp Block timestamp when report was stored
     * @return metadata JSON metadata of the report
     * @return exists Whether the report exists
     */
    function getReport(string memory reportHash) external view returns (
        string memory documentHash,
        uint256 timestamp,
        string memory metadata,
        bool exists
    ) {
        Report memory report = reports[reportHash];
        return (
            report.documentHash,
            report.timestamp,
            report.metadata,
            report.exists
        );
    }
    
    /**
     * @dev Verify if a report exists and is valid
     * @param reportHash SHA-256 hash of the report
     * @return isValid Whether the report is valid and exists
     */
    function verifyReport(string memory reportHash) external view returns (bool isValid) {
        return reports[reportHash].exists;
    }
    
    /**
     * @dev Get all reports submitted by a specific address
     * @param userAddress Address of the user
     * @return Array of report hashes
     */
    function getUserReports(address userAddress) external view returns (string[] memory) {
        return userReports[userAddress];
    }
    
    /**
     * @dev Get report count for a specific address
     * @param userAddress Address of the user
     * @return Number of reports submitted by the user
     */
    function getUserReportCount(address userAddress) external view returns (uint256) {
        return userReports[userAddress].length;
    }
    
    /**
     * @dev Verify report integrity by checking document hash
     * @param reportHash SHA-256 hash of the report
     * @param expectedDocumentHash Expected document hash
     * @return isValid Whether the document hash matches
     */
    function verifyDocumentIntegrity(
        string memory reportHash,
        string memory expectedDocumentHash
    ) external view returns (bool isValid) {
        if (!reports[reportHash].exists) {
            return false;
        }
        
        return keccak256(bytes(reports[reportHash].documentHash)) == 
               keccak256(bytes(expectedDocumentHash));
    }
    
    /**
     * @dev Get report submitter address
     * @param reportHash SHA-256 hash of the report
     * @return submitter Address of the report submitter
     */
    function getReportSubmitter(string memory reportHash) external view returns (address submitter) {
        require(reports[reportHash].exists, "Report does not exist");
        return reports[reportHash].submitter;
    }
    
    /**
     * @dev Update admin address (only current admin)
     * @param newAdmin New admin address
     */
    function updateAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "Invalid admin address");
        admin = newAdmin;
    }
    
    /**
     * @dev Emergency function to remove a report (only admin)
     * @param reportHash SHA-256 hash of the report to remove
     */
    function removeReport(string memory reportHash) external onlyAdmin {
        require(reports[reportHash].exists, "Report does not exist");
        delete reports[reportHash];
    }
    
    /**
     * @dev Get contract information
     * @return contractAddress Address of this contract
     * @return adminAddress Current admin address
     * @return blockNumber Current block number
     */
    function getContractInfo() external view returns (
        address contractAddress,
        address adminAddress,
        uint256 blockNumber
    ) {
        return (
            address(this),
            admin,
            block.number
        );
    }
}
