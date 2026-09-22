import psycopg2
from app.core.config import settings

def setup_vector_type():
    conn = psycopg2.connect(
        dbname="skilly",
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
    )
    cur = conn.cursor()
    
    # Check if native pgvector extension exists
    cur.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector';")
    if cur.fetchone():
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("Native pgvector extension enabled.")
    else:
        # Create a vector type with typmod support so VECTOR(1536) executes without error
        cur.execute("DROP DOMAIN IF EXISTS vector CASCADE;")
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
        print("Custom vector type with typmod support registered.")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    setup_vector_type()
