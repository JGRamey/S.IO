"""Add analysis result tables

Revision ID: analysis_tables_001
Revises: hybrid_database_001
Create Date: 2024-12-22 14:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'analysis_tables_001'
down_revision: Union[str, None] = 'hybrid_database_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add analysis result tables for storing AI agent analysis results separately from main data."""
    
    # FallacyAnalysis table - Complete fallacy analysis results
    op.create_table('fallacy_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('text_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_fallacies', sa.Integer(), nullable=False, default=0),
        sa.Column('average_confidence', sa.Float(), nullable=False, default=0.0),
        sa.Column('logical_quality_score', sa.Float(), nullable=False, default=100.0),
        sa.Column('quality_assessment', sa.String(length=50), nullable=True),
        sa.Column('analysis_summary', sa.JSON(), nullable=False, default={}),
        sa.Column('fallacy_categories', sa.JSON(), nullable=False, default={}),
        sa.Column('improvement_suggestions', postgresql.ARRAY(sa.String()), nullable=False, default={}),
        sa.Column('agent_version', sa.String(length=50), nullable=False, default='1.0'),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('rag_context_used', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['text_id'], ['spiritual_texts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('text_id')
    )

    # DoctrineAnalysis table - Complete doctrine analysis results
    op.create_table('doctrine_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('text_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_doctrines', sa.Integer(), nullable=False, default=0),
        sa.Column('average_confidence', sa.Float(), nullable=False, default=0.0),
        sa.Column('dominant_tradition', sa.String(length=100), nullable=True),
        sa.Column('doctrinal_diversity', sa.Float(), nullable=False, default=0.0),
        sa.Column('detected_doctrines', sa.JSON(), nullable=False, default=[]),
        sa.Column('tradition_distribution', sa.JSON(), nullable=False, default={}),
        sa.Column('cross_tradition_analysis', sa.JSON(), nullable=False, default={}),
        sa.Column('rag_enhancement', sa.JSON(), nullable=True),
        sa.Column('agent_version', sa.String(length=50), nullable=False, default='1.0'),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('rag_context_used', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['text_id'], ['spiritual_texts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('text_id')
    )

    # ThemeAnalysis table - Complete theme analysis results
    op.create_table('theme_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('text_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_themes', sa.Integer(), nullable=False, default=0),
        sa.Column('average_confidence', sa.Float(), nullable=False, default=0.0),
        sa.Column('dominant_theme', sa.String(length=200), nullable=True),
        sa.Column('theme_diversity', sa.Float(), nullable=False, default=0.0),
        sa.Column('detected_themes', sa.JSON(), nullable=False, default=[]),
        sa.Column('theme_categories', sa.JSON(), nullable=False, default={}),
        sa.Column('universal_themes', postgresql.ARRAY(sa.String()), nullable=False, default={}),
        sa.Column('cross_tradition_themes', sa.JSON(), nullable=False, default={}),
        sa.Column('rag_enhancement', sa.JSON(), nullable=True),
        sa.Column('agent_version', sa.String(length=50), nullable=False, default='1.0'),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('rag_context_used', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['text_id'], ['spiritual_texts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('text_id')
    )

    # TranslationAnalysis table - Translation quality analysis results
    op.create_table('translation_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('original_text_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('translated_text_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('accuracy_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('semantic_similarity', sa.Float(), nullable=False, default=0.0),
        sa.Column('cultural_adaptation', sa.Float(), nullable=False, default=0.0),
        sa.Column('detected_issues', sa.JSON(), nullable=False, default=[]),
        sa.Column('improvement_suggestions', postgresql.ARRAY(sa.String()), nullable=False, default={}),
        sa.Column('translation_chain', postgresql.ARRAY(sa.String()), nullable=False, default={}),
        sa.Column('chain_quality_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('rag_enhancement', sa.JSON(), nullable=True),
        sa.Column('agent_version', sa.String(length=50), nullable=False, default='1.0'),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('rag_context_used', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['original_text_id'], ['spiritual_texts.id'], ),
        sa.ForeignKeyConstraint(['translated_text_id'], ['spiritual_texts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('original_text_id', 'translated_text_id')
    )

    # TextSourceAnalysis table - Text sourcing and authenticity analysis
    op.create_table('text_source_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('text_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('authenticity_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('source_reliability', sa.Float(), nullable=False, default=0.0),
        sa.Column('manuscript_quality', sa.Float(), nullable=False, default=0.0),
        sa.Column('source_chain', sa.JSON(), nullable=False, default=[]),
        sa.Column('historical_context', sa.Text(), nullable=True),
        sa.Column('provenance_notes', sa.Text(), nullable=True),
        sa.Column('quality_indicators', sa.JSON(), nullable=False, default={}),
        sa.Column('concerns', postgresql.ARRAY(sa.String()), nullable=False, default={}),
        sa.Column('recommendations', postgresql.ARRAY(sa.String()), nullable=False, default={}),
        sa.Column('rag_enhancement', sa.JSON(), nullable=True),
        sa.Column('agent_version', sa.String(length=50), nullable=False, default='1.0'),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('rag_context_used', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['text_id'], ['spiritual_texts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('text_id')
    )

    # Update LogicalFallacy table structure (enhance existing)
    op.add_column('logical_fallacies', sa.Column('severity', sa.String(length=50), nullable=False, default='moderate'))
    op.add_column('logical_fallacies', sa.Column('analysis_version', sa.String(length=50), nullable=False, default='1.0'))
    op.alter_column('logical_fallacies', 'context', nullable=True)
    op.alter_column('logical_fallacies', 'detected_by', nullable=False, default='fallacy_detection_agent')

    # Create indexes for performance
    op.create_index('idx_fallacy_analyses_text_id', 'fallacy_analyses', ['text_id'])
    op.create_index('idx_doctrine_analyses_text_id', 'doctrine_analyses', ['text_id'])
    op.create_index('idx_theme_analyses_text_id', 'theme_analyses', ['text_id'])
    op.create_index('idx_translation_analyses_original', 'translation_analyses', ['original_text_id'])
    op.create_index('idx_translation_analyses_translated', 'translation_analyses', ['translated_text_id'])
    op.create_index('idx_text_source_analyses_text_id', 'text_source_analyses', ['text_id'])
    
    # Analysis performance indexes
    op.create_index('idx_fallacy_analyses_quality', 'fallacy_analyses', ['logical_quality_score'])
    op.create_index('idx_doctrine_analyses_tradition', 'doctrine_analyses', ['dominant_tradition'])
    op.create_index('idx_theme_analyses_theme', 'theme_analyses', ['dominant_theme'])


def downgrade() -> None:
    """Remove analysis result tables."""
    
    # Drop indexes
    op.drop_index('idx_theme_analyses_theme')
    op.drop_index('idx_doctrine_analyses_tradition')
    op.drop_index('idx_fallacy_analyses_quality')
    op.drop_index('idx_text_source_analyses_text_id')
    op.drop_index('idx_translation_analyses_translated')
    op.drop_index('idx_translation_analyses_original')
    op.drop_index('idx_theme_analyses_text_id')
    op.drop_index('idx_doctrine_analyses_text_id')
    op.drop_index('idx_fallacy_analyses_text_id')
    
    # Revert LogicalFallacy changes
    op.drop_column('logical_fallacies', 'analysis_version')
    op.drop_column('logical_fallacies', 'severity')
    op.alter_column('logical_fallacies', 'context', nullable=False)
    op.alter_column('logical_fallacies', 'detected_by', nullable=False)
    
    # Drop analysis tables
    op.drop_table('text_source_analyses')
    op.drop_table('translation_analyses')
    op.drop_table('theme_analyses')
    op.drop_table('doctrine_analyses')
    op.drop_table('fallacy_analyses')
