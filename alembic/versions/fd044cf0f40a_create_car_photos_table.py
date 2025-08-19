from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_create_car_photos"
down_revision = "0003_create_cars"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "car_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("car_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("is_cover", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_car_photos_car_id", "car_photos", ["car_id"])

def downgrade():
    op.drop_index("ix_car_photos_car_id", table_name="car_photos")
    op.drop_table("car_photos")
