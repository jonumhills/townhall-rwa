const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");

/**
 * Create a new Ethereum-compatible wallet for ADI Chain
 *
 * This generates a brand new wallet with:
 * - Private key
 * - Public key
 * - Wallet address
 *
 * Works offline - no RPC connection needed
 */
async function createWallet() {
  console.log("\n========================================");
  console.log("ADI Chain Wallet Generator");
  console.log("========================================\n");

  console.log("⚠️  SECURITY WARNING:");
  console.log("This wallet is for TESTNET ONLY!");
  console.log("Never use these keys for real funds.\n");

  // Generate random wallet
  const wallet = ethers.Wallet.createRandom();

  console.log("✅ New wallet created!\n");

  console.log("========================================");
  console.log("WALLET DETAILS");
  console.log("========================================\n");

  console.log("Address:");
  console.log(wallet.address);
  console.log("");

  console.log("Private Key:");
  console.log(wallet.privateKey);
  console.log("");

  console.log("Mnemonic (12 words):");
  console.log(wallet.mnemonic.phrase);
  console.log("");

  console.log("========================================");
  console.log("IMPORTANT - SAVE THESE SECURELY!");
  console.log("========================================\n");

  // Save to file
  const walletData = {
    address: wallet.address,
    privateKey: wallet.privateKey,
    mnemonic: wallet.mnemonic.phrase,
    network: "ADI Testnet",
    chainId: 99999,
    created: new Date().toISOString(),
  };

  const outputPath = path.join(__dirname, "..", "wallet-info.json");
  fs.writeFileSync(outputPath, JSON.stringify(walletData, null, 2));

  console.log(`Wallet details saved to: ${outputPath}`);
  console.log("⚠️  DELETE THIS FILE after copying to .env\n");

  // Create .env snippet
  console.log("========================================");
  console.log("COPY THIS TO YOUR .env FILE:");
  console.log("========================================\n");
  console.log(`DURHAM_PRIVATE_KEY=${wallet.privateKey}\n`);

  console.log("========================================");
  console.log("NEXT STEPS:");
  console.log("========================================\n");
  console.log("1. Copy the private key above to your .env file");
  console.log("2. Get testnet tokens using your address:");
  console.log("   https://faucet.ab.testnet.adifoundation.ai/\n");
  console.log(`3. Your wallet address is: ${wallet.address}\n`);
  console.log("4. Import to MetaMask (optional):");
  console.log("   - Click 'Import Account' in MetaMask");
  console.log("   - Paste the private key above\n");
  console.log("5. Check balance: npm run check-balance\n");

  console.log("========================================");
  console.log("SECURITY REMINDERS:");
  console.log("========================================\n");
  console.log("✅ Save the mnemonic phrase in a secure location");
  console.log("✅ Never share your private key with anyone");
  console.log("✅ Delete wallet-info.json after copying to .env");
  console.log("✅ Add .env to .gitignore (already done)\n");
}

createWallet()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error creating wallet:", error);
    process.exit(1);
  });
