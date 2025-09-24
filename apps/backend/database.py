import os
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, String, Date, DateTime, Text, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ts = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    sender = Column(String)
    subject = Column(String)
    text = Column(Text)
    tags = Column(JSON, nullable=True)
    due_date = Column(Date)
    child = Column(String)

class Digest(Base):
    __tablename__ = "digests"
    
    day = Column(Date, primary_key=True)
    markdown = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        # Use DATABASE_URL from environment (Render provides this)
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Fallback to local SQLite for development
            database_url = "sqlite:///./parently.db"
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.SessionLocal = SessionLocal
    
    def get_session(self):
        return self.SessionLocal()
    
    def save_items(self, items: List[Dict[str, Any]]) -> None:
        """Save or update items in the database"""
        with self.get_session() as session:
            for item_data in items:
                # Check if item already exists (by source + sender + subject)
                existing = session.query(Item).filter(
                    Item.source == item_data.get("source"),
                    Item.sender == item_data.get("sender"),
                    Item.subject == item_data.get("subject")
                ).first()
                
                if existing:
                    # Update existing item
                    for key, value in item_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Create new item
                    item = Item(**item_data)
                    session.add(item)
            
            session.commit()
    
    def save_digest(self, day: date, markdown: str) -> None:
        """Save or update digest for a specific day"""
        with self.get_session() as session:
            existing = session.query(Digest).filter(Digest.day == day).first()
            if existing:
                existing.markdown = markdown
                existing.created_at = datetime.utcnow()
            else:
                digest = Digest(day=day, markdown=markdown)
                session.add(digest)
            session.commit()
    
    def get_digest(self, day: date) -> Optional[str]:
        """Get digest for a specific day"""
        with self.get_session() as session:
            digest = session.query(Digest).filter(Digest.day == day).first()
            return digest.markdown if digest else None
    
    def get_items_by_date_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get items within a date range"""
        with self.get_session() as session:
            items = session.query(Item).filter(
                Item.ts >= start_date,
                Item.ts <= end_date
            ).all()
            return [
                {
                    "id": item.id,
                    "ts": item.ts,
                    "source": item.source,
                    "sender": item.sender,
                    "subject": item.subject,
                    "text": item.text,
                    "tags": item.tags,
                    "due_date": item.due_date,
                    "child": item.child
                }
                for item in items
            ]

# Global database instance
db = Database()
