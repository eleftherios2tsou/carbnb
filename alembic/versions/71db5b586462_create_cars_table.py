from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_create_cars"
down_revision = "0002_create_profiles"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "cars",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("make", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("seats", sa.Integer(), nullable=False),
        sa.Column("transmission", sa.String(), nullable=False),
        sa.Column("fuel", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("daily_price_cents", sa.Integer(), nullable=False),
        sa.Column("location_text", sa.String(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("year BETWEEN 1980 AND EXTRACT(YEAR FROM now())::int + 1", name="car_year_valid"),
        sa.CheckConstraint("seats > 0", name="car_seats_positive"),
        sa.CheckConstraint("daily_price_cents > 0", name="car_price_positive"),
        sa.CheckConstraint("transmission IN ('manual','automatic')", name="car_transmission_valid"),
    )
    op.create_index("ix_cars_owner_id", "cars", ["owner_id"])

def downgrade():
    op.drop_index("ix_cars_owner_id", table_name="cars")
    op.drop_table("cars")
