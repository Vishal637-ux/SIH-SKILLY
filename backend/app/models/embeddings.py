import uuid
from typing import Optional
from sqlalchemy import (
    String, text, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.models.base import Base


class Embedding(Base):
    """Polymorphic vector storage supporting semantic skill search and AI recommendations."""
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    embedding_vector: Mapped[Vector] = mapped_column(Vector(1536), nullable=False)
    model_name: Mapped[str] = mapped_column(
        String(100),
        default="text-embedding-3-small",
        server_default=text("'text-embedding-3-small'"),
        nullable=False,
    )
    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        default="1.0",
        server_default=text("'1.0'"),
        nullable=True,
    )
    updated_at: Mapped[str] = mapped_column(
        server_default=text("NOW()"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_entity_embedding"),
        Index("idx_embeddings_lookup", "entity_type", "entity_id"),
        Index(
            "idx_embeddings_cosine",
            "embedding_vector",
            postgresql_using="hnsw",
            postgresql_ops={"embedding_vector": "vector_cosine_ops"},
        ),
    )
