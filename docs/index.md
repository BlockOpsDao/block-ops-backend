# Block Ops

need to store some sort of JSON-like data with a standard schema onto the blockchain.

The standard schema should not limit what developers can store, so maybe an "attributes" array of dicts with `{attribute_name: attribute_value}` syntax?

Then we hash this data so that it is always the same length. Then this data is un-hashed on the web ui and/or sdk to be turned into charts and tables. How do we hash the artifact? IPFS, Arweave, then store the link to the artifact?

What key do we use to hash it though? This is a good opportunity to release this data with NFT-like functionality, in that developers can share access to the data and artifacts either by sharing or selling access.

## Important Terms & Definitions

| Term      | Definition                                                              |
|-----------|-------------------------------------------------------------------------|
| Contract  | A set of requirements to be satisfied that is incentivized by a bounty. |
| User      | Person who creates a contract to be fulfilled by a developer.           |
| Developer | Someone who contributes code to fulfill requirements by a contract.     |