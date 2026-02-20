# Testing Guide - Deed Verification Workflow

## Migration Complete ✅
The database migration has been successfully applied. Your `token_registry` table now includes:
- `deed_document_url`
- `verification_status` (with constraint: pending/approved/rejected)
- `verification_notes`
- `verified_by`
- `verified_at`

## Quick Test Steps

### 1. Test User Flow (Submit a Claim)

1. **Start the frontend:**
   ```bash
   cd frontend && npm run dev
   ```

2. **Navigate to the map:**
   - Go to `http://localhost:5173/map`
   - Click on any parcel on the map
   - Click "Claim Parcel"

3. **Go through the 4-step flow:**
   - **Step 1:** Verify parcel details → Click "Verify Ownership"
   - **Step 2:** Upload a sample PDF deed
     - You can use any PDF file for testing
     - Max size: 10MB
   - **Step 3:** Optionally set a share price → Click "Submit Claim for Review"
   - **Step 4:** See "Claim Submitted!" confirmation with pending status

### 2. Test Admin Flow (Review Claims)

1. **Navigate to admin dashboard:**
   - Go to `http://localhost:5173/admin`

2. **View pending claims:**
   - You should see the claim you just submitted
   - Shows: PIN, owner account, deed document link, created date

3. **Review a claim:**
   - Enter your name/email in "Verified By" field (e.g., `admin@raleigh.gov`)
   - Click "Review Claim" on a pending item
   - Click "View Deed PDF" to see the uploaded document
   - Review the verification checklist

4. **Approve the claim:**
   - Add optional notes (e.g., "Deed verified, PIN matches")
   - Click "Approve & Mint"
   - Wait for Hedera transaction to complete (~5 seconds)
   - You'll see success message with NFT token ID and serial number

5. **Verify on Hedera:**
   - Click the Hashscan explorer links in the success message
   - Confirm the NFT was minted with the county account signature

### 3. Test Rejection Flow

1. **Submit another claim** (repeat User Flow steps)

2. **Reject the claim:**
   - Go to `/admin`
   - Click "Review Claim"
   - Add rejection notes (e.g., "PIN does not match deed document")
   - Click "Reject"
   - Claim status changes to "rejected"

### 4. Verify Database State

Check your Supabase `token_registry` table:

**Approved claim should have:**
```sql
verification_status = 'approved'
nft_token_id = '0.0.xxxxx'  -- Hedera token ID
serial_number = 1  -- or higher
share_token_id = '0.0.xxxxx'
verification_notes = 'your approval notes'
verified_by = 'admin@raleigh.gov'
verified_at = [timestamp]
```

**Rejected claim should have:**
```sql
verification_status = 'rejected'
nft_token_id = null
serial_number = null
verification_notes = 'your rejection notes'
verified_by = 'admin@raleigh.gov'
verified_at = [timestamp]
```

## Common Issues & Solutions

### Issue: "Parcel already has a pending claim"
**Solution:** The parcel has an existing claim in pending/approved/rejected status. Choose a different parcel or delete the existing claim from Supabase.

### Issue: "File too large" error
**Solution:** Use a PDF smaller than 10MB. For production, consider upgrading to IPFS/S3.

### Issue: Admin dashboard shows no pending claims
**Solution:**
1. Check that you submitted a claim first
2. Verify the claim wasn't already approved/rejected
3. Check Supabase to confirm the claim exists with `verification_status = 'pending'`

### Issue: County signature error during approval
**Solution:**
1. Ensure county account is properly configured in `.env`:
   ```
   RALEIGH_NC_ACCOUNT_ID=0.0.xxxxx
   RALEIGH_NC_PRIVATE_KEY=302e...
   ```
2. Verify county account has enough HBAR for gas fees

## Testing Checklist

- [ ] User can submit a claim with deed upload
- [ ] Claim appears in admin dashboard with "pending" status
- [ ] Admin can view uploaded deed PDF
- [ ] Admin can approve claim → NFT mints successfully
- [ ] Admin can reject claim → status changes to "rejected"
- [ ] Approved claims show NFT token ID and serial number
- [ ] Hashscan links work and show county signature
- [ ] Database records match expected state

## Demo Presentation Flow

For a demo, follow this sequence:

1. **Show the map** - explain parcel visualization
2. **Click a parcel** - show petition/zoning details
3. **Start claim flow** - walk through 4 steps
4. **Upload sample deed** - explain document requirement
5. **Submit claim** - show pending status
6. **Switch to admin view** - show `/admin` dashboard
7. **Review claim** - show verification checklist
8. **Approve claim** - demonstrate county signature minting
9. **Show Hashscan** - prove on-chain county approval
10. **Explain security** - county private key = proof of legitimacy

## Next Steps After Testing

Once testing is complete, consider:

1. **Production file storage:**
   - Replace base64 inline storage with IPFS (Pinata/NFT.Storage)
   - Or use S3 with presigned URLs
   - See `/hedera/utils/file-upload.js` for TODO comments

2. **Email notifications:**
   - Notify users when claims are approved/rejected
   - Use SendGrid, AWS SES, or similar

3. **Admin authentication:**
   - Add role-based access control for `/admin`
   - Integrate with county SSO/auth system

4. **Document OCR:**
   - Auto-extract PIN from uploaded deed PDFs
   - Flag mismatches for manual review

5. **Multi-signature approval:**
   - Require 2+ county officials to approve high-value parcels
