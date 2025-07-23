#!/usr/bin/env python3
"""
Database Schema Setup Script for Anki-AI
This script creates the necessary tables and indexes in Supabase.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.supabase import get_supabase
from app.core.logging import logger

def create_schema():
    """Create the database schema for Anki-AI."""
    try:
        supabase = get_supabase()
        logger.info("Starting database schema creation...")
        
        # SQL statements to create the schema
        schema_sql = """
        -- Create users table (extends Supabase auth.users)
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Create cards table
        CREATE TABLE IF NOT EXISTS public.cards (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            interval INTEGER DEFAULT 1,
            ease REAL DEFAULT 2.5,
            next_review TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Create reviews table
        CREATE TABLE IF NOT EXISTS public.reviews (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
            card_id UUID REFERENCES public.cards(id) ON DELETE CASCADE NOT NULL,
            rating INTEGER NOT NULL CHECK (rating IN (1, 2, 3, 4, 5)),
            reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Execute the schema creation
        result = supabase.rpc('exec_sql', {'sql': schema_sql}).execute()
        logger.info("Schema creation completed successfully")
        
        # Create indexes
        indexes_sql = """
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_cards_user_id ON public.cards(user_id);
        CREATE INDEX IF NOT EXISTS idx_cards_next_review ON public.cards(next_review);
        CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON public.reviews(user_id);
        CREATE INDEX IF NOT EXISTS idx_reviews_card_id ON public.reviews(card_id);
        CREATE INDEX IF NOT EXISTS idx_reviews_reviewed_at ON public.reviews(reviewed_at);
        """
        
        result = supabase.rpc('exec_sql', {'sql': indexes_sql}).execute()
        logger.info("Indexes created successfully")
        
        # Create triggers
        triggers_sql = """
        -- Create updated_at trigger function
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        -- Create triggers for updated_at
        DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

        DROP TRIGGER IF EXISTS update_cards_updated_at ON public.cards;
        CREATE TRIGGER update_cards_updated_at BEFORE UPDATE ON public.cards
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        result = supabase.rpc('exec_sql', {'sql': triggers_sql}).execute()
        logger.info("Triggers created successfully")
        
        logger.info("✅ Database schema setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
        raise

def setup_rls_policies():
    """Set up Row Level Security policies."""
    try:
        supabase = get_supabase()
        logger.info("Setting up Row Level Security policies...")
        
        # Enable RLS on tables
        rls_sql = """
        -- Enable RLS on all tables
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.cards ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
        
        -- Users can only access their own data
        CREATE POLICY "Users can view own profile" ON public.users
            FOR SELECT USING (auth.uid() = id);
            
        CREATE POLICY "Users can update own profile" ON public.users
            FOR UPDATE USING (auth.uid() = id);
            
        CREATE POLICY "Users can insert own profile" ON public.users
            FOR INSERT WITH CHECK (auth.uid() = id);
        
        -- Cards policies
        CREATE POLICY "Users can view own cards" ON public.cards
            FOR SELECT USING (auth.uid() = user_id);
            
        CREATE POLICY "Users can insert own cards" ON public.cards
            FOR INSERT WITH CHECK (auth.uid() = user_id);
            
        CREATE POLICY "Users can update own cards" ON public.cards
            FOR UPDATE USING (auth.uid() = user_id);
            
        CREATE POLICY "Users can delete own cards" ON public.cards
            FOR DELETE USING (auth.uid() = user_id);
        
        -- Reviews policies
        CREATE POLICY "Users can view own reviews" ON public.reviews
            FOR SELECT USING (auth.uid() = user_id);
            
        CREATE POLICY "Users can insert own reviews" ON public.reviews
            FOR INSERT WITH CHECK (auth.uid() = user_id);
        """
        
        result = supabase.rpc('exec_sql', {'sql': rls_sql}).execute()
        logger.info("✅ RLS policies set up successfully!")
        
    except Exception as e:
        logger.error(f"Failed to set up RLS policies: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting Anki-AI database setup...")
    
    try:
        create_schema()
        setup_rls_policies()
        logger.info("🎉 Database setup completed successfully!")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1) 