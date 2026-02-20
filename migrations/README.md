# Database Migrations

## Running the Deed Verification Migration

To add the deed verification columns to your Supabase `token_registry` table:

### Option 1: Supabase Dashboard (Recommended for MVP)
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy the contents of `001_add_deed_verification.sql`
4. Paste and run the SQL

### Option 2: Supabase CLI
```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref <your-project-ref>

# Run migration
supabase db push
```

### What This Migration Does
- Adds `deed_document_url` column for storing IPFS/S3 URLs to deed PDFs
- Adds `verification_status` column (pending/approved/rejected) with constraint
- Adds `verification_notes` column for county admin review notes
- Adds `verified_by` column to track which admin reviewed the claim
- Adds `verified_at` timestamp column
- Creates indexes for efficient admin dashboard queries

### Verification After Migration
Run this query in SQL Editor to confirm the columns exist:
```sql
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'token_registry'
AND column_name IN (
  'deed_document_url',
  'verification_status',
  'verification_notes',
  'verified_by',
  'verified_at'
);
```
