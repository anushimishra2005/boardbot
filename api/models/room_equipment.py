from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from api.core.database import Base


class RoomEquipment(Base):
    __tablename__ = "room_equipment"

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        primary_key=True,
    )

    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"),
        primary_key=True,
    )