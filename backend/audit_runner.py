import sys
import os
import json
import importlib
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlalchemy
from sqlalchemy import create_engine, text
import fastapi
import alembic
import pgvector
import pydantic

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings
from app.models import Base

def run_deep_audit():
    print("=" * 70)
    print("SKILLY PHASE 2.2 DEEP AUDIT RUNNER")
    print("=" * 70)
    
    audit_data = {}
    
    # 1. Environment & Package Versions
    print("\n--- 1. Environment & Installed Versions ---")
    env_info = {
        "python_version": sys.version,
        "fastapi_version": getattr(fastapi, "__version__", "unknown"),
        "sqlalchemy_version": getattr(sqlalchemy, "__version__", "unknown"),
        "alembic_version": getattr(alembic, "__version__", "unknown"),
        "pgvector_version": getattr(pgvector, "__version__", "unknown"),
        "pydantic_version": getattr(pydantic, "__version__", "unknown"),
        "database_url": settings.DATABASE_URL.replace("postgres:postgres", "postgres:***"),
        "sync_database_url": settings.SYNC_DATABASE_URL.replace("postgres:postgres", "postgres:***"),
    }
    for k, v in env_info.items():
        print(f"  {k}: {v}")
    audit_data["environment"] = env_info

    # 2. Model Inspection
    print("\n--- 2. SQLAlchemy ORM Model Audit ---")
    model_classes = [cls for cls in Base.__subclasses__()]
    # Collect all direct and indirect subclasses if any
    all_models = set()
    def collect_subclasses(cls):
        for sub in cls.__subclasses__():
            all_models.add(sub)
            collect_subclasses(sub)
    collect_subclasses(Base)
    
    table_names_in_metadata = sorted(list(Base.metadata.tables.keys()))
    print(f"  ORM Models Count: {len(all_models)}")
    print(f"  Metadata Tables Count: {len(table_names_in_metadata)}")
    print(f"  Metadata Tables: {table_names_in_metadata}")
    audit_data["models"] = {
        "model_classes_count": len(all_models),
        "metadata_tables_count": len(table_names_in_metadata),
        "metadata_tables": table_names_in_metadata
    }

    # 3. PostgreSQL Database Audit
    print("\n--- 3. PostgreSQL Direct System Catalog Audit ---")
    # Connect directly to Postgres
    sync_url = settings.SYNC_DATABASE_URL
    # parse db, user, host, port
    conn = psycopg2.connect(dbname="skilly", user="postgres", password="postgres", host="localhost", port=5433)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # DB Version
    cur.execute("SELECT version();")
    pg_version = cur.fetchone()[0]
    print(f"  PostgreSQL Server Version: {pg_version}")
    audit_data["pg_version"] = pg_version

    # Extensions
    cur.execute("SELECT extname, extversion FROM pg_extension;")
    extensions = {row[0]: row[1] for row in cur.fetchall()}
    print(f"  Installed Extensions: {extensions}")
    audit_data["extensions"] = extensions

    # Tables in public schema
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    db_tables = [row[0] for row in cur.fetchall()]
    app_tables = [t for t in db_tables if t != "alembic_version"]
    print(f"  Total DB Base Tables: {len(db_tables)}")
    print(f"  Application Tables (excl. alembic_version): {len(app_tables)}")
    print(f"  Application Tables List: {app_tables}")
    audit_data["db_tables"] = {
        "total_base_tables": len(db_tables),
        "app_tables_count": len(app_tables),
        "app_tables": app_tables
    }

    # Foreign Keys & Composite Foreign Keys
    cur.execute("""
        SELECT
            tc.table_name,
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.update_rule,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.referential_constraints AS rc
            ON tc.constraint_name = rc.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position;
    """)
    fks = cur.fetchall()
    print(f"  Total Foreign Key Constraints / Column Mappings: {len(fks)}")
    audit_data["foreign_keys"] = [
        {
            "table": row[0],
            "constraint": row[1],
            "column": row[2],
            "foreign_table": row[3],
            "foreign_column": row[4],
            "on_update": row[5],
            "on_delete": row[6]
        }
        for row in fks
    ]

    # Unique Constraints
    cur.execute("""
        SELECT tc.table_name, tc.constraint_name, string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as cols
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'UNIQUE'
        GROUP BY tc.table_name, tc.constraint_name
        ORDER BY tc.table_name;
    """)
    uqs = cur.fetchall()
    print(f"  Total Unique Constraints: {len(uqs)}")
    audit_data["unique_constraints"] = [
        {"table": row[0], "constraint": row[1], "columns": row[2]} for row in uqs
    ]

    # CHECK Constraints
    cur.execute("""
        SELECT tc.table_name, tc.constraint_name, cc.check_clause
        FROM information_schema.table_constraints tc
        JOIN information_schema.check_constraints cc
            ON tc.constraint_name = cc.constraint_name
        WHERE tc.constraint_type = 'CHECK' AND tc.constraint_name NOT LIKE '%_not_null'
        ORDER BY tc.table_name;
    """)
    chks = cur.fetchall()
    print(f"  Total CHECK Constraints: {len(chks)}")
    audit_data["check_constraints"] = [
        {"table": row[0], "constraint": row[1], "clause": row[2]} for row in chks
    ]

    # Indexes
    cur.execute("""
        SELECT tablename, indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
    """)
    indexes = cur.fetchall()
    print(f"  Total Indexes in Public Schema: {len(indexes)}")
    audit_data["indexes"] = [
        {"table": row[0], "index": row[1], "definition": row[2]} for row in indexes
    ]

    # Vector Column & HNSW Index Audit
    cur.execute("""
        SELECT column_name, udt_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'embeddings' AND column_name = 'embedding_vector';
    """)
    vec_col = cur.fetchone()
    print(f"  Embeddings.embedding_vector column: {vec_col}")
    audit_data["vector_column"] = vec_col

    cur.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'embeddings' AND indexname = 'idx_embeddings_cosine';
    """)
    hnsw_def = cur.fetchone()
    print(f"  HNSW Cosine Index: {hnsw_def}")
    audit_data["hnsw_index"] = hnsw_def

    # Columns detail for each table
    cur.execute("""
        SELECT table_name, column_name, data_type, udt_name, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name != 'alembic_version'
        ORDER BY table_name, ordinal_position;
    """)
    cols = cur.fetchall()
    columns_by_table = {}
    for row in cols:
        t_name = row[0]
        if t_name not in columns_by_table:
            columns_by_table[t_name] = []
        columns_by_table[t_name].append({
            "name": row[1],
            "data_type": row[2],
            "udt_name": row[3],
            "is_nullable": row[4],
            "default": row[5]
        })
    audit_data["columns_by_table"] = columns_by_table
    print(f"  Audited columns for {len(columns_by_table)} tables.")

    cur.close()
    conn.close()

    # Save audit raw data
    with open("backend/audit_results.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, default=str)
    print("\n[SUCCESS] Raw audit data written to backend/audit_results.json")

if __name__ == "__main__":
    run_deep_audit()
