from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import datetime

# Association tables
note_tags = Table('note_tags', Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

worklog_tags = Table('worklog_tags', Base.metadata,
    Column('worklog_id', Integer, ForeignKey('worklogs.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String, default="#5C4B00")

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    color = Column(String, default="#FFF9E6")
    is_deleted = Column(Boolean, default=False) # For trash bin
    priority = Column(Integer, default=0) # 0: Normal, 1: High

    tags = relationship("Tag", secondary=note_tags, backref="notes")

class WorkLog(Base):
    __tablename__ = 'worklogs'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow) # Represents the log date
    title = Column(String)
    content = Column(Text)
    duration_minutes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tags = relationship("Tag", secondary=worklog_tags, backref="worklogs")

class OperationLog(Base):
    __tablename__ = 'operation_logs'

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String) # "create", "complete", "delete", "restore"
    note_content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
