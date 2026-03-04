"""
API dependencies: authentication and tenant scoping.
"""
import os
from typing import Optional
from fastapi import Header, HTTPException, status
from pydantic import BaseModel


class AuthContext(BaseModel):
    tenant_id: str
    api_key: str
    role: str = "owner"


def get_auth_context(
    x_api_key: str = Header(..., alias="X-API-Key"),
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    x_role: Optional[str] = Header("owner", alias="X-Role")
) -> AuthContext:
    """Validate API key and tenant headers.

    In production, this would validate JWT/OAuth tokens and load RBAC from DB.
    Here we enforce an API key from env and require tenant scoping.
    """
    expected_key = os.getenv("PAPERPILOT_API_KEY")
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    if not x_tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant required")

    role = x_role or "owner"
    return AuthContext(tenant_id=x_tenant_id, api_key=x_api_key, role=role)
