# Durham County Smart Contracts

Smart contracts for Durham County property tokenization on **ADI Chain** (zkSync-based L2).

## Overview

This system enables fractional ownership of Durham County real estate through blockchain tokenization:

- **ParcelNFT**: ERC-721 NFTs representing verified property deeds
- **ShareTokenFactory**: Creates ERC-20 tokens (1000 shares per property)
- **Marketplace**: Decentralized exchange for buying/selling shares

## Architecture

```
Durham County (ADI Chain)              Raleigh County (Hedera)
├── ParcelNFT (ERC-721)                ├── DeedNFT (HTS NFT)
├── ShareTokenFactory (ERC-20)         ├── ShareToken (HTS Fungible)
└── Marketplace (DEX)                  └── Hedera SDK
```

## Prerequisites

1. **MetaMask Wallet**
   - Install MetaMask browser extension or mobile app
   - Create a new wallet or import existing one
   - Save your wallet address and private key

2. **ADI Testnet Tokens**
   - Get testnet ADI tokens from: https://faucet.ab.testnet.adifoundation.ai/
   - Paste your MetaMask address
   - You'll receive testnet ADI for gas fees

3. **Node.js & npm**
   - Node.js v18+ required
   - npm v9+ recommended

## Setup

### 1. Install Dependencies

```bash
cd durham
npm install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your private key
nano .env
```

Add your MetaMask private key to `.env`:

```bash
DURHAM_PRIVATE_KEY=0x...your_private_key_here
```

**How to export private key from MetaMask:**
1. Open MetaMask
2. Click on account menu (3 dots)
3. Account details → Show private key
4. Enter password → Copy private key
5. Paste into `.env` file (keep it secret!)

### 3. Add ADI Network to MetaMask

**Network Configuration:**
- **Network Name**: ADI Testnet
- **RPC URL**: https://rpc.ab.testnet.adifoundation.ai/
- **Chain ID**: 99999
- **Currency Symbol**: ADI
- **Block Explorer**: https://explorer.ab.testnet.adifoundation.ai/

### 4. Check Your Balance

```bash
npm run check-balance
```

Expected output:
```
Wallet Address: 0x...
Balance: 1.5 ADI
✅ Balance is sufficient for deployment
```

If balance is low, get more tokens from the faucet.

## Deployment

### 1. Compile Contracts

```bash
npm run compile
```

This generates zkSync-compatible bytecode in `artifacts-zk/`.

### 2. Deploy to ADI Testnet

```bash
npm run deploy
```

Expected output:
```
✅ ParcelNFT deployed to: 0x...
✅ ShareTokenFactory deployed to: 0x...
✅ Marketplace deployed to: 0x...
```

Copy the contract addresses and update your `.env`:

```bash
PARCEL_NFT_ADDRESS=0x...
SHARE_TOKEN_FACTORY_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
```

### 3. Extract ABIs for Backend

```bash
npm run extract-abis
```

This copies contract ABIs to `../hedera/abis/durham/` for backend integration.

## Testing

### Test Minting a Parcel

```bash
npm run test-mint
```

This mints a sample property NFT to your wallet. Expected output:

```
✅ Parcel minted successfully!
Token ID: 1
PIN: TEST-1234567890
Verified By: 0x...
```

### Run Contract Tests

```bash
npm test
```

## Smart Contract Details

### ParcelNFT.sol

ERC-721 NFT contract for property deeds.

**Key Functions:**
- `mintParcel(to, pin, deedHash, geojson)` - Mint new parcel (county admin only)
- `getParcelByPin(pin)` - Retrieve parcel data by PIN
- `linkShareToken(tokenId, shareTokenId)` - Link share token to parcel

**Events:**
- `ParcelMinted(tokenId, owner, pin, deedHash, verifiedBy)`
- `ShareTokenLinked(tokenId, shareToken)`

### ShareTokenFactory.sol

Factory contract that creates ERC-20 share tokens (1000 per property).

