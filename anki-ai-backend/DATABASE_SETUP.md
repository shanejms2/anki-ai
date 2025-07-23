# Database Schema Setup for Anki-AI

This document provides instructions for setting up the database schema in Supabase.

## Prerequisites

- Supabase project created and configured
- Environment variables set up in `.env` file
- Backend application ready

## Database Schema Overview

The Anki-AI application uses three main tables:

### 1. `users` Table
- Extends Supabase's built-in `auth.users` table
- Stores additional user profile information
- Fields: `id`, `email`, `username`, `created_at`, `updated_at`

### 2. `cards` Table
- Stores flashcard data
- Fields: `id`, `user_id`, `front`, `back`, `interval`, `ease`, `next_review`, `created_at`, `updated_at`
- Implements spaced repetition algorithm data

### 3. `reviews` Table
- Stores review history for spaced repetition
- Fields: `id`, `user_id`, `card_id`, `rating`, `reviewed_at`
- Rating values: 1-5 (1=Forgot, 2=Hard, 3=Good, 4=Easy, 5=Perfect)

## Setup Instructions

### Step 1: Access Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to the **SQL Editor** section
3. Click **New Query**

### Step 2: Run the Schema Script

1. Copy the contents of `schema.sql` file
2. Paste it into the SQL Editor
3. Click **Run** to execute the script

### Step 3: Verify Setup

After running the script, you should see:

1. **Tables created**: `users`, `cards`, `reviews`
2. **Indexes created**: Performance indexes on key columns
3. **Triggers created**: Automatic `updated_at` timestamp updates
4. **RLS policies**: Row Level Security enabled with proper policies

### Step 4: Test the Setup

Run the following command to test the database connection:

```bash
python -c "from app.core.supabase import get_supabase; supabase = get_supabase(); print('✅ Database connection working!')"
```

## Schema Details

### Relationships

- `users.id` → `cards.user_id` (One-to-Many)
- `users.id` → `reviews.user_id` (One-to-Many)
- `cards.id` → `reviews.card_id` (One-to-Many)

### Indexes

- `idx_cards_user_id`: Fast user card queries
- `idx_cards_next_review`: Fast due card queries
- `idx_reviews_user_id`: Fast user review queries
- `idx_reviews_card_id`: Fast card review queries
- `idx_reviews_reviewed_at`: Fast review history queries

### Security

- **Row Level Security (RLS)** enabled on all tables
- Users can only access their own data
- Policies ensure data isolation between users

### Triggers

- Automatic `updated_at` timestamp updates on record modifications

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure you're using the correct API keys
2. **Table Already Exists**: The script uses `CREATE TABLE IF NOT EXISTS`
3. **Foreign Key Errors**: Ensure the `auth.users` table exists (should be automatic)

### Verification Commands

Check if tables exist:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'cards', 'reviews');
```

Check RLS policies:
```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public';
```

## Next Steps

After setting up the database schema:

1. **Test the API endpoints** with the new database
2. **Implement authentication** using Supabase Auth
3. **Create API endpoints** for CRUD operations
4. **Set up frontend integration** to use the new backend

## Support

If you encounter any issues:

1. Check the Supabase logs in the dashboard
2. Verify your environment variables
3. Test the connection using the provided test commands
4. Review the error messages in the application logs 