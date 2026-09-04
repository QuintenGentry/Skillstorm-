"""
Define brands and posts tables for our database. 
"""
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from media_api.db_files.extensions import db


class BrandRecord(db.Model): 
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)

    # Allowing relationship back to posts. 
    brand_posts: Mapped[list["PostRecord"]] = relationship(
        back_populates="brand",
        cascade="all, delete-orphan"
    )

class PostRecord(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    caption_text: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str] = mapped_column(String(200), nullable=True)
    scheduled_publish_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    compliance_status: Mapped[str] = mapped_column(String(100), nullable=False)

    #Establishing foreign key. 
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), nullable=False)
    brand: Mapped["BrandRecord"] = relationship(back_populates="brand_posts")
