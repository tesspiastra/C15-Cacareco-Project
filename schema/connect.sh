source ../pipeline/.env

if [ "$1" == "reset" ]; then
    sqlcmd -S "$DB_HOST,$DB_PORT" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -i "path/to/your/schema.sql"
    echo "Database schema has been reset."
else
    sqlcmd -S $DB_HOST,$DB_PORT -U $DB_USER -P $DB_PASSWORD -d $DB_NAME
fi
