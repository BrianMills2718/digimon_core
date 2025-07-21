#!/bin/bash

# This script creates timestamped backups of the Neo4j and SQLite databases.

# --- Configuration ---
NEO4J_CONTAINER_NAME="digimons-neo4j-1" # Replace with your Neo4j container name if different
SQLITE_DB_PATH="./data/kGAS.sqlite" # Path to the SQLite database file
BACKUP_DIR="./data/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# --- Pre-flight Checks ---
echo "Starting database backup process..."

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory '$BACKUP_DIR' not found. Creating it..."
    mkdir -p "$BACKUP_DIR"
fi

# Check if SQLite database exists
if [ ! -f "$SQLITE_DB_PATH" ]; then
    echo "Error: SQLite database not found at '$SQLITE_DB_PATH'. Aborting."
    exit 1
fi

# Check if Neo4j container is running
if ! docker ps | grep -q "$NEO4J_CONTAINER_NAME"; then
    echo "Error: Neo4j container '$NEO4J_CONTAINER_NAME' is not running. Aborting."
    exit 1
fi

# --- SQLite Backup ---
SQLITE_BACKUP_FILENAME="sqlite_backup_${TIMESTAMP}.db"
echo "Backing up SQLite database to '$BACKUP_DIR/$SQLITE_BACKUP_FILENAME'..."
sqlite3 "$SQLITE_DB_PATH" ".backup '$BACKUP_DIR/$SQLITE_BACKUP_FILENAME'"
if [ $? -eq 0 ]; then
    echo "SQLite backup successful."
else
    echo "Error: SQLite backup failed."
    exit 1
fi

# --- Neo4j Backup ---
NEO4J_BACKUP_FILENAME="neo4j_backup_${TIMESTAMP}.dump"
echo "Backing up Neo4j database to '$BACKUP_DIR/$NEO4J_BACKUP_FILENAME'..."
docker exec "$NEO4J_CONTAINER_NAME" neo4j-admin database dump --to-path=/backups --database=neo4j
# The dump is created inside the container, now move it out
docker cp "$NEO4J_CONTAINER_NAME:/backups/neo4j.dump" "$BACKUP_DIR/$NEO4J_BACKUP_FILENAME"
if [ $? -eq 0 ]; then
    echo "Neo4j backup successful."
else
    echo "Error: Neo4j backup failed."
    # Optional: Clean up failed SQLite backup
    rm "$BACKUP_DIR/$SQLITE_BACKUP_FILENAME"
    exit 1
fi

echo "All database backups completed successfully and stored in '$BACKUP_DIR'." 