-- Migration to update allowance status values from lowercase to uppercase
-- Run this on your database to ensure compatibility with the updated code

-- Update status values to uppercase
UPDATE allowances 
SET status = UPPER(status)
WHERE status IN ('available', 'reserved', 'retired');

-- Verify the update
SELECT status, COUNT(*) as count 
FROM allowances 
GROUP BY status 
ORDER BY status;

-- Expected output should show:
-- AVAILABLE | count
-- RESERVED  | count  
-- RETIRED   | count