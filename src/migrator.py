import os
import aiomysql
import importlib.util

MIGRATIONS_DIR = 'migrations'

async def _create_migrations_table(conn):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    migration VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.commit()
    except Exception as e:
        print(f"Error creating migrations table: {e}")

async def _migration_applied(conn, migration_file):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM migrations WHERE migration = %s", (migration_file,))
            result = await cursor.fetchone()
        return result[0] > 0
    except Exception as e:
        print(f"Error checking if migration is applied: {e}")
        return False

async def _record_migration(conn, migration_file):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO migrations (migration) VALUES (%s)", (migration_file,))
            await conn.commit()
    except Exception as e:
        print(f"Error recording migration: {e}")

async def _execute_migration(conn, migration_file):
    spec = importlib.util.spec_from_file_location("migration", migration_file)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    if hasattr(migration, 'run'):
        await migration.run(conn)

async def _get_db_connection():
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'mysql'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', 'rootpassword'),
        'db': os.getenv('MYSQL_DATABASE', 'mydatabase'),
    }
    return await aiomysql.connect(**MYSQL_CONFIG)

async def run_migrations():
    conn = await _get_db_connection()
    await _create_migrations_table(conn)
    migration_files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.py')
    )
    for migration_file in migration_files:
        if not await _migration_applied(conn, migration_file):
            full_path = os.path.join(MIGRATIONS_DIR, migration_file)
            print(f"Executing migration: {migration_file}")
            await _execute_migration(conn, full_path)
            await _record_migration(conn, migration_file)
    conn.close()
    print("All migrations executed.")