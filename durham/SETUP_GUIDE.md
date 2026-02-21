# Durham County Setup Guide

Quick start guide for deploying Durham County contracts to ADI Chain.

## Step 1: MetaMask Setup

### Install MetaMask
- Browser: https://metamask.io/download/
- Mobile: Install from App Store / Play Store

### Add ADI Testnet Network

Click "Add Network" in MetaMask and enter:

```
Network Name: ADI Testnet
RPC URL: https://rpc.ab.testnet.adifoundation.ai/
Chain ID: 99999
Currency Symbol: ADI
Block Explorer: https://explorer.ab.testnet.adifoundation.ai/
```

### Export Your Private Key

1. Open MetaMask
2. Click account menu (3 dots)
3. Account Details → Show Private Key
4. Enter password
5. Copy the private key (starts with `0x...`)

**⚠️ KEEP THIS SECRET - Never share your private key!**

## Step 2: Get Testnet Tokens

1. Copy your MetaMask wallet address (e.g., `0x1234...`)
2. Visit: https://faucet.ab.testnet.adifoundation.ai/
3. Paste your address
4. Request testnet ADI tokens
5. Wait ~30 seconds for tokens to arrive

## Step 3: Install & Configure

```bash
# Navigate to Durham directory
cd durham

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env and add your private key
nano .env
```

**In `.env` file:**
```bash
DURHAM_PRIVATE_KEY=0x...paste_your_private_key_here
```

Save and exit (Ctrl+X, then Y, then Enter)

## Step 4: Verify Setup

```bash
# Check your wallet balance
npm run check-balance
```

Expected output:
```
✅ Balance is sufficient for deployment
Balance: 1.5 ADI
```

## Step 5: Deploy Contracts

```bash
# Compile smart contracts
npm run compile

# Deploy to ADI testnet
npm run deploy
```

Expected output:
```
✅ ParcelNFT deployed to: 0xABC...
✅ ShareTokenFactory deployed to: 0xDEF...
✅ Marketplace deployed to: 0x123...
```

**Copy these addresses!** You'll need them for the backend.

## Step 6: Extract ABIs

```bash
npm run extract-abis
```

This copies contract ABIs to `../hedera/abis/durham/` for backend use.

## Step 7: Test Everything Works

```bash
# Test minting a property NFT
npm run test-mint
```

Expected output:
```
✅ Parcel minted successfully!
Token ID: 1
PIN: TEST-1234567890
```

## Step 8: Update .env with Contract Addresses

Edit `.env` again and add the deployed contract addresses:

```bash
PARCEL_NFT_ADDRESS=0xABC...
SHARE_TOKEN_FACTORY_ADDRESS=0xDEF...
MARKETPLACE_ADDRESS=0x123...
```

## You're Done!

Durham County contracts are now deployed on ADI Chain.

### View Your Contracts

Visit ADI Block Explorer:
https://explorer.ab.testnet.adifoundation.ai/

Search for your contract addresses to see transactions.

### Next Steps

1. Integrate Durham contracts with backend API
2. Add Durham County to frontend dropdown
3. Test end-to-end property tokenization flow

## Troubleshooting

### "Insufficient balance"
→ Get more tokens from https://faucet.ab.testnet.adifoundation.ai/

### "DURHAM_PRIVATE_KEY not found"
→ Make sure you created `.env` file and added your private key

### "Cannot connect to network"
→ Check ADI RPC URL: https://rpc.ab.testnet.adifoundation.ai/

### "Permission denied"
→ You're not using the county admin wallet

## Need Help?

- ADI Docs: https://docs.adi.foundation
- Durham README: See `README.md` in this directory
- Smart Contract Code: Check `contracts/` folder
