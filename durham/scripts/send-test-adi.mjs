#!/usr/bin/env node
/**
 * Send test ADI tokens to a wallet address
 * Usage: node send-test-adi.js <recipient-address> <amount-in-adi>
 */

import { ethers } from 'ethers';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env from parent directory
dotenv.config({ path: join(__dirname, '..', '.env') });

const RPC_URL = process.env.ADI_RPC_URL || 'https://rpc.ab.testnet.adifoundation.ai';
const ADMIN_PRIVATE_KEY = process.env.DURHAM_PRIVATE_KEY;

async function sendAdi(recipientAddress, amountInAdi) {
  if (!ADMIN_PRIVATE_KEY) {
    console.error('❌ DURHAM_PRIVATE_KEY not found in .env');
    process.exit(1);
  }

  if (!ethers.isAddress(recipientAddress)) {
    console.error('❌ Invalid recipient address:', recipientAddress);
    process.exit(1);
  }

  const amount = parseFloat(amountInAdi);
  if (isNaN(amount) || amount <= 0) {
    console.error('❌ Invalid amount:', amountInAdi);
    process.exit(1);
  }

  try {
    // Connect to ADI testnet
    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const wallet = new ethers.Wallet(ADMIN_PRIVATE_KEY, provider);

    console.log('\n🔗 ADI Testnet Transfer');
    console.log('━'.repeat(50));
    console.log(`From:   ${wallet.address}`);
    console.log(`To:     ${recipientAddress}`);
    console.log(`Amount: ${amount} ADI`);
    console.log('━'.repeat(50));

    // Check sender balance
    const balance = await provider.getBalance(wallet.address);
    const balanceInAdi = ethers.formatEther(balance);
    console.log(`\n💰 Sender Balance: ${balanceInAdi} ADI`);

    if (parseFloat(balanceInAdi) < amount) {
      console.error(`❌ Insufficient balance. You have ${balanceInAdi} ADI but trying to send ${amount} ADI`);
      process.exit(1);
    }

    // Send transaction
    console.log('\n📤 Sending transaction...');
    const tx = await wallet.sendTransaction({
      to: recipientAddress,
      value: ethers.parseEther(amount.toString()),
    });

    console.log(`\n⏳ Transaction sent: ${tx.hash}`);
    console.log('⏳ Waiting for confirmation...');

    const receipt = await tx.wait();

    console.log('\n✅ Transaction confirmed!');
    console.log(`Block: ${receipt.blockNumber}`);
    console.log(`Gas Used: ${receipt.gasUsed.toString()}`);

    // Check new balances
    const newSenderBalance = await provider.getBalance(wallet.address);
    const newRecipientBalance = await provider.getBalance(recipientAddress);

    console.log('\n💰 Updated Balances:');
    console.log(`Sender:    ${ethers.formatEther(newSenderBalance)} ADI`);
    console.log(`Recipient: ${ethers.formatEther(newRecipientBalance)} ADI`);

    console.log('\n🎉 Transfer complete!\n');
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('Usage: node send-test-adi.js <recipient-address> <amount-in-adi>');
  console.log('Example: node send-test-adi.js 0xdD2FD4581271e230360230F9337D5c0430Bf44C0 100');
  process.exit(1);
}

const [recipient, amount] = args;
sendAdi(recipient, amount);
