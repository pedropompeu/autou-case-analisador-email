"""phase_4_workflows_notes_rules

Revision ID: d9e71ab523f1
Revises: 39030255bf15
Create Date: 2026-09-19 16:48:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9e71ab523f1'
down_revision = '39030255bf15'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Update email_analyses with status and assigned_to_user_id
    with op.batch_alter_table('email_analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=30), server_default='pending', nullable=False))
        batch_op.add_column(sa.Column('assigned_to_user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_email_analyses_assigned_user', 'users', ['assigned_to_user_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index(batch_op.f('ix_email_analyses_assigned_to_user_id'), ['assigned_to_user_id'], unique=False)

    # 2. Create internal_notes
    op.create_table('internal_notes',
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['email_analyses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('internal_notes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_internal_notes_analysis_id'), ['analysis_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_internal_notes_tenant_id'), ['tenant_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_internal_notes_user_id'), ['user_id'], unique=False)

    # 3. Create routing_rules
    op.create_table('routing_rules',
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('condition_field', sa.String(length=50), nullable=False),
        sa.Column('condition_operator', sa.String(length=30), nullable=False),
        sa.Column('condition_value', sa.String(length=255), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('action_payload', sa.JSON(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('routing_rules', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_routing_rules_tenant_id'), ['tenant_id'], unique=False)


def downgrade():
    with op.batch_alter_table('routing_rules', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_routing_rules_tenant_id'))

    op.drop_table('routing_rules')

    with op.batch_alter_table('internal_notes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_internal_notes_user_id'))
        batch_op.drop_index(batch_op.f('ix_internal_notes_tenant_id'))
        batch_op.drop_index(batch_op.f('ix_internal_notes_analysis_id'))

    op.drop_table('internal_notes')

    with op.batch_alter_table('email_analyses', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_email_analyses_assigned_to_user_id'))
        batch_op.drop_constraint('fk_email_analyses_assigned_user', type_='foreignkey')
        batch_op.drop_column('assigned_to_user_id')
        batch_op.drop_column('status')
