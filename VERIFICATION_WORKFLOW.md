# Option A1: Manual Deed Document Verification Workflow

## Overview
This document describes the deed verification workflow (Option A1) implemented for Townhall. Users submit claims with deed documents, which are manually reviewed by county legislators before NFT minting with county signature.

## How It Works

### User Flow (Claim Submission)
1. **User selects a parcel** on the map and clicks "Claim Parcel"
2. **Step 1: Verify Parcel** - System checks that:
   - PIN exists in the database
   - Parcel is not already tokenized
3. **Step 2: Upload Deed Document** - User uploads PDF deed (max 10MB)
4. **Step 3: Set Share Price** (optional) - User can set initial price or skip
5. **Step 4: Claim Submitted** - Claim enters `pending` status awaiting review

### County Admin Flow (Verification Dashboard)
1. **Navigate to `/admin`** - Admin verification dashboard
2. **View pending claims** - Shows all claims awaiting review
3. **Review each claim**:
   - View uploaded deed PDF
   - Check verification checklist:
     - PIN matches deed document
     - Owner account is valid
     - Document is recent and authentic
     - No liens/encumbrances (if applicable)
4. **Approve or Reject**:
   - **Reject:** Claim marked as rejected with notes
   - **Approve:** NFT minted with **county signature** on Hedera

## Implementation Details

### Database Schema (`token_registry` table)
```sql
-- New columns added via migrations/001_add_deed_verification.sql
deed_document_url     TEXT           -- IPFS/S3 URL or base64 data URL (MVP)
verification_status   TEXT           -- pending | approved | rejected
verification_notes    TEXT           -- Admin review notes
verified_by           TEXT           -- Email/ID of admin who reviewed
verified_at           TIMESTAMPTZ    -- Timestamp of approval/rejection
```

### Backend Endpoints

#### POST /token/submit-claim
Submit a new claim with deed document.

**Request:**
```json
{
  "pin": "Z-51-2024",
  "countyId": "raleigh_nc",
  "ownerAccountId": "0.0.12345",
  "priceHbar": 5000,
  "deedDocumentBase64": "data:application/pdf;base64,JVBERi0xLjQK..."
}
```

**Response:**
```json
{
  "success": true,
  "claim_id": 123,
  "verification_status": "pending",
  "message": "Claim submitted successfully. Awaiting county legislator approval."
}
```

#### GET /token/admin/pending-claims
Fetch all pending claims (for admin dashboard).

**Query params:** `?countyId=raleigh_nc` (optional)

**Response:**
```json
{
  "pending_claims": [
    {
      "id": 123,
      "pin": "Z-51-2024",
      "county_id": "raleigh_nc",
      "owner_wallet": "0.0.12345",
      "deed_document_url": "data:application/pdf;base64,...",
      "verification_status": "pending",
      "created_at": "2026-02-19T10:30:00Z",
      ...
    }
  ],
  "count": 1
}
```

#### POST /token/admin/approve-claim
Approve or reject a claim (county admin only).

**Request:**
```json
{
  "claimId": 123,
  "approved": true,
  "notes": "Deed document verified, PIN matches",
  "verifiedBy": "admin@raleigh.gov"
}
```

**Response (approved):**
```json
{
  "success": true,
  "claim_id": 123,
  "verification_status": "approved",
  "message": "Claim approved and NFT minted with county signature",
  "mint": {
    "nft_token_id": "0.0.56789",
    "serial_number": 1,
    "share_token_id": "0.0.56790",
    "total_shares": 1000,
    "tx_hash": "0.0.12345@1234567890.123456789",
    "explorer_urls": { ... }
  }
}
```

**Response (rejected):**
```json
{
  "success": true,
  "claim_id": 123,
  "verification_status": "rejected",
  "message": "Claim rejected"
}
```

### Frontend Components

#### ClaimModal (Modified - 4 Steps)
- **Step 1:** Verify parcel details
- **Step 2:** Upload deed PDF document
- **Step 3:** Set share price (optional)
- **Step 4:** Pending review confirmation

#### AdminDashboard (New)
- Located at `/admin` route
- Shows all pending claims
- Review modal with verification checklist
- Approve/Reject buttons
- Links to view deed PDFs

### File Upload (MVP)
For the demo, deed documents are:
- Converted to base64 data URLs in the browser
- Stored inline in Supabase `deed_document_url` column
- **Not recommended for production** (large text fields)

**Production alternatives:**
- **IPFS** (Pinata, NFT.Storage) - decentralized, immutable
- **S3** with presigned URLs - centralized, easier to manage

See `/hedera/utils/file-upload.js` for implementation.

## County Signature Proof

The key security feature is that **every NFT mint requires county signature**:

```javascript
// From /hedera/mint-parcel-nft.js line 47-52
const mintTx = await new TokenMintTransaction()
  .setTokenId(nftTokenId)
  .addMetadata(metadata)
  .setMaxTransactionFee(new Hbar(20))
  .freezeWith(client)
  .sign(county.key);  // ← COUNTY SIGNS THE MINT
```

This means:
- County account holds the NFT supply key
- Only county can mint new NFT serials
- On-chain transaction proves county approved the claim
- Hedera transaction ID serves as immutable audit trail

## Running the Migration

Before using this workflow, you must run the database migration:

1. Go to your Supabase SQL Editor
2. Copy contents of `/migrations/001_add_deed_verification.sql`
3. Run the SQL to add verification columns

See `/migrations/README.md` for details.

## Demo Usage

### As a User:
1. Navigate to `/map`
2. Click a parcel → "Claim Parcel"
3. Follow the 4-step flow
4. Upload a sample PDF deed
5. Submit claim

### As a County Admin:
1. Navigate to `/admin`
2. Enter your name/email in "Verified By" field
3. Click "Review Claim" on pending items
4. View uploaded deed PDF
5. Click "Approve & Mint" or "Reject"

## Architecture Benefits

1. **Security:** County signature required for all mints
2. **Auditability:** On-chain record of approval via county transaction
3. **Flexibility:** Admin can review and reject invalid claims
4. **Demo-ready:** Works without complex auth/KYC
5. **Scalable:** Easy to upgrade to automated verification later

## Future Enhancements

1. **IPFS/S3 storage** for deed documents instead of inline base64
2. **Email notifications** to users when claims approved/rejected
3. **Document OCR/parsing** to auto-extract PIN from deed PDFs
4. **Multi-signature** approval from multiple county officials
5. **Role-based access control** for admin dashboard
6. **Webhook integration** to county GIS/deed systems
