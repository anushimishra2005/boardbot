"""ignore cancelled bookings in overlap constraint

Revision ID: a9de8010723f
Revises: af937e09be99
Create Date: 2026-09-24 04:18:35.854136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9de8010723f'
down_revision: Union[str, Sequence[str], None] = 'af937e09be99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE bookings
        DROP CONSTRAINT booking_no_room_overlap
        """
    )

    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT booking_no_room_overlap
        EXCLUDE USING gist (
            room_id WITH =,
            tstzrange(start_time, end_time, '[)') WITH &&
        )
        WHERE (status != 'cancelled')
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE bookings
        DROP CONSTRAINT booking_no_room_overlap
        """
    )

    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT booking_no_room_overlap
        EXCLUDE USING gist (
            room_id WITH =,
            tstzrange(start_time, end_time, '[)') WITH &&
        )
        """
    )