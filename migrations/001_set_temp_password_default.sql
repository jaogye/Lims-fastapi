-- Migration: Set default value for temp_password column
-- Date: 2025-12-04
-- Description: Update existing NULL values in temp_password to FALSE (0)

-- Update all NULL temp_password values to 0 (False)
UPDATE tuser
SET temp_password = 0
WHERE temp_password IS NULL;

-- Add default constraint if not exists (optional, for future inserts)
-- Note: This will fail if the constraint already exists, which is fine
BEGIN TRY
    ALTER TABLE tuser
    ADD CONSTRAINT DF_tuser_temp_password DEFAULT 0 FOR temp_password;
END TRY
BEGIN CATCH
    -- Constraint might already exist, ignore error
    PRINT 'Default constraint already exists or could not be added';
END CATCH;

PRINT 'Migration completed successfully';
