# Run using bash connect.sh [seed|reset]

source ../pipeline/.env

# Set default schema for the user
sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "ALTER USER [$DB_USER] WITH DEFAULT_SCHEMA = [$SCHEMA_NAME]"

if [ "_$1_" == "_reset_" ]; then
    # Run schema.sql to reset the database schema
    sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -i "schema.sql"
    echo "Database schema has been reset."

elif [ "_$1_" == "_seed_" ]; then
    # Run the seed_master_data.py
    python3 seed_master_data.py

else
    # Connect to the DB in terminal
    sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME"
fi