"""
Auth Provider MCP Client

MCP client for authentication and authorization services.
Supports OAuth2, SAML, API keys, and role-based access control.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

from .base_client import BaseMCPClient, MCPRequest, MCPResponse
from .http_client import HTTPMCPClient
from ..exceptions import MCPError, AuthenticationError


logger = logging.getLogger(__name__)


class AuthenticationMethod(str, Enum):
    """Supported authentication methods"""
    BASIC = "basic"
    OAUTH2 = "oauth2"
    SAML = "saml"
    API_KEY = "api_key"
    LDAP = "ldap"
    MFA = "mfa"


@dataclass
class User:
    """User profile information"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    roles: List[str] = None
    permissions: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None


@dataclass
class Role:
    """Role with permissions"""
    id: str
    name: str
    description: str
    permissions: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Permission:
    """Permission definition"""
    resource: str
    action: str
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class AuthToken:
    """Authentication token"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    issued_at: Optional[str] = None
    user: Optional[User] = None


class AuthProviderMCPClient(HTTPMCPClient):
    """
    MCP client for authentication and authorization.
    
    Provides:
    - Multi-method authentication (OAuth2, SAML, Basic, API Key)
    - Role-based access control (RBAC)
    - API key management
    - Session management
    - Audit logging
    """
    
    def __init__(self, server_url: str, rate_limiter, circuit_breaker):
        """Initialize Auth Provider MCP client"""
        super().__init__(
            server_name="auth_provider",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    async def authenticate(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        method: AuthenticationMethod = AuthenticationMethod.BASIC
    ) -> MCPResponse[AuthToken]:
        """
        Authenticate user with specified method.
        
        Args:
            username: Username for basic auth
            password: Password for basic auth
            api_key: API key for key-based auth
            method: Authentication method
            
        Returns:
            Authentication token with user info
        """
        params = {"method": method.value}
        
        if method == AuthenticationMethod.BASIC:
            if not username or not password:
                return MCPResponse(
                    success=False,
                    error={
                        "code": "missing_credentials",
                        "message": "Username and password required for basic auth"
                    }
                )
            params.update({"username": username, "password": password})
        elif method == AuthenticationMethod.API_KEY:
            if not api_key:
                return MCPResponse(
                    success=False,
                    error={
                        "code": "missing_api_key",
                        "message": "API key required for key-based auth"
                    }
                )
            params["api_key"] = api_key
        
        request = MCPRequest(method="authenticate", params=params)
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        result = response["result"]
        token_data = result["token"]
        
        # Parse user if present
        user = None
        if "user" in result:
            user_data = result["user"]
            user = User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                roles=user_data.get("roles", [])
            )
        
        token = AuthToken(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data["expires_in"],
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
            issued_at=token_data.get("issued_at"),
            user=user
        )
        
        return MCPResponse(success=True, data=token)
    
    async def initiate_oauth2(
        self,
        client_id: str,
        redirect_uri: str,
        scopes: List[str],
        state: Optional[str] = None
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Initiate OAuth2 flow.
        
        Args:
            client_id: OAuth2 client ID
            redirect_uri: Callback URL
            scopes: Requested scopes
            state: Optional state parameter
            
        Returns:
            Authorization URL and state
        """
        request = MCPRequest(
            method="initiate_oauth2",
            params={
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scopes": scopes,
                "state": state
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def verify_token(
        self,
        token: str
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Verify access token validity.
        
        Args:
            token: Access token to verify
            
        Returns:
            Token validity and user info
        """
        request = MCPRequest(
            method="verify_token",
            params={"token": token}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def refresh_token(
        self,
        refresh_token: str
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access token
        """
        request = MCPRequest(
            method="refresh_token",
            params={"refresh_token": refresh_token}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def get_user_profile(
        self,
        user_id: str
    ) -> MCPResponse[User]:
        """
        Get user profile information.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile with roles and permissions
        """
        request = MCPRequest(
            method="get_user_profile",
            params={"user_id": user_id}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        user_data = response["result"]["user"]
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data.get("full_name"),
            roles=user_data.get("roles", []),
            permissions=user_data.get("permissions", []),
            metadata=user_data.get("metadata"),
            created_at=user_data.get("created_at"),
            last_login=user_data.get("last_login")
        )
        
        return MCPResponse(success=True, data=user)
    
    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Check if user has permission.
        
        Args:
            user_id: User identifier
            resource: Resource to access
            action: Action to perform
            context: Additional context
            
        Returns:
            Permission check result
        """
        params = {
            "user_id": user_id,
            "resource": resource,
            "action": action
        }
        if context:
            params["context"] = context
        
        request = MCPRequest(
            method="check_permission",
            params=params
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def list_roles(self) -> MCPResponse[List[Role]]:
        """
        List available roles.
        
        Returns:
            List of roles with permissions
        """
        request = MCPRequest(
            method="list_roles",
            params={}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        roles = []
        for role_data in response["result"]["roles"]:
            role = Role(
                id=role_data["id"],
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"],
                metadata=role_data.get("metadata")
            )
            roles.append(role)
        
        return MCPResponse(success=True, data=roles)
    
    async def create_api_key(
        self,
        name: str,
        scopes: List[str],
        expires_in_days: Optional[int] = None
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Create new API key.
        
        Args:
            name: Key name/description
            scopes: Granted scopes
            expires_in_days: Expiration period
            
        Returns:
            Created API key details
        """
        params = {
            "name": name,
            "scopes": scopes
        }
        if expires_in_days:
            params["expires_in_days"] = expires_in_days
        
        request = MCPRequest(
            method="create_api_key",
            params=params
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def revoke_api_key(
        self,
        key_id: str
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Revoke API key.
        
        Args:
            key_id: Key identifier
            
        Returns:
            Revocation confirmation
        """
        request = MCPRequest(
            method="revoke_api_key",
            params={"key_id": key_id}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def initiate_saml(
        self,
        idp_name: str
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Initiate SAML authentication.
        
        Args:
            idp_name: Identity provider name
            
        Returns:
            SAML request and redirect URL
        """
        request = MCPRequest(
            method="initiate_saml",
            params={"idp_name": idp_name}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def initiate_mfa(
        self,
        user_id: str,
        method: str = "totp"
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Initiate multi-factor authentication.
        
        Args:
            user_id: User identifier
            method: MFA method (totp, sms, email)
            
        Returns:
            MFA challenge details
        """
        request = MCPRequest(
            method="initiate_mfa",
            params={
                "user_id": user_id,
                "method": method
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> MCPResponse[List[Dict[str, Any]]]:
        """
        Get authentication audit log.
        
        Args:
            user_id: Filter by user
            event_types: Filter by event types
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum results
            
        Returns:
            Audit log entries
        """
        params = {"limit": limit}
        
        if user_id:
            params["user_id"] = user_id
        if event_types:
            params["event_types"] = event_types
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        
        request = MCPRequest(
            method="get_audit_log",
            params=params
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]["events"]
        )
    
    async def get_active_sessions(
        self,
        user_id: str
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Get user's active sessions.
        
        Args:
            user_id: User identifier
            
        Returns:
            Active session information
        """
        request = MCPRequest(
            method="get_active_sessions",
            params={"user_id": user_id}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get auth service health status"""
        response = await self._send_request(MCPRequest(method="health", params={}))
        
        if "error" in response:
            return {
                "service_status": "unhealthy",
                "error": response["error"],
                "circuit_breaker_state": self.circuit_breaker.state.name
            }
        
        result = response.get("result", {})
        return {
            "service_status": result.get("status", "unknown"),
            "auth_methods": result.get("supported_methods", []),
            "token_types": result.get("token_types", []),
            "mfa_enabled": result.get("mfa_enabled", False),
            "circuit_breaker_state": self.circuit_breaker.state.name,
            "rate_limit_remaining": self.rate_limiter.get_remaining_requests(self.server_name)
        }