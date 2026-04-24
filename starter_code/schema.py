from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# ==========================================
# ROLE 1: LEAD DATA ARCHITECT
# ==========================================
# Your task is to define the Unified Schema for all sources.
# This is v1. Note: A breaking change is coming at 11:00 AM!

SCHEMA_VERSION = "v2"

VALID_SOURCE_TYPES = {"PDF", "Video", "HTML", "CSV", "Code"}

class UnifiedDocument(BaseModel):
    """
    Unified schema v2 for the multi-source Knowledge Base.
    Every processing script must produce dicts that conform to this model.
    """

    document_id: str
    content: str
    source_type: str  # e.g., 'PDF', 'Video', 'HTML', 'CSV', 'Code'
    creator: Optional[str] = "Unknown"
    created_at: Optional[datetime] = None

    # You might want a dict for source-specific metadata
    source_metadata: dict = Field(default_factory=dict)

    # Track schema version so the mid-lab migration is easier
    schema_version: str = Field(default=SCHEMA_VERSION)

    # --- Validators -----------------------------------------------------------

    @field_validator("source_type")
    @classmethod
    def source_type_must_be_known(cls, v: str) -> str:
        if v not in VALID_SOURCE_TYPES:
            raise ValueError(
                f"source_type '{v}' is not valid. "
                f"Must be one of {VALID_SOURCE_TYPES}"
            )
        return v

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content must not be empty or whitespace-only")
        return v

    @field_validator("document_id")
    @classmethod
    def document_id_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("document_id must not be empty")
        return v
