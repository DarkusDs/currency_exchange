"""create initial tables

Revision ID: 95063535a886
Revises: 
Create Date: 2026-03-13 17:00:49.805733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95063535a886'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            bank VARCHAR(10) NOT NULL,
            code VARCHAR(10) NOT NULL,
            name VARCHAR(100),
            rate DECIMAL(12,6) NOT NULL,
            rate_date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            request_id CHAR(36),
            INDEX (request_id)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TABLE IF EXISTS exchange_rates")
