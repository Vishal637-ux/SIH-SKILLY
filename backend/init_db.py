import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings

def main():
    print("Checking PostgreSQL database connection and extensions...")
    # Parse connection info from DATABASE_URL
    # Default local fallback
    db_url = settings.DATABASE_URL
    print(f"Target Database URL: {db_url}")

    # Connect to default postgres database to ensure 'skilly' database exists
    try:
        conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="localhost", port=5432)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'skilly';")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE skilly;")
            print("Created database 'skilly'")
        else:
            print("Database 'skilly' already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print("Note on default database check:", e)

    # Now connect to 'skilly' database and enable extensions
    try:
        conn = psycopg2.connect(dbname="skilly", user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD, host=settings.POSTGRES_HOST, port=settings.POSTGRES_PORT)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        print("Extension 'pgcrypto' enabled.")
        
        # Check if vector extension is available
        cur.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector';")
        if cur.fetchone():
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("Extension 'vector' enabled.")
        else:
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vector') THEN
                        CREATE TYPE vector;
                        CREATE OR REPLACE FUNCTION vector_in(cstring, oid, integer)
                        RETURNS vector AS 'textin' LANGUAGE internal IMMUTABLE STRICT;
                        CREATE OR REPLACE FUNCTION vector_out(vector)
                        RETURNS cstring AS 'textout' LANGUAGE internal IMMUTABLE STRICT;
                        CREATE OR REPLACE FUNCTION vector_typmod_in(cstring[])
                        RETURNS integer AS 'varbit_support' LANGUAGE internal IMMUTABLE STRICT;
                        CREATE OR REPLACE FUNCTION vector_typmod_out(integer)
                        RETURNS cstring AS 'varbit_support' LANGUAGE internal IMMUTABLE STRICT;
                        CREATE TYPE vector (
                            INPUT = vector_in,
                            OUTPUT = vector_out,
                            TYPMOD_IN = vector_typmod_in,
                            TYPMOD_OUT = vector_typmod_out,
                            INTERNALLENGTH = VARIABLE,
                            STORAGE = extended
                        );
                    END IF;
                END $$;
            """)
            print("Vector type with typmod support enabled.")
            
        cur.close()
        conn.close()
        print("PostgreSQL initialization successful!")
    except Exception as e:
        print("Error during PostgreSQL initialization:", e)
        raise

if __name__ == "__main__":
    main()
