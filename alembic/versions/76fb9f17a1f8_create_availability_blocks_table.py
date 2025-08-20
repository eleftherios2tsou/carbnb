from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_create_availability_blocks"
down_revision = "0004_create_car_photos"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "availability_blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("car_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("start_date <= end_date", name="block_start_before_end"),
    )
    op.create_index("ix_blocks_car_id", "availability_blocks", ["car_id"])
    op.create_index("ix_blocks_car_dates", "availability_blocks", ["car_id", "start_date", "end_date"])

def downgrade():
    op.drop_index("ix_blocks_car_dates", table_name="availability_blocks")
    op.drop_index("ix_blocks_car_id", table_name="availability_blocks")
    op.drop_table("availability_blocks")
