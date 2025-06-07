/* ------------------
*  init_user.sql
*  ------------------
*  Purpose:
*   SQL script that initializes user with password read from file.
*   Used as initializing script for postgreSQL container.
*
*  Note: 
*   Not used for creating tables.
*   Reads password from docker secrets file.
*/

-- Create 'controller' user
DO $$
DECLARE
  cntrl_pass text;
BEGIN
  -- Read password from the file and trim any leading/trailing whitespace (e.g., newline)
  SELECT TRIM(BOTH E'\n' FROM pg_read_file('/run/secrets/pg_password')) INTO cntrl_pass;

  -- Create user if not exists 
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'controller') THEN
    EXECUTE format('CREATE ROLE controller WITH LOGIN PASSWORD %L', cntrl_pass);
  END IF;
END
$$;

-- Grant controller user necessary access
GRANT CONNECT ON DATABASE projectdb TO controller;
GRANT USAGE ON SCHEMA public TO controller;

-- Full access to all existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO controller;

-- Full access to all existing sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO controller;

-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO controller;

-- Default privileges for future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO controller;


