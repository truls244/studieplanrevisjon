"""fixed program ansvarlig

Revision ID: c9c2f94d037e
Revises: 9a1ee8dd6ba4
Create Date: 2025-05-15 01:48:53.342733

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'c9c2f94d037e'
down_revision = '9a1ee8dd6ba4'
branch_labels = None
depends_on = None


def upgrade():
    # Add foreign key in studyprogram table for program_ansvarlig
    with op.batch_alter_table('studyprogram') as batch_op:
        # Drop the original program_ansvarlig column
        batch_op.drop_column('program_ansvarlig')
        # Add new program_ansvarlig as a foreign key to user table
        batch_op.add_column(sa.Column('program_ansvarlig_id', sa.Integer(), nullable=True))
        # Add the foreign key constraint with explicit name
        batch_op.create_foreign_key(
            constraint_name='fk_studyprogram_program_ansvarlig_id_user',
            referent_table='user',
            local_cols=['program_ansvarlig_id'],
            remote_cols=['id']
        )


def downgrade():
    # Revert changes
    with op.batch_alter_table('studyprogram') as batch_op:
        # Drop the foreign key constraint first
        batch_op.drop_constraint('fk_studyprogram_program_ansvarlig_id_user', type_='foreignkey')
        # Remove the foreign key column
        batch_op.drop_column('program_ansvarlig_id')
        # Add back the original string column
        batch_op.add_column(sa.Column('program_ansvarlig', sa.String(80), nullable=True))