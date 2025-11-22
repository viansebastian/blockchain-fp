// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract DocumentRegistry {
    uint256 public docCount;

    struct Document {
        uint256 id;
        bytes32 docHash;   // sha256 of the document bytes
        string ipfsCid;    // ipfs CID or cloud URL
        string issuer;     // e.g., university name
        uint256 dateIssued; // unix timestamp (seconds) or yyyymmdd integer
        string verifier;   // who verified (maybe an org id)
        address owner;     // uploader
        uint256 version;   // incremental version number
        uint256 createdAt; // block timestamp
    }

    // id -> Document
    mapping(uint256 => Document[]) private versionsById;
    // map docHash => id (first id that had this hash)
    mapping(bytes32 => uint256) public firstIdByHash;

    event DocumentAdded(uint256 indexed id, bytes32 docHash, string ipfsCid, address indexed owner, uint256 version);
    event DocumentVersioned(uint256 indexed id, bytes32 docHash, string ipfsCid, address indexed owner, uint256 version);

    constructor() {
        docCount = 0;
    }

    // create a new document record (first version)
    function addDocument(
        bytes32 docHash,
        string calldata ipfsCid,
        string calldata issuer,
        uint256 dateIssued,
        string calldata verifier
    ) external returns (uint256) {
        docCount += 1;
        uint256 id = docCount;

        Document memory d = Document({
            id: id,
            docHash: docHash,
            ipfsCid: ipfsCid,
            issuer: issuer,
            dateIssued: dateIssued,
            verifier: verifier,
            owner: msg.sender,
            version: 1,
            createdAt: block.timestamp
        });

        versionsById[id].push(d);

        // store first mapping if not exists
        if (firstIdByHash[docHash] == 0) {
            firstIdByHash[docHash] = id;
        }

        emit DocumentAdded(id, docHash, ipfsCid, msg.sender, 1);
        return id;
    }

    // create a new version for an existing id (no deletion, append-only)
    function addVersion(
        uint256 id,
        bytes32 docHash,
        string calldata ipfsCid,
        string calldata issuer,
        uint256 dateIssued,
        string calldata verifier
    ) external returns (uint256) {
        require(id > 0 && id <= docCount, "invalid id");

        uint256 newVersion = versionsById[id].length + 1;

        Document memory d = Document({
            id: id,
            docHash: docHash,
            ipfsCid: ipfsCid,
            issuer: issuer,
            dateIssued: dateIssued,
            verifier: verifier,
            owner: msg.sender,
            version: newVersion,
            createdAt: block.timestamp
        });

        versionsById[id].push(d);

        if (firstIdByHash[docHash] == 0) {
            firstIdByHash[docHash] = id;
        }

        emit DocumentVersioned(id, docHash, ipfsCid, msg.sender, newVersion);
        return newVersion;
    }

    // read latest version for id
    function getLatest(uint256 id) external view returns (
        uint256, bytes32, string memory, string memory, uint256, string memory, address, uint256, uint256
    ) {
        require(id > 0 && id <= docCount, "invalid id");
        Document storage d = versionsById[id][versionsById[id].length - 1];
        return (d.id, d.docHash, d.ipfsCid, d.issuer, d.dateIssued, d.verifier, d.owner, d.version, d.createdAt);
    }

    // get specific version (1-based)
    function getVersion(uint256 id, uint256 version) external view returns (
        uint256, bytes32, string memory, string memory, uint256, string memory, address, uint256, uint256
    ) {
        require(id > 0 && id <= docCount, "invalid id");
        require(version >= 1 && version <= versionsById[id].length, "invalid version");
        Document storage d = versionsById[id][version - 1];
        return (d.id, d.docHash, d.ipfsCid, d.issuer, d.dateIssued, d.verifier, d.owner, d.version, d.createdAt);
    }

    // helper: get number of versions for id
    function getVersionCount(uint256 id) external view returns (uint256) {
        require(id > 0 && id <= docCount, "invalid id");
        return versionsById[id].length;
    }

    // lookup by hash -> first id
    function lookupByHash(bytes32 docHash) external view returns (uint256) {
        return firstIdByHash[docHash];
    }
}
