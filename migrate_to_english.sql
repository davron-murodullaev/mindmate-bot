-- Migration: Update all users from 'uz' to 'en' language
-- Run this in your Render.com PostgreSQL console

-- Check current language distribution
SELECT language, COUNT(*) as user_count
FROM users
GROUP BY language;

-- Update all users with 'uz' to 'en'
UPDATE users
SET language = 'en'
WHERE language = 'uz';

-- Verify the update
SELECT language, COUNT(*) as user_count
FROM users
GROUP BY language;

-- Show total affected rows
SELECT 'Migration completed!' as status;
