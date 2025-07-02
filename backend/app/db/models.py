import typing as t
import datetime

from sqlalchemy import (
    func,
    ForeignKey
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class HealthCheckHistory(Base):
    __tablename__ = "health_check_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    ping_time: Mapped[t.Optional[float]] = mapped_column(nullable=True, default=None)
    delivered_packages_percentage: Mapped[t.Optional[int]] = mapped_column(nullable=True, default=None)
    last_successful_ping_timestamp: Mapped[t.Optional[datetime.datetime]] = mapped_column(server_default=func.now())

    related_address: Mapped[str] = mapped_column(ForeignKey("host_addresses.ip_address", ondelete="CASCADE"))


class HostAddresses(Base):
    __tablename__ = "host_addresses"

    ip_address: Mapped[str] = mapped_column(primary_key=True)

    health_checks: Mapped[t.List[HealthCheckHistory]] = relationship()
