"""Text management API routes."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from solomon.database import get_db_session, SpiritualText, TextType, Language
from solomon.agents.orchestrator import AgentOrchestrator, OrchestrationRequest, AnalysisType

router = APIRouter()


class TextCreate(BaseModel):
    """Model for creating a new text."""
    title: str
    text_type: TextType
    language: Language
    content: str
    source_url: Optional[str] = None
    manuscript_source: Optional[str] = None
    publication_date: Optional[datetime] = None
    book: Optional[str] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None


class TextResponse(BaseModel):
    """Model for text responses."""
    id: str
    title: str
    text_type: TextType
    language: Language
    content: str
    source_url: Optional[str] = None
    manuscript_source: Optional[str] = None
    publication_date: Optional[datetime] = None
    book: Optional[str] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TextSearchRequest(BaseModel):
    """Model for text search requests."""
    query: str
    text_type: Optional[TextType] = None
    language: Optional[Language] = None
    tradition: Optional[str] = None
    limit: int = Field(default=10, le=100)


class TextSearchResponse(BaseModel):
    """Model for text search responses."""
    texts: List[TextResponse]
    total: int
    query: str
    execution_time: float


def get_orchestrator() -> AgentOrchestrator:
    """Get orchestrator dependency."""
    from solomon.api.main import orchestrator
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    return orchestrator


@router.post("/", response_model=TextResponse)
async def create_text(
    text_data: TextCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new spiritual text."""
    try:
        # Create new text
        new_text = SpiritualText(
            title=text_data.title,
            text_type=text_data.text_type,
            language=text_data.language,
            content=text_data.content,
            source_url=text_data.source_url,
            manuscript_source=text_data.manuscript_source,
            publication_date=text_data.publication_date,
            book=text_data.book,
            chapter=text_data.chapter,
            verse=text_data.verse
        )
        
        db.add(new_text)
        await db.commit()
        await db.refresh(new_text)
        
        return TextResponse.from_orm(new_text)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create text: {str(e)}")


@router.get("/{text_id}", response_model=TextResponse)
async def get_text(
    text_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific text by ID."""
    try:
        result = await db.execute(
            select(SpiritualText).where(SpiritualText.id == text_id)
        )
        text = result.scalar_one_or_none()
        
        if not text:
            raise HTTPException(status_code=404, detail="Text not found")
        
        return TextResponse.from_orm(text)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve text: {str(e)}")


@router.get("/", response_model=List[TextResponse])
async def list_texts(
    text_type: Optional[TextType] = Query(None),
    language: Optional[Language] = Query(None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    """List texts with optional filtering."""
    try:
        query = select(SpiritualText)
        
        # Apply filters
        if text_type:
            query = query.where(SpiritualText.text_type == text_type)
        if language:
            query = query.where(SpiritualText.language == language)
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        query = query.order_by(SpiritualText.created_at.desc())
        
        result = await db.execute(query)
        texts = result.scalars().all()
        
        return [TextResponse.from_orm(text) for text in texts]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list texts: {str(e)}")


@router.post("/search", response_model=TextSearchResponse)
async def search_texts(
    search_request: TextSearchRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_db_session)
):
    """Search for texts using the text sourcing agent."""
    start_time = datetime.now()
    
    try:
        # Use text sourcing agent to find texts
        orchestration_request = OrchestrationRequest(
            analysis_type=AnalysisType.TEXT_SOURCING,
            query=search_request.query,
            parameters={
                "text_type": search_request.text_type.value if search_request.text_type else None,
                "language": search_request.language.value if search_request.language else None,
                "tradition": search_request.tradition,
                "limit": search_request.limit
            }
        )
        
        result = await orchestrator.execute_analysis(orchestration_request)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=f"Search failed: {result.error}")
        
        # Also search local database
        query = select(SpiritualText)
        
        # Simple text search in content and title
        search_term = f"%{search_request.query}%"
        query = query.where(
            (SpiritualText.title.ilike(search_term)) |
            (SpiritualText.content.ilike(search_term))
        )
        
        # Apply filters
        if search_request.text_type:
            query = query.where(SpiritualText.text_type == search_request.text_type)
        if search_request.language:
            query = query.where(SpiritualText.language == search_request.language)
        
        query = query.limit(search_request.limit)
        db_result = await db.execute(query)
        local_texts = db_result.scalars().all()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return TextSearchResponse(
            texts=[TextResponse.from_orm(text) for text in local_texts],
            total=len(local_texts),
            query=search_request.query,
            execution_time=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.put("/{text_id}", response_model=TextResponse)
async def update_text(
    text_id: str,
    text_data: TextCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update an existing text."""
    try:
        result = await db.execute(
            select(SpiritualText).where(SpiritualText.id == text_id)
        )
        text = result.scalar_one_or_none()
        
        if not text:
            raise HTTPException(status_code=404, detail="Text not found")
        
        # Update fields
        text.title = text_data.title
        text.text_type = text_data.text_type
        text.language = text_data.language
        text.content = text_data.content
        text.source_url = text_data.source_url
        text.manuscript_source = text_data.manuscript_source
        text.publication_date = text_data.publication_date
        text.book = text_data.book
        text.chapter = text_data.chapter
        text.verse = text_data.verse
        
        await db.commit()
        await db.refresh(text)
        
        return TextResponse.from_orm(text)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update text: {str(e)}")


@router.delete("/{text_id}")
async def delete_text(
    text_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a text."""
    try:
        result = await db.execute(
            select(SpiritualText).where(SpiritualText.id == text_id)
        )
        text = result.scalar_one_or_none()
        
        if not text:
            raise HTTPException(status_code=404, detail="Text not found")
        
        await db.delete(text)
        await db.commit()
        
        return {"message": "Text deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete text: {str(e)}")


@router.get("/types/available")
async def get_text_types():
    """Get available text types."""
    return {
        "text_types": [
            {"value": text_type.value, "name": text_type.value.replace("_", " ").title()}
            for text_type in TextType
        ]
    }


@router.get("/languages/available")
async def get_languages():
    """Get available languages."""
    return {
        "languages": [
            {"value": language.value, "name": language.value.replace("_", " ").title()}
            for language in Language
        ]
    }


@router.get("/stats")
async def get_text_statistics(db: AsyncSession = Depends(get_db_session)):
    """Get text collection statistics."""
    try:
        # Count by text type
        type_counts = await db.execute(
            select(SpiritualText.text_type, func.count(SpiritualText.id))
            .group_by(SpiritualText.text_type)
        )
        
        # Count by language
        language_counts = await db.execute(
            select(SpiritualText.language, func.count(SpiritualText.id))
            .group_by(SpiritualText.language)
        )
        
        # Total count
        total_result = await db.execute(select(func.count(SpiritualText.id)))
        total_texts = total_result.scalar()
        
        return {
            "total_texts": total_texts,
            "by_type": {row[0].value: row[1] for row in type_counts},
            "by_language": {row[0].value: row[1] for row in language_counts},
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
