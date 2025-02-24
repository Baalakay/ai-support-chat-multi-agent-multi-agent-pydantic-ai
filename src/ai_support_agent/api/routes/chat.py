"""Chat endpoint with SSE streaming for agent responses."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from typing import Optional, Dict, Any, List
import json
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext

from ...agents.customer_support import CustomerSupportAgent, CustomerSupportResponse
from ...core.dependencies import get_agent_context
from ...core.db import get_db_client
from ...types.chat import ChatMessage, ChatResponse
from ...types.agent import AgentDependencies

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatMessage(ai.BaseModel):
    """Chat message request model."""
    message: str
    context: Optional[Dict[str, Any]] = None

async def stream_agent_response(
    agent: CustomerSupportAgent,
    message: ChatMessage
) -> AsyncGenerator[str, None]:
    """Stream agent response events."""
    try:
        # Initial thinking event
        yield json.dumps({
            "event": "thinking",
            "data": {"message": "Analyzing your query..."}
        })
        
        # Get agent response
        response = await agent.analyze_query(
            query=message.message,
            context=message.context
        )
        
        # If specialist consultation is needed
        if response.requires_specialist:
            yield json.dumps({
                "event": "specialist",
                "data": {
                    "message": "Consulting product specialist...",
                    "specialist_type": response.specialist_type
                }
            })
            
            # Wait for specialist response (already handled in analyze_query)
            await asyncio.sleep(0.1)  # Small delay for UI
        
        # Send final response
        yield json.dumps({
            "event": "response",
            "data": response.model_dump()
        })
        
        # Completion event
        yield json.dumps({
            "event": "complete",
            "data": {"message": "Analysis complete"}
        })
        
    except Exception as e:
        yield json.dumps({
            "event": "error",
            "data": {
                "message": "Error processing query",
                "error": str(e)
            }
        })

@router.post("/message")
async def chat_message(
    message: ChatMessage,
    request: Request,
    agent_context: ai.Context = Depends(get_agent_context)
) -> StreamingResponse:
    """
    Chat message endpoint with SSE streaming.
    
    Args:
        message: The chat message and context
        request: FastAPI request object
        agent_context: Agent context with dependencies
        
    Returns:
        Streaming response with agent events
    """
    try:
        # Create agent with context
        agent = CustomerSupportAgent(context=agent_context)
        
        # Return SSE response
        return EventSourceResponse(
            stream_agent_response(agent, message),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

@router.get("/history")
async def chat_history(
    session_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get chat history for a session.
    
    Args:
        session_id: The session ID
        limit: Maximum number of messages to return
        
    Returns:
        List of chat messages and responses
    """
    try:
        db = await get_db_client()
        async with db._client.pool.acquire() as conn:
            # Get queries and responses
            result = await conn.fetch("""
                SELECT 
                    q.query_text,
                    q.query_type,
                    q.created_at as query_time,
                    r.response_data,
                    r.created_at as response_time
                FROM agent_queries q
                LEFT JOIN agent_responses r ON r.query_id = q.id
                WHERE q.session_id = $1
                ORDER BY q.created_at DESC
                LIMIT $2
            """, session_id, limit)
            
            return [dict(row) for row in result]
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        ) 