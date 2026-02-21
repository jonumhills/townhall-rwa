# Townhall - Real Estate DeFi

> Tokenized real estate with blockchain-verified deeds and fractional ownership

## Problem Statement

**Real estate investment is inaccessible to most people:**

- 💰 Requires $200,000+ to buy property
- 🔒 Only wealthy developers can invest in rezoning value
- 📄 Manual deed verification costs $4.20+ and takes 10+ minutes
- 🏦 No way to own fractional shares of real estate

**When a parcel is rezoned** (e.g., residential → commercial), property value can increase 10x overnight — but only wealthy buyers can capitalize.

## Solution

**Townhall makes real estate investment democratic and blockchain-powered:**

### For Property Owners
1. Upload deed document for verification
2. County admin approves and mints NFT deed on-chain
3. Property is fractionalized into 1,000 shares
4. List shares on marketplace for trading

### For Investors
1. Browse tokenized parcels on interactive map
2. Buy fractional shares (as low as $50)
3. Trade shares on multi-chain marketplace
4. Track rezoning decisions that increase value

### Key Features

- **Blockchain Deed NFTs**: Property deeds minted as NFTs with county signature
- **Fractional Ownership**: 1,000 shares per property, 0 decimals
- **Multi-Chain**: Hedera (HBAR) for Raleigh, ADI Chain (zkSync) for Durham
- **County Verification**: Admin dashboard for government-approved minting
- **Interactive Maps**: Mapbox visualization showing tokenized parcels in gold
- **Instant Trading**: Buy/sell shares with 3-5 second finality

## Architecture

### Two-Token System Per Parcel

**Every tokenized property has:**
1. **NFT (Deed)**: ERC-721 or Hedera NonFungibleUnique - proof of ownership
2. **Share Tokens**: ERC-20 or Hedera FungibleCommon - 1,000 shares for fractional ownership

### Raleigh County (Hedera)

```
County Admin Creates NFT Token (ONCE)
    ↓
Landowner Submits Claim (PIN + Deed PDF)
    ↓
County Admin Approves
    ↓
Minting:
  ├─ NFT Serial #N on county token → stays in county treasury
  └─ Share Token (1000 shares) → held by operator wallet
    ↓
Owner Lists Shares on Marketplace
    ↓
Buyers Purchase Fractional Shares
```

**Token Standards:**
- NFT: Hedera `TokenType.NonFungibleUnique`
- Shares: Hedera `TokenType.FungibleCommon`

### Durham County (ADI Chain - zkSync Era)

```
County Admin Deploys Contracts (ONCE)
    ↓
Landowner Submits Claim (PIN + Deed PDF)
    ↓
County Admin Approves Claim
    ↓
Minting:
  ├─ ParcelNFT.mintParcel() → ERC-721 NFT sent to owner
  └─ ShareTokenFactory.createShareToken() → Deploys new ERC-20 contract
      └─ 1000 shares minted to owner immediately
    ↓
Owner Lists Shares on Marketplace Smart Contract
    ↓
Buyers Purchase via Marketplace.buyShares()
```

**Token Standards:**
- NFT: OpenZeppelin ERC-721
- Shares: OpenZeppelin ERC-20 (deployed per parcel)

### Tech Stack

- **Frontend**: React, Vite, TailwindCSS, Mapbox GL
- **Blockchain**: Hedera SDK (`@hashgraph/sdk`), Ethers.js, Hardhat
- **Backend**: Node.js (Express), Python (FastAPI)
- **Database**: Supabase (PostgreSQL)
- **Smart Contracts**: Solidity 0.8.20, OpenZeppelin

## Links

### Raleigh County (Hedera Testnet)

**NFT Token:**
- Token ID: `0.0.7961346`
- Explorer: https://hashscan.io/testnet/token/0.0.7961346

**Share Tokens** (created per parcel):
- Example: `0.0.7963265` (TCZ-91-21)
- Explorer: https://hashscan.io/testnet/token/0.0.7963265

### Durham County (ADI Testnet - zkSync Era)

**ParcelNFT Contract (ERC-721):**
- Address: `0x9157055CaC3583Ed303C51862e6C9A79E6Aa2e17`
- Explorer: https://explorer.testnet.abs.xyz/address/0x9157055CaC3583Ed303C51862e6C9A79E6Aa2e17

**ShareTokenFactory Contract:**
- Address: `0x8f16C7EE2C7100Bc074550CdB79dAD35C590Bb97`
- Explorer: https://explorer.testnet.abs.xyz/address/0x8f16C7EE2C7100Bc074550CdB79dAD35C590Bb97

**Marketplace Contract:**
- Address: `0x24d46f74Dd046A6B8DE72E8f01598d22C0cA8ab0`
- Explorer: https://explorer.testnet.abs.xyz/address/0x24d46f74Dd046A6B8DE72E8f01598d22C0cA8ab0

---

**Built with blockchain technology for democratic real estate investment**
