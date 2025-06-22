"""create_hybrid_database_schema_with_categories

Revision ID: hybrid_db_001
Revises: e1847fb660ca
Create Date: 2025-06-22 13:47:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'hybrid_db_001'
down_revision = 'e1847fb660ca'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create field_categories table
    op.create_table('field_categories',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('field_name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('field_name')
    )
    
    # Create subfield_categories table
    op.create_table('subfield_categories',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('field_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('subfield_name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['field_id'], ['field_categories.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('field_id', 'subfield_name')
    )
    
    # Create spiritual_texts table with enhanced schema
    op.create_table('spiritual_texts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('text_type', sa.String(length=50), nullable=False),
    sa.Column('language', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('field_category_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('subfield_category_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('source_url', sa.String(length=1000), nullable=True),
    sa.Column('manuscript_source', sa.String(length=500), nullable=True),
    sa.Column('publication_date', sa.DateTime(), nullable=True),
    sa.Column('author', sa.String(length=300), nullable=True),
    sa.Column('publisher', sa.String(length=300), nullable=True),
    sa.Column('isbn', sa.String(length=20), nullable=True),
    sa.Column('doi', sa.String(length=100), nullable=True),
    sa.Column('edition', sa.String(length=100), nullable=True),
    sa.Column('page_count', sa.Integer(), nullable=True),
    sa.Column('book', sa.String(length=100), nullable=True),
    sa.Column('chapter', sa.Integer(), nullable=True),
    sa.Column('verse', sa.Integer(), nullable=True),
    sa.Column('verse_end', sa.Integer(), nullable=True),
    sa.Column('embedding_vector', postgresql.ARRAY(sa.Float()), nullable=True),
    sa.Column('qdrant_point_id', sa.String(length=100), nullable=True),
    sa.Column('embedding_model', sa.String(length=100), nullable=True),
    sa.Column('token_count', sa.Integer(), nullable=True),
    sa.Column('chunk_sequence', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['field_category_id'], ['field_categories.id'], ),
    sa.ForeignKeyConstraint(['subfield_category_id'], ['subfield_categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_spiritual_texts_type_lang', 'spiritual_texts', ['text_type', 'language'], unique=False)
    op.create_index('idx_spiritual_texts_book_chapter', 'spiritual_texts', ['book', 'chapter'], unique=False)
    op.create_index('idx_spiritual_texts_field_subfield', 'spiritual_texts', ['field_category_id', 'subfield_category_id'], unique=False)
    op.create_index('idx_spiritual_texts_qdrant', 'spiritual_texts', ['qdrant_point_id'], unique=False)
    
    # Create other existing tables (translations, doctrines, etc.)
    op.create_table('translations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('original_text_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('target_language', sa.String(length=50), nullable=False),
    sa.Column('translated_content', sa.Text(), nullable=False),
    sa.Column('translator', sa.String(length=200), nullable=True),
    sa.Column('translation_date', sa.DateTime(), nullable=True),
    sa.Column('translation_chain', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('accuracy_score', sa.Float(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['original_text_id'], ['spiritual_texts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('doctrines',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('tradition', sa.String(length=100), nullable=True),
    sa.Column('denomination', sa.String(length=100), nullable=True),
    sa.Column('origin_date', sa.DateTime(), nullable=True),
    sa.Column('historical_context', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    
    op.create_table('themes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('keywords', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    
    op.create_table('doctrine_references',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('text_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('doctrine_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('relevance_score', sa.Float(), nullable=False),
    sa.Column('context', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['doctrine_id'], ['doctrines.id'], ),
    sa.ForeignKeyConstraint(['text_id'], ['spiritual_texts.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('text_id', 'doctrine_id')
    )
    
    op.create_table('theme_references',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('text_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('theme_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('relevance_score', sa.Float(), nullable=False),
    sa.Column('context', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['text_id'], ['spiritual_texts.id'], ),
    sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('text_id', 'theme_id')
    )
    
    op.create_table('logical_fallacies',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('text_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('fallacy_type', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('context', sa.Text(), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('detected_by', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['text_id'], ['spiritual_texts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('contradictions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('text1_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('text2_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('contradiction_type', sa.String(length=100), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('detected_by', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['text1_id'], ['spiritual_texts.id'], ),
    sa.ForeignKeyConstraint(['text2_id'], ['spiritual_texts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('analysis_sessions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('query', sa.Text(), nullable=False),
    sa.Column('session_type', sa.String(length=50), nullable=True),
    sa.Column('parameters', sa.JSON(), nullable=True),
    sa.Column('results', sa.JSON(), nullable=True),
    sa.Column('texts_analyzed', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('execution_time', sa.Float(), nullable=True),
    sa.Column('tokens_used', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('analysis_sessions')
    op.drop_table('contradictions')
    op.drop_table('logical_fallacies')
    op.drop_table('theme_references')
    op.drop_table('doctrine_references')
    op.drop_table('themes')
    op.drop_table('doctrines')
    op.drop_table('translations')
    op.drop_index('idx_spiritual_texts_qdrant', table_name='spiritual_texts')
    op.drop_index('idx_spiritual_texts_field_subfield', table_name='spiritual_texts')
    op.drop_index('idx_spiritual_texts_book_chapter', table_name='spiritual_texts')
    op.drop_index('idx_spiritual_texts_type_lang', table_name='spiritual_texts')
    op.drop_table('spiritual_texts')
    op.drop_table('subfield_categories')
    op.drop_table('field_categories')
