"""add autoincrement in id column of elective_course table

Revision ID: 09e1a3172bf2
Revises: de332dbe1bb4
Create Date: 2024-05-13 14:34:00.745901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09e1a3172bf2'
down_revision: Union[str, None] = 'de332dbe1bb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('CREATE SEQUENCE elective_course_id_seq START WITH 1')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DROP SEQUENCE elective_course_id_seq')
    # ### end Alembic commands ###