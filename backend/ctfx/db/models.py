import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="analyst")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="Misc", index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    flag_format: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    files: Mapped[List["ChallengeFile"]] = relationship("ChallengeFile", back_populates="challenge", cascade="all, delete-orphan")
    jobs: Mapped[List["AnalysisJob"]] = relationship("AnalysisJob", back_populates="challenge", cascade="all, delete-orphan")
    candidates: Mapped[List["CandidateFlag"]] = relationship("CandidateFlag", back_populates="challenge", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="challenge", cascade="all, delete-orphan")

class ChallengeFile(Base):
    __tablename__ = "challenge_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(64), default="BINARY", index=True)
    mime_type: Mapped[str] = mapped_column(String(128), default="application/octet-stream")
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    entropy: Mapped[float] = mapped_column(Float, default=0.0)
    has_trailing_bytes: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="files")
    artifacts: Mapped[List["ExtractedArtifact"]] = relationship("ExtractedArtifact", back_populates="parent_file", cascade="all, delete-orphan")

class FileHash(Base):
    __tablename__ = "file_hashes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    file_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenge_files.id", ondelete="CASCADE"), index=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    md5: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    sha1: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    job_type: Mapped[str] = mapped_column(String(64), default="universal_scan")
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="jobs")
    results: Mapped[List["AnalysisResult"]] = relationship("AnalysisResult", back_populates="job", cascade="all, delete-orphan")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), index=True)
    module: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[str] = mapped_column(String(512), default="")
    data_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    job: Mapped["AnalysisJob"] = relationship("AnalysisJob", back_populates="results")

class ExtractedArtifact(Base):
    __tablename__ = "extracted_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    parent_file_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenge_files.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(64), default="archive_extract")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    parent_file: Mapped["ChallengeFile"] = relationship("ChallengeFile", back_populates="artifacts")

class CandidateFlag(Base):
    __tablename__ = "candidate_flags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    source_file_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    flag: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="CANDIDATE", index=True)
    is_probable_decoy: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence_reasons_json: Mapped[str] = mapped_column(Text, default="[]")
    byte_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    encoding: Mapped[str] = mapped_column(String(32), default="utf-8")
    extraction_method: Mapped[str] = mapped_column(String(64), default="direct_scan")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="candidates")
    evidence: Mapped[List["FlagEvidence"]] = relationship("FlagEvidence", back_populates="candidate", cascade="all, delete-orphan")
    decodes: Mapped[List["DecodingOperation"]] = relationship("DecodingOperation", back_populates="candidate", cascade="all, delete-orphan")
    events: Mapped[List["VerificationEvent"]] = relationship("VerificationEvent", back_populates="candidate", cascade="all, delete-orphan")

class FlagEvidence(Base):
    __tablename__ = "flag_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_flags.id", ondelete="CASCADE"), index=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    start_offset: Mapped[int] = mapped_column(Integer, default=0)
    end_offset: Mapped[int] = mapped_column(Integer, default=0)
    snippet: Mapped[str] = mapped_column(String(512), default="")
    hex_preview: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    candidate: Mapped["CandidateFlag"] = relationship("CandidateFlag", back_populates="evidence")

class DecodingOperation(Base):
    __tablename__ = "decoding_operations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_flags.id", ondelete="CASCADE"), index=True)
    step_index: Mapped[int] = mapped_column(Integer, default=1)
    method: Mapped[str] = mapped_column(String(64), nullable=False)
    input_preview: Mapped[str] = mapped_column(String(256), default="")
    output_preview: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    candidate: Mapped["CandidateFlag"] = relationship("CandidateFlag", back_populates="decodes")

class VerificationEvent(Base):
    __tablename__ = "verification_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_flags.id", ondelete="CASCADE"), index=True)
    validator: Mapped[str] = mapped_column(String(128), nullable=False)
    result: Mapped[str] = mapped_column(String(32), nullable=False)  # ACCEPTED / REJECTED
    new_status: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_response: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    candidate: Mapped["CandidateFlag"] = relationship("CandidateFlag", back_populates="events")

class ToolInventory(Base):
    __tablename__ = "tool_inventory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    binary: Mapped[str] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(64))
    is_installed: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[str] = mapped_column(String(128), default="Unavailable")
    executable_path: Mapped[str] = mapped_column(String(512), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(64))
    target_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), default="127.0.0.1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    format: Mapped[str] = mapped_column(String(16))  # HTML, JSON, CSV, PDF
    title: Mapped[str] = mapped_column(String(256))
    content_path: Mapped[str] = mapped_column(String(512))
    summary_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="reports")

class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value_json: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
