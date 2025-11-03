"""OAuth authentication routes."""

from uuid import uuid4
from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from ...core.oauth import get_authorization_url, exchange_code_for_token
from ...core.db import get_session
from ...models import OAuthToken, RunLog

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/etsy/login")
def etsy_login():
    """Initiate Etsy OAuth flow."""
    state = str(uuid4())
    url = get_authorization_url(state)
    return RedirectResponse(url=url, status_code=303)


@router.get("/etsy/callback")
def etsy_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    shop_id: str | None = Query(None, description="Optional shop ID to associate with this token")
):
    """Handle Etsy OAuth callback."""
    if error:
        with next(get_session()) as session:
            session.add(RunLog(job="etsy_oauth", status="error", message=error))
            session.commit()
        return RedirectResponse(url="/settings", status_code=303)
    
    if code:
        try:
            token = exchange_code_for_token(code, shop_id=shop_id)
            with next(get_session()) as session:
                session.add(RunLog(job="etsy_oauth", status="ok", message=f"connected to shop {token.shop_id or 'default'}"))
                session.commit()
        except Exception as e:
            with next(get_session()) as session:
                session.add(RunLog(job="etsy_oauth", status="error", message=str(e)))
                session.commit()
    
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/etsy/refresh")
def refresh_etsy_token():
    """Refresh Etsy access token."""
    from ...core.oauth import refresh_access_token
    
    token = refresh_access_token()
    if token:
        return {"status": "ok", "message": "Token refreshed"}
    return {"status": "error", "message": "Failed to refresh token"}

