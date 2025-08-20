from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0006_create_bookings"
down_revision = "0005_create_availability_blocks"
branch_labels = None
depends_on = None

def upgrade():
    booking_status = postgresql.ENUM(
        "pending", "confirmed", "cancelled", "completed",
        name="booking_status"
    )
    booking_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "car_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cars.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "renter_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(              
                name="booking_status",
                create_type=False        
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("total_price_cents", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("start_date <= end_date", name="booking_start_before_end"),
        sa.CheckConstraint("total_price_cents > 0", name="booking_price_positive"),
    )
    op.create_index("ix_bookings_car_id", "bookings", ["car_id"])
    op.create_index("ix_bookings_renter_id", "bookings", ["renter_id"])

def downgrade():
    op.drop_index("ix_bookings_renter_id", table_name="bookings")
    op.drop_index("ix_bookings_car_id", table_name="bookings")
    op.drop_table("bookings")
    booking_status = postgresql.ENUM(name="booking_status")
    booking_status.drop(op.get_bind(), checkfirst=True)
