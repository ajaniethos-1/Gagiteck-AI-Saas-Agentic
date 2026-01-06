"""Search API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# --- Models ---

class SearchResult(BaseModel):
    """Individual search result."""
    id: str
    type: str  # 'agent', 'workflow', 'execution'
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    score: float  # Relevance score


class SearchResponse(BaseModel):
    """Search response with results."""
    query: str
    results: List[SearchResult]
    total: int
    took_ms: float


# --- Search Service ---

class SearchService:
    """Service for searching across resources."""

    @staticmethod
    def search_text(query: str, text: str) -> float:
        """Simple text search scoring."""
        if not query or not text:
            return 0.0

        query_lower = query.lower()
        text_lower = text.lower()

        # Exact match
        if query_lower == text_lower:
            return 1.0

        # Contains
        if query_lower in text_lower:
            return 0.8

        # Word match
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        matching_words = query_words & text_words
        if matching_words:
            return len(matching_words) / len(query_words) * 0.6

        return 0.0


search_service = SearchService()


# --- Endpoints ---

@router.get(
    "",
    response_model=SearchResponse,
    summary="Search",
    description="Search across agents, workflows, and executions.",
)
async def search(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    types: Optional[str] = Query(None, description="Comma-separated types to search (agent,workflow,execution)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
):
    """Search across all resources."""
    import time
    start_time = time.time()

    # Parse types filter
    type_filter = None
    if types:
        type_filter = [t.strip() for t in types.split(',')]

    results: List[SearchResult] = []

    # Search agents
    if not type_filter or 'agent' in type_filter:
        from api.routes.agents import _agents_db
        for agent in _agents_db.values():
            if status and agent.get('status') != status:
                continue

            # Calculate score
            name_score = search_service.search_text(q, agent.get('name', ''))
            prompt_score = search_service.search_text(q, agent.get('system_prompt', '') or '')
            score = max(name_score, prompt_score * 0.7)

            if score > 0:
                results.append(SearchResult(
                    id=agent['id'],
                    type='agent',
                    name=agent['name'],
                    description=agent.get('system_prompt', '')[:100] if agent.get('system_prompt') else None,
                    status=agent.get('status', 'unknown'),
                    created_at=agent['created_at'],
                    score=score,
                ))

    # Search workflows
    if not type_filter or 'workflow' in type_filter:
        from api.routes.workflows import _workflows_db
        for workflow in _workflows_db.values():
            if status and workflow.get('status') != status:
                continue

            name_score = search_service.search_text(q, workflow.get('name', ''))
            desc_score = search_service.search_text(q, workflow.get('description', '') or '')
            score = max(name_score, desc_score * 0.7)

            if score > 0:
                results.append(SearchResult(
                    id=workflow['id'],
                    type='workflow',
                    name=workflow['name'],
                    description=workflow.get('description'),
                    status=workflow.get('status', 'unknown'),
                    created_at=workflow['created_at'],
                    score=score,
                ))

    # Search executions
    if not type_filter or 'execution' in type_filter:
        from api.routes.executions import _executions_db
        for execution in _executions_db.values():
            if status and execution.get('status') != status:
                continue

            # Search by ID or resource ID
            id_score = search_service.search_text(q, execution.get('id', ''))
            resource_score = search_service.search_text(q, execution.get('resource_id', ''))
            score = max(id_score, resource_score)

            if score > 0:
                results.append(SearchResult(
                    id=execution['id'],
                    type='execution',
                    name=f"{execution['type']} execution",
                    description=f"Resource: {execution.get('resource_id', 'unknown')}",
                    status=execution.get('status', 'unknown'),
                    created_at=execution['started_at'],
                    score=score,
                ))

    # Sort by score and limit
    results.sort(key=lambda x: x.score, reverse=True)
    results = results[:limit]

    took_ms = (time.time() - start_time) * 1000

    return SearchResponse(
        query=q,
        results=results,
        total=len(results),
        took_ms=took_ms,
    )


@router.get(
    "/suggestions",
    summary="Search suggestions",
    description="Get search suggestions based on partial query.",
)
async def search_suggestions(
    q: str = Query(..., min_length=1, max_length=50, description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Maximum suggestions"),
):
    """Get search suggestions."""
    suggestions = []

    # Collect names from all resources
    from api.routes.agents import _agents_db
    from api.routes.workflows import _workflows_db

    q_lower = q.lower()

    for agent in _agents_db.values():
        name = agent.get('name', '')
        if q_lower in name.lower():
            suggestions.append({'text': name, 'type': 'agent'})

    for workflow in _workflows_db.values():
        name = workflow.get('name', '')
        if q_lower in name.lower():
            suggestions.append({'text': name, 'type': 'workflow'})

    # Deduplicate and limit
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s['text'] not in seen:
            seen.add(s['text'])
            unique_suggestions.append(s)
            if len(unique_suggestions) >= limit:
                break

    return {'suggestions': unique_suggestions}
