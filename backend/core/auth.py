"""
OAuth2/OIDC RBAC utilities for FundTrace API.
Supports disabled/mock/jwt modes via AUTH_MODE setting.
"""

import base64
import json
from dataclasses import dataclass
from typing import List

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

from .config import get_settings


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://auth.local/authorize",
    tokenUrl="https://auth.local/token",
    auto_error=False,
)


@dataclass
class AuthUser:
    id: str
    roles: List[str]
    email: str | None = None


def _decode_jwt_unverified(token: str) -> dict:
    """
    Decode JWT payload without verifying signature.
    This is used only for mock/demo environments.
    """
    try:
        parts = token.split(".")
        if len(parts) < 2:
            raise ValueError("Invalid JWT format")
        payload = parts[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded.decode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid JWT payload") from exc


async def verify_investigator_access(token: str | None = Depends(oauth2_scheme)) -> AuthUser:
    """
    Verify the user has L2_Investigator access.
    """
    settings = get_settings()
    auth_mode = settings.AUTH_MODE

    if auth_mode == "disabled":
        return AuthUser(id="demo-user", roles=["L2_Investigator"], email="demo@fundtrace.ai")

    if auth_mode == "mock":
        if not token:
            raise HTTPException(status_code=401, detail="Missing token")
        if token == "demo-investigator":
            return AuthUser(id="demo-user", roles=["L2_Investigator"], email="demo@fundtrace.ai")
        raise HTTPException(status_code=403, detail="Invalid demo token")

    if auth_mode == "jwt":
        if not token:
            raise HTTPException(status_code=401, detail="Missing token")
        try:
            payload = _decode_jwt_unverified(token)
            roles = payload.get("roles", [])
            user_id = payload.get("sub", "unknown")
            email = payload.get("email")
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid token")

        if "L2_Investigator" not in roles:
            raise HTTPException(status_code=403, detail="Insufficient clearance")

        return AuthUser(id=user_id, roles=roles, email=email)

    raise HTTPException(status_code=500, detail="Invalid auth configuration")
