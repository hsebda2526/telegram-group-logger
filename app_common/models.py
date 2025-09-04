# app_common/models.py
# SQLAlchemy 2.0 декларативные модели и индексы


from datetime import datetime
from typing import Optional


from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column




class Base(DeclarativeBase):
    pass




class DbMessage(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


    # Chat info
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    chat_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    chat_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


    # Message ids and time
    message_id: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


    # Author info
    from_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, index=True)
    from_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    from_first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    from_last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    from_is_bot: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    from_language_code: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)


    # Content
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    has_media: Mapped[bool] = mapped_column(Boolean, default=False)
    media_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


    # Links
    reply_to_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    forward_from_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    forward_from_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    forward_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


    # Edits
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    edit_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


    # Full JSON from Telegram (на будущее)
    full_json: Mapped[dict] = mapped_column(JSONB)


    __table_args__ = (
    UniqueConstraint("chat_id", "message_id", name="uq_chat_message"),
    Index("ix_chat_id_date", "chat_id", "date"),
    )