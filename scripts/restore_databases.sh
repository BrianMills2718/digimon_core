#!/bin/bash

# This script restores the Neo4j and SQLite databases from specified backup files.
# WARNING: This is a destructive operation and will overwrite existing data.

# --- Configuration ---
NEO4J_CONTAINER_NAME="digimons-neo4j-1" # Replace with your Neo4j container name if different
SQLITE_DB_PATH="./data/kGAS.sqlite" # Path to the SQLite database file

# --- Input Validation ---
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_sqlite_backup.db> <path_to_neo4j_backup.dump>"
    exit 1
fi

SQLITE_BACKUP_PATH=$1
NEO4J_BACKUP_PATH=$2

echo "Starting database restore process..."
echo "=================================================="
echo "WARNING: This will overwrite the current databases."
echo "SQLite DB: $SQLITE_DB_PATH"
echo "Neo4j Container: $NEO4J_CONTAINER_NAME"
echo "=================================================="
read -p "Do you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 1
fi

# --- Pre-flight Checks ---
# Check if backup files exist
if [ ! -f "$SQLITE_BACKUP_PATH" ]; then
    echo "Error: SQLite backup file not found at '$SQLITE_BACKUP_PATH'."
    exit 1
fi
if [ ! -f "$NEO4J_BACKUP_PATH" ]; then
    echo "Error: Neo4j backup file not found at '$NEO4J_BACKUP_PATH'."
    exit 1
fi

# --- Stop Services (if they were running) ---
echo "Stopping Neo4j container to perform restore..."
docker stop "$NEO4J_CONTAINER_NAME"

# --- SQLite Restore ---
echo "Restoring SQLite database from '$SQLITE_BACKUP_PATH'..."
rm -f "$SQLITE_DB_PATH"
sqlite3 "$SQLITE_DB_PATH" ".restore '$SQLITE_BACKUP_PATH'"
if [ $? -eq 0 ]; then
    echo "SQLite restore successful."
else
    echo "Error: SQLite restore failed."
    docker start "$NEO4J_CONTAINER_NAME" # Restart neo4j before exiting
    exit 1
fi

# --- Neo4j Restore ---
echo "Restoring Neo4j database from '$NEO4J_BACKUP_PATH'..."
# Copy the dump file into the container
docker cp "$NEO4J_BACKUP_PATH" "$NEO4J_CONTAINER_NAME:/backups/restore.dump"
# Run the load command inside the container
docker exec "$NEO4J_CONTAINER_NAME" neo4j-admin database load --from-path=/backups/restore.dump --overwrite-destination=true neo4j
if [ $? -eq 0 ]; then
    echo "Neo4j restore successful."
else
    echo "Error: Neo4j restore failed."
    docker start "$NEO4J_CONTAINER_NAME" # Attempt to restart neo4j anyway
    exit 1
fi

# --- Start Services ---
echo "Starting Neo4j container..."
docker start "$NEO4J_CONTAINER_NAME"

echo "All database restores completed successfully."
echo "Please verify the data in your applications." 