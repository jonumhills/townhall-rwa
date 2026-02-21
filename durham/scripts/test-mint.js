const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

/**
 * Test script to mint a sample parcel NFT
 *
 * This tests the deployed ParcelNFT contract by minting
 * a test property deed to the county admin wallet
 */
async function testMint() {
  console.log("\n========================================");
  console.log("Test Minting Durham County Parcel");
  console.log("========================================\n");

  // Load environment variables
  const privateKey = process.env.DURHAM_PRIVATE_KEY;
  const rpcUrl =
    process.env.ADI_RPC_URL || "https://rpc.ab.testnet.adifoundation.ai/";
  const parcelNFTAddress = process.env.PARCEL_NFT_ADDRESS;

  if (!privateKey) {
    throw new Error("DURHAM_PRIVATE_KEY not found in .env");
  }

  if (!parcelNFTAddress) {
    console.log("❌ PARCEL_NFT_ADDRESS not found in .env");
    console.log("\nPlease deploy contracts first:");
    console.log("1. npm run deploy");
    console.log("2. Copy ParcelNFT address to .env\n");
    process.exit(1);
  }

  // Connect to network
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(privateKey, provider);

  console.log(`Wallet: ${wallet.address}`);
  console.log(`Network: ADI Testnet\n`);

  // Load ParcelNFT ABI
  const abiPath = path.join(
    __dirname,
    "..",
    "..",
    "hedera",
    "abis",
    "durham",
    "ParcelNFT.json"
  );

  if (!fs.existsSync(abiPath)) {
    console.log("❌ ParcelNFT ABI not found");
    console.log("\nPlease extract ABIs first:");
    console.log("npm run extract-abis\n");
    process.exit(1);
  }

  const abi = JSON.parse(fs.readFileSync(abiPath, "utf8"));

  // Create contract instance
  const parcelNFT = new ethers.Contract(parcelNFTAddress, abi, wallet);

  console.log(`ParcelNFT Contract: ${parcelNFTAddress}\n`);

  // Test parcel data
  const testParcel = {
    to: wallet.address, // Mint to county admin
    pin: "TEST-" + Date.now(), // Unique PIN
    deedHash: "QmTestHash" + Math.random().toString(36).substring(7),
    geojson: JSON.stringify({
      type: "Polygon",
      coordinates: [
        [
          [-78.9, 35.9],
          [-78.8, 35.9],
          [-78.8, 36.0],
          [-78.9, 36.0],
          [-78.9, 35.9],
        ],
      ],
    }),
  };

  console.log("Test Parcel Data:");
  console.log(`  Owner: ${testParcel.to}`);
  console.log(`  PIN: ${testParcel.pin}`);
  console.log(`  Deed Hash: ${testParcel.deedHash}`);
  console.log(`  GeoJSON: ${testParcel.geojson.substring(0, 50)}...\n`);

  try {
    // Check if PIN already exists
    console.log("Checking if PIN exists...");
    const pinExists = await parcelNFT.pinExists(testParcel.pin);
    if (pinExists) {
      console.log("⚠️  PIN already minted. Using new PIN...");
      testParcel.pin = "TEST-" + Date.now();
    }

    // Mint parcel
    console.log("Minting parcel NFT...");
    const tx = await parcelNFT.mintParcel(
      testParcel.to,
      testParcel.pin,
      testParcel.deedHash,
      testParcel.geojson
    );

    console.log(`Transaction hash: ${tx.hash}`);
    console.log("Waiting for confirmation...\n");

    const receipt = await tx.wait();
    console.log("✅ Parcel minted successfully!\n");

    // Get token ID from event
    const event = receipt.logs.find((log) => {
      try {
        return parcelNFT.interface.parseLog(log).name === "ParcelMinted";
      } catch {
        return false;
      }
    });

    if (event) {
      const parsedEvent = parcelNFT.interface.parseLog(event);
      const tokenId = parsedEvent.args.tokenId;

      console.log(`Token ID: ${tokenId}`);
      console.log(`Owner: ${parsedEvent.args.owner}`);
      console.log(`PIN: ${parsedEvent.args.pin}\n`);

      // Verify parcel data
      console.log("Verifying on-chain data...");
      const parcel = await parcelNFT.parcels(tokenId);

      console.log(`\nOn-chain Parcel Data:`);
      console.log(`  PIN: ${parcel.pin}`);
      console.log(`  Deed Hash: ${parcel.deedHash}`);
      console.log(`  Verified By: ${parcel.verifiedBy}`);
      console.log(`  Verified At: ${new Date(Number(parcel.verifiedAt) * 1000).toISOString()}\n`);
    }

    // Get total supply
    const totalSupply = await parcelNFT.totalSupply();
    console.log(`Total Parcels Minted: ${totalSupply}\n`);

    console.log("Block Explorer:");
    console.log(
      `https://explorer.ab.testnet.adifoundation.ai/tx/${tx.hash}\n`
    );
  } catch (error) {
    console.error("❌ Minting failed:", error.message);

    if (error.message.includes("Only county admin")) {
      console.log(
        "\nError: The wallet is not authorized as county admin"
      );
    } else if (error.message.includes("PIN already minted")) {
      console.log("\nError: This PIN has already been minted");
    } else if (error.message.includes("insufficient funds")) {
      console.log("\nError: Insufficient ADI balance for gas fees");
      console.log(
        "Get testnet tokens: https://faucet.ab.testnet.adifoundation.ai/"
      );
    }

    process.exit(1);
  }
}

testMint()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
  });
