/* ------------------
*  init.sql
*  ------------------
*  Purpose:
*   SQL script that initializes the database with tables.
*   Used as initializing script for postgreSQL container.
*
*  Note: 
*   In production this should be ran together with 'init_user.sql' 
*   to create user and manage privileges.
*/

-- Drop tables if they exist
DROP TABLE IF EXISTS agent_outputs CASCADE;
DROP TABLE IF EXISTS agent_scenarios CASCADE;
DROP TABLE IF EXISTS simod_outputs CASCADE;
DROP TABLE IF EXISTS simod_scenarios CASCADE;
DROP TABLE IF EXISTS event_logs CASCADE;


-- Create tables
CREATE TABLE IF NOT EXISTS event_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    event_log BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS simod_scenarios (
    id SERIAL PRIMARY KEY,
    event_log_id INTEGER NOT NULL REFERENCES event_logs(id),
    name VARCHAR(255) NOT NULL,
    file_bpmn BYTEA NOT NULL,
    param_json BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS simod_outputs (
    simod_scenario_id INTEGER NOT NULL REFERENCES simod_scenarios(id),
    filename VARCHAR(255) NOT NULL,
    output_data BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_scenarios (
    id SERIAL PRIMARY KEY,
    event_log_id INTEGER NOT NULL REFERENCES event_logs(id),
    name VARCHAR(255) NOT NULL,
    model_pkl BYTEA NOT NULL,
    param_json BYTEA NOT NULL,
    visualization_json BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_outputs (
    agent_scenario_id INTEGER NOT NULL REFERENCES agent_scenarios(id),
    filename VARCHAR(255) NOT NULL,
    output_data BYTEA NOT NULL
);

