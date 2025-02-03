source ../pipeline/.env

if [ "_$1_" == "_reset_" ]; then
    # Set default schema for the user
    sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "ALTER USER [$DB_USER] WITH DEFAULT_SCHEMA = [$SCHEMA_NAME]"
    
    # Run schema.sql to reset the database schema
    sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -i "schema.sql"
    
    echo "Database schema has been reset."
else
    # Set default schema for the user
    sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "ALTER USER [$DB_USER] WITH DEFAULT_SCHEMA = [$SCHEMA_NAME]"

    sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME"
fi