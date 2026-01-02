"""Webhook API endpoints and service."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, HttpUrl
import httpx
import hashlib
import hmac
import json
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---

class WebhookCreate(BaseModel):
    """Request to create a webhook."""
    url: HttpUrl = Field(..., description="The URL to send webhook events to")
    events: List[str] = Field(..., description="List of events to subscribe to", examples=[["execution.completed", "execution.failed"]])
    secret: Optional[str] = Field(None, description="Secret for signing webhook payloads")
    description: Optional[str] = Field(None, description="Description of this webhook")
    is_active: bool = Field(True, description="Whether the webhook is active")


class WebhookUpdate(BaseModel):
    """Request to update a webhook."""
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Webhook(BaseModel):
    """Webhook response model."""
    id: str
    url: str
    events: List[str]
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime] = None
    failure_count: int = 0


class WebhookList(BaseModel):
    """Paginated list of webhooks."""
    data: List[Webhook]
    total: int


class WebhookEvent(BaseModel):
    """Webhook event payload."""
    id: str
    type: str
    timestamp: datetime
    data: dict


# Supported webhook events
WEBHOOK_EVENTS = [
    "agent.created",
    "agent.updated",
    "agent.deleted",
    "workflow.created",
    "workflow.updated",
    "workflow.deleted",
    "execution.started",
    "execution.completed",
    "execution.failed",
    "execution.cancelled",
]


# --- In-memory storage (replace with database) ---
_webhooks_db: dict[str, dict] = {}


# --- Webhook Service ---

class WebhookService:
    """Service for managing and triggering webhooks."""

    @staticmethod
    def sign_payload(payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def send_webhook(webhook: dict, event: WebhookEvent) -> bool:
        """Send webhook event to the configured URL."""
        payload = json.dumps({
            "id": event.id,
            "type": event.type,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
        })

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event.type,
            "X-Webhook-ID": event.id,
            "X-Webhook-Timestamp": event.timestamp.isoformat(),
        }

        # Add signature if secret is configured
        if webhook.get("secret"):
            signature = WebhookService.sign_payload(payload, webhook["secret"])
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook["url"],
                    content=payload,
                    headers=headers,
                )
                response.raise_for_status()
                logger.info(f"Webhook {webhook['id']} delivered successfully to {webhook['url']}")
                return True
        except Exception as e:
            logger.error(f"Webhook {webhook['id']} delivery failed: {e}")
            return False

    @staticmethod
    async def trigger_event(event_type: str, data: dict):
        """Trigger webhooks for a specific event type."""
        event = WebhookEvent(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
        )

        for webhook in _webhooks_db.values():
            if not webhook.get("is_active", True):
                continue
            if event_type not in webhook.get("events", []):
                continue

            success = await WebhookService.send_webhook(webhook, event)

            # Update webhook stats
            webhook["last_triggered_at"] = datetime.utcnow()
            if not success:
                webhook["failure_count"] = webhook.get("failure_count", 0) + 1
            else:
                webhook["failure_count"] = 0


webhook_service = WebhookService()


# --- Endpoints ---

@router.get(
    "",
    response_model=WebhookList,
    summary="List webhooks",
    description="Retrieve all configured webhooks.",
)
async def list_webhooks():
    """List all webhooks."""
    webhooks = list(_webhooks_db.values())
    return WebhookList(
        data=[Webhook(**w) for w in webhooks],
        total=len(webhooks),
    )


@router.post(
    "",
    response_model=Webhook,
    status_code=201,
    summary="Create webhook",
    description="Create a new webhook subscription.",
)
async def create_webhook(request: WebhookCreate):
    """Create a new webhook."""
    # Validate events
    invalid_events = set(request.events) - set(WEBHOOK_EVENTS)
    if invalid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid events: {invalid_events}. Valid events: {WEBHOOK_EVENTS}"
        )

    webhook_id = f"wh_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    webhook = {
        "id": webhook_id,
        "url": str(request.url),
        "events": request.events,
        "secret": request.secret,
        "description": request.description,
        "is_active": request.is_active,
        "created_at": now,
        "updated_at": now,
        "last_triggered_at": None,
        "failure_count": 0,
    }

    _webhooks_db[webhook_id] = webhook
    return Webhook(**webhook)


@router.get(
    "/events",
    summary="List webhook events",
    description="Get list of all available webhook event types.",
)
async def list_webhook_events():
    """List all available webhook event types."""
    return {
        "events": WEBHOOK_EVENTS,
        "categories": {
            "agent": ["agent.created", "agent.updated", "agent.deleted"],
            "workflow": ["workflow.created", "workflow.updated", "workflow.deleted"],
            "execution": ["execution.started", "execution.completed", "execution.failed", "execution.cancelled"],
        }
    }


@router.get(
    "/{webhook_id}",
    response_model=Webhook,
    summary="Get webhook",
    description="Retrieve a specific webhook by ID.",
)
async def get_webhook(webhook_id: str):
    """Get a webhook by ID."""
    if webhook_id not in _webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return Webhook(**_webhooks_db[webhook_id])


@router.patch(
    "/{webhook_id}",
    response_model=Webhook,
    summary="Update webhook",
    description="Update a webhook's configuration.",
)
async def update_webhook(webhook_id: str, request: WebhookUpdate):
    """Update a webhook."""
    if webhook_id not in _webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook = _webhooks_db[webhook_id]

    if request.url is not None:
        webhook["url"] = str(request.url)
    if request.events is not None:
        invalid_events = set(request.events) - set(WEBHOOK_EVENTS)
        if invalid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid events: {invalid_events}"
            )
        webhook["events"] = request.events
    if request.secret is not None:
        webhook["secret"] = request.secret
    if request.description is not None:
        webhook["description"] = request.description
    if request.is_active is not None:
        webhook["is_active"] = request.is_active

    webhook["updated_at"] = datetime.utcnow()
    return Webhook(**webhook)


@router.delete(
    "/{webhook_id}",
    status_code=204,
    summary="Delete webhook",
    description="Delete a webhook.",
)
async def delete_webhook(webhook_id: str):
    """Delete a webhook."""
    if webhook_id not in _webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    del _webhooks_db[webhook_id]


@router.post(
    "/{webhook_id}/test",
    summary="Test webhook",
    description="Send a test event to the webhook.",
)
async def test_webhook(webhook_id: str, background_tasks: BackgroundTasks):
    """Send a test event to the webhook."""
    if webhook_id not in _webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook = _webhooks_db[webhook_id]
    test_event = WebhookEvent(
        id=f"evt_{uuid.uuid4().hex[:12]}",
        type="test",
        timestamp=datetime.utcnow(),
        data={"message": "This is a test webhook event"},
    )

    # Send test webhook in background
    background_tasks.add_task(WebhookService.send_webhook, webhook, test_event)

    return {"message": "Test webhook queued", "event_id": test_event.id}
