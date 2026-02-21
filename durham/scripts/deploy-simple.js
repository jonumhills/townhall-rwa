const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * Simple deployment script for ADI Chain (EVM-compatible)
 */
async function main() {
  console.log("\n========================================");
  console.log("Durham County Smart Contract Deployment");
  console.log("Network: ADI Chain Testnet");
  console.log("========================================\n");

  const [deployer] = await hre.ethers.getSigners();
  const countyAdmin = deployer.address;
  const platformWallet = deployer.address;

  console.log(`Deployer address: ${deployer.address}`);
  console.log(`County Admin: ${countyAdmin}`);
  console.log(`Platform Wallet: ${platformWallet}\n`);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log(`Wallet balance: ${hre.ethers.formatEther(balance)} ADI\n`);

  const deploymentResults = {
    network: "ADI Testnet",
    chainId: 99999,
    deployer: deployer.address,
    countyAdmin,
    platformWallet,
    timestamp: new Date().toISOString(),
    contracts: {},
  };

  // 1. Deploy ParcelNFT
  console.log("📝 Deploying ParcelNFT...");
  const ParcelNFT = await hre.ethers.getContractFactory("ParcelNFT");
  const parcelNFT = await ParcelNFT.deploy(countyAdmin);
  await parcelNFT.waitForDeployment();
  const parcelNFTAddress = await parcelNFT.getAddress();

  console.log(`✅ ParcelNFT deployed to: ${parcelNFTAddress}`);
  console.log(
    `   Explorer: https://explorer.ab.testnet.adifoundation.ai/address/${parcelNFTAddress}\n`
  );

  deploymentResults.contracts.ParcelNFT = {
    address: parcelNFTAddress,
    constructorArgs: [countyAdmin],
  };

  // 2. Deploy ShareTokenFactory
  console.log("🏭 Deploying ShareTokenFactory...");
  const ShareTokenFactory = await hre.ethers.getContractFactory("ShareTokenFactory");
  const shareTokenFactory = await ShareTokenFactory.deploy(countyAdmin, parcelNFTAddress);
  await shareTokenFactory.waitForDeployment();
  const shareTokenFactoryAddress = await shareTokenFactory.getAddress();

  console.log(`✅ ShareTokenFactory deployed to: ${shareTokenFactoryAddress}`);
  console.log(
    `   Explorer: https://explorer.ab.testnet.adifoundation.ai/address/${shareTokenFactoryAddress}\n`
  );

  deploymentResults.contracts.ShareTokenFactory = {
    address: shareTokenFactoryAddress,
    constructorArgs: [countyAdmin, parcelNFTAddress],
  };

  // 3. Deploy Marketplace
  console.log("🏪 Deploying Marketplace...");
  const Marketplace = await hre.ethers.getContractFactory("Marketplace");
  const marketplace = await Marketplace.deploy(platformWallet);
  await marketplace.waitForDeployment();
  const marketplaceAddress = await marketplace.getAddress();

  console.log(`✅ Marketplace deployed to: ${marketplaceAddress}`);
  console.log(
    `   Explorer: https://explorer.ab.testnet.adifoundation.ai/address/${marketplaceAddress}\n`
  );

  deploymentResults.contracts.Marketplace = {
    address: marketplaceAddress,
    constructorArgs: [platformWallet],
  };

  // Save deployment results
  const resultsPath = path.join(__dirname, "..", "deployed-addresses.json");
  fs.writeFileSync(resultsPath, JSON.stringify(deploymentResults, null, 2));

  console.log("========================================");
  console.log("✅ Deployment Complete!");
  console.log("========================================\n");

  console.log("Contract Addresses:");
  console.log(`ParcelNFT:         ${parcelNFTAddress}`);
  console.log(`ShareTokenFactory: ${shareTokenFactoryAddress}`);
  console.log(`Marketplace:       ${marketplaceAddress}\n`);

  console.log("Next steps:");
  console.log("1. Update your .env file with these addresses");
  console.log("2. Run: npm run extract-abis");
  console.log("3. Test minting: npm run test-mint\n");

  console.log(`Deployment details saved to: ${resultsPath}\n`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