**Key Functions:**
- `createShareToken(parcelTokenId, pin, owner)` - Create shares for property
- `getShareToken(parcelTokenId)` - Get share token address
- `getAllShareTokens()` - List all created share tokens

**ShareToken.sol** (deployed by factory):
- 1000 total supply (0 decimals)
- Linked to ParcelNFT via `parcelTokenId`
- Standard ERC-20 transfer/approve functions

**Events:**
- `ShareTokenCreated(tokenAddress, parcelTokenId, creator, symbol)`

### Marketplace.sol

Decentralized marketplace for buying/selling shares.

**Key Functions:**
- `listShares(shareToken, amount, pricePerShare)` - List shares for sale
- `purchaseShares(listingId)` - Buy shares (send ADI)
- `cancelListing(listingId)` - Cancel listing
- `getActiveListings(shareToken)` - View active listings

**Features:**
- Escrow mechanism (shares held in contract)
- 2% platform fee (configurable)
- ADI token payments
- ReentrancyGuard protection

**Events:**
- `SharesListed(listingId, seller, shareToken, amount, pricePerShare)`
- `SharesPurchased(listingId, buyer, seller, shareToken, amount, totalPrice, platformFee)`

## Directory Structure

```
durham/
├── contracts/           # Solidity smart contracts
│   ├── ParcelNFT.sol
│   ├── ShareTokenFactory.sol
│   └── Marketplace.sol
├── deploy/              # Deployment scripts
│   └── deploy-durham.js
├── scripts/             # Utility scripts
│   ├── extract-abis.js
│   ├── check-balance.js
│   └── test-mint.js
├── test/                # Contract tests
├── hardhat.config.js    # Hardhat configuration
├── package.json         # Dependencies
└── .env                 # Environment variables (keep secret!)
```

## Useful Commands

```bash
# Development
npm run compile          # Compile contracts
npm run deploy           # Deploy to ADI testnet
npm run extract-abis     # Copy ABIs to backend

# Testing
npm test                 # Run contract tests
npm run test-mint        # Test minting a parcel

# Utilities
npm run check-balance    # Check wallet balance
```

## ADI Chain Resources

- **Testnet Faucet**: https://faucet.ab.testnet.adifoundation.ai/
- **Block Explorer**: https://explorer.ab.testnet.adifoundation.ai/
- **Documentation**: https://docs.adi.foundation
- **GitHub**: https://github.com/ADI-Foundation-Labs

## Network Details

- **Chain ID**: 99999
- **RPC URL**: https://rpc.ab.testnet.adifoundation.ai/
- **Native Token**: ADI
- **L2 Type**: zkSync Atlas
- **Gas Fees**: ~$0.00001 per transaction
- **TPS**: 2,000 transactions per second

## Security Notes

- **NEVER** commit `.env` file to git (it contains your private key)
- **NEVER** share your private key with anyone
- Use testnet tokens only (no real value)
- County admin private key should be kept in secure hardware wallet for production

## Troubleshooting

### "Insufficient ADI balance"
Get testnet tokens from: https://faucet.ab.testnet.adifoundation.ai/

### "DURHAM_PRIVATE_KEY not found"
Make sure you created `.env` file from `.env.example` and added your private key

### "Compilation failed"
Run `npm install` to ensure all dependencies are installed

### "Network error"
Check your internet connection and verify RPC URL is correct

## Next Steps

After deployment:

1. **Extract ABIs** for backend integration: `npm run extract-abis`
2. **Update backend service** to interact with Durham contracts
3. **Add multi-chain routing** to detect Durham vs Raleigh counties
4. **Test end-to-end flow** from frontend → backend → ADI Chain

## Support

For issues specific to:
- **Smart contracts**: Check this README
- **ADI Chain**: https://docs.adi.foundation
- **zkSync**: https://docs.zksync.io
- **Hardhat**: https://hardhat.org/docs
