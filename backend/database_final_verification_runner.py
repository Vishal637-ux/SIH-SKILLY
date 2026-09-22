import sys
import os
import uuid
import json
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.config import settings

CANONICAL_47_TABLES = sorted([
    "users", "user_profiles", "institutions", "departments", "students", "teachers", "institution_staff",
    "companies", "company_users", "opportunities",
    "skills", "skill_relationships", "student_skills", "skill_evidence",
    "career_roles", "career_role_skills", "skill_gaps", "roadmaps", "roadmap_items",
    "assessments", "assessment_questions", "assessment_attempts",
    "training_programs", "training_enrollments",
    "opportunity_skills", "applications", "application_status_history", "internships", "internship_progress", "internship_evaluations", "placement_records",
    "placement_interactions", "portfolio_items", "recognitions", "resume_versions",
    "mentor_connections", "mentorship_sessions",
    "community_posts", "community_comments", "peer_skill_requests", "activities",
    "competitions", "competition_participants", "competition_teams", "competition_team_members",
    "notifications", "embeddings"
])

def run_final_manual_verification():
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB,
    )
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)

    results = {}

    # 1. Identity & Version
    cur.execute("SELECT current_database() AS db, current_user AS usr, version() AS ver;")
    ident = cur.fetchone()
    results["identity"] = ident
    print(f"DATABASE: {ident['db']} | USER: {ident['usr']} | VERSION: {ident['ver']}")

    # 2. Table Counts
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE table_name <> 'alembic_version') AS application_tables,
            COUNT(*) FILTER (WHERE table_name = 'alembic_version') AS migration_tables,
            COUNT(*) AS total_tables
        FROM information_schema.tables
        WHERE table_schema='public'
          AND table_type='BASE TABLE';
    """)
    counts = cur.fetchone()
    results["counts"] = counts
    print(f"COUNTS: Application={counts['application_tables']}, Migration={counts['migration_tables']}, Total={counts['total_tables']}")

    # 3. Exact 47 Application Tables
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
          AND table_type='BASE TABLE'
          AND table_name <> 'alembic_version'
        ORDER BY table_name;
    """)
    act_tables = [r["table_name"] for r in cur.fetchall()]
    results["tables"] = act_tables
    missing = [t for t in CANONICAL_47_TABLES if t not in act_tables]
    unexpected = [t for t in act_tables if t not in CANONICAL_47_TABLES]
    assert len(missing) == 0, f"Missing tables: {missing}"
    assert len(unexpected) == 0, f"Unexpected tables: {unexpected}"
    print(f"TABLES MATCH: {len(act_tables)}/47 exact match.")

    # 4. Primary Keys
    cur.execute("""
        SELECT
            tc.table_name,
            kcu.column_name,
            c.udt_name,
            c.column_default
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
        JOIN information_schema.columns c
          ON c.table_schema = kcu.table_schema AND c.table_name = kcu.table_name AND c.column_name = kcu.column_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'
          AND tc.table_name <> 'alembic_version'
        ORDER BY tc.table_name;
    """)
    pks = cur.fetchall()
    results["pk_count"] = len(pks)
    print(f"PRIMARY KEYS: {len(pks)}/47 tables have UUID primary keys.")

    # 5. Foreign Keys
    cur.execute("""
        SELECT
            tc.table_name AS source_table,
            kcu.column_name AS source_column,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column,
            rc.delete_rule,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
        JOIN information_schema.referential_constraints rc
          ON tc.constraint_name = rc.constraint_name AND tc.table_schema = rc.constraint_schema
        JOIN information_schema.constraint_column_usage ccu
          ON rc.unique_constraint_name = ccu.constraint_name AND rc.unique_constraint_schema = ccu.constraint_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
        ORDER BY tc.table_name, kcu.column_name;
    """)
    fks = cur.fetchall()
    results["fk_count"] = len(fks)
    print(f"FOREIGN KEYS: {len(fks)} total foreign key constraints.")

    # 6. Composite Foreign Keys
    cur.execute("""
        SELECT
            tc.constraint_name,
            kcu.table_name AS source_table,
            kcu.column_name AS source_column,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
          ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_name IN ('students', 'teachers')
          AND tc.constraint_name IN ('fk_student_institution_dept', 'fk_teacher_institution_dept')
        ORDER BY tc.constraint_name, kcu.ordinal_position;
    """)
    comp_fks = cur.fetchall()
    results["composite_fks"] = comp_fks
    print(f"COMPOSITE FKS VERIFIED: {set(r['constraint_name'] for r in comp_fks)}")

    # 7. CHECK Constraints
    cur.execute("""
        SELECT
            tc.table_name,
            tc.constraint_name,
            cc.check_clause
        FROM information_schema.table_constraints tc
        JOIN information_schema.check_constraints cc
          ON tc.constraint_name = cc.constraint_name AND tc.table_schema = cc.constraint_schema
        WHERE tc.constraint_type = 'CHECK'
          AND tc.table_schema = 'public'
          AND tc.constraint_name NOT LIKE '%_not_null'
        ORDER BY tc.table_name, tc.constraint_name;
    """)
    checks = cur.fetchall()
    results["check_count"] = len(checks)
    print(f"CHECK CONSTRAINTS: {len(checks)} domain CHECK constraints verified.")

    # 8. Alembic Version
    cur.execute("SELECT version_num FROM alembic_version;")
    alem = cur.fetchone()["version_num"]
    results["alembic_version"] = alem
    print(f"ALEMBIC VERSION: {alem}")

    # 9. pgvector & Embeddings
    cur.execute("""
        SELECT column_name, udt_name, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'embeddings' AND column_name = 'embedding_vector';
    """)
    vec = cur.fetchone()
    print(f"VECTOR TYPE: {vec['column_name']} ({vec['udt_name']})")

    conn.rollback()
    conn.close()
    return results

if __name__ == "__main__":
    run_final_manual_verification()
