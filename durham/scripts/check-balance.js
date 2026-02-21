const { ethers } = require("ethers");
require("dotenv").config();

/**
 * Check ADI testnet balance for Durham County wallet
 */
async function checkBalance() {
  console.log("\n========================================");
  console.log("ADI Chain Balance Checker");
  console.log("========================================\n");

  const privateKey = process.env.DURHAM_PRIVATE_KEY;
  if (!privateKey) {
    throw new Error("DURHAM_PRIVATE_KEY not found in .env file");
  }

  const rpcUrl =
    process.env.ADI_RPC_URL || "https://rpc.ab.testnet.adifoundation.ai/";

  // Connect to ADI testnet
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(privateKey, provider);

  console.log(`Wallet Address: ${wallet.address}\n`);

  try {
    // Get balance
    const balance = await provider.getBalance(wallet.address);
    const balanceInADI = ethers.formatEther(balance);

    console.log(`Balance: ${balanceInADI} ADI`);
    console.log(`Balance (wei): ${balance.toString()}\n`);

    // Check network
    const network = await provider.getNetwork();
    console.log(`Network: ${network.name}`);
    console.log(`Chain ID: ${network.chainId}\n`);

    // Get block number
    const blockNumber = await provider.getBlockNumber();
    console.log(`Current Block: ${blockNumber}\n`);

    // Check if balance is sufficient for deployment
    const minimumBalance = ethers.parseEther("0.01"); // 0.01 ADI minimum
    if (balance < minimumBalance) {
      console.log("⚠️  WARNING: Balance is low for deployment");
      console.log("   Recommended: At least 0.01 ADI");
      console.log("\nGet testnet tokens from:");
      console.log("https://faucet.ab.testnet.adifoundation.ai/\n");
    } else {
      console.log("✅ Balance is sufficient for deployment\n");
    }

    console.log("Block Explorer:");
    console.log(
      `https://explorer.ab.testnet.adifoundation.ai/address/${wallet.address}\n`
    );
  } catch (error) {
    console.error("❌ Error checking balance:", error.message);
    console.log("\nTroubleshooting:");
    console.log("1. Check your internet connection");
    console.log("2. Verify ADI_RPC_URL is correct");
    console.log("3. Ensure DURHAM_PRIVATE_KEY is valid\n");
    process.exit(1);
  }
}

checkBalance()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
  });
