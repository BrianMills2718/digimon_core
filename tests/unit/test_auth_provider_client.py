"""
Tests for Auth Provider MCP Client

Tests the MCP client for authentication and authorization services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import json

from src.integrations.mcp.auth_provider_client import (
    AuthProviderMCPClient,
    AuthToken,
    User,
    Role,
    Permission,
    AuthenticationMethod
)
from src.integrations.mcp.base_client import MCPRequest, MCPResponse
from src.core.api_rate_limiter import APIRateLimiter
from src.core.circuit_breaker import CircuitBreaker


class TestAuthProviderMCPClient:
    """Test suite for Auth Provider MCP client"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter"""
        return APIRateLimiter()
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker"""
        return CircuitBreaker("auth_provider")
    
    @pytest.fixture
    def client(self, rate_limiter, circuit_breaker):
        """Create Auth Provider MCP client"""
        return AuthProviderMCPClient(
            server_url="http://localhost:8013",
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    @pytest.mark.asyncio
    async def test_authenticate_basic(self, client):
        """Test: Basic authentication"""
        mock_response = {
            "result": {
                "token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIs...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": "read write",
                    "issued_at": "2024-01-15T10:00:00Z"
                },
                "user": {
                    "id": "user123",
                    "username": "john.doe",
                    "email": "john.doe@example.com",
                    "roles": ["researcher", "admin"]
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.authenticate(
                username="john.doe",
                password="secure_password",
                method=AuthenticationMethod.BASIC
            )
        
        # Verify request
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert request.method == "authenticate"
        assert request.params["username"] == "john.doe"
        assert request.params["method"] == "basic"
        
        # Verify response
        assert isinstance(result.data, AuthToken)
        assert result.data.access_token.startswith("eyJ")
        assert result.data.user.username == "john.doe"
    
    @pytest.mark.asyncio
    async def test_authenticate_oauth2(self, client):
        """Test: OAuth2 authentication"""
        mock_response = {
            "result": {
                "authorization_url": "https://auth.example.com/oauth/authorize?client_id=app123&response_type=code",
                "state": "random_state_123"
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.initiate_oauth2(
                client_id="app123",
                redirect_uri="http://localhost:8000/callback",
                scopes=["read", "write", "admin"]
            )
        
        assert result.data["authorization_url"].startswith("https://auth.example.com")
        assert result.data["state"] == "random_state_123"
    
    @pytest.mark.asyncio
    async def test_verify_token(self, client):
        """Test: Verify access token"""
        mock_response = {
            "result": {
                "valid": True,
                "user": {
                    "id": "user123",
                    "username": "john.doe",
                    "email": "john.doe@example.com",
                    "roles": ["researcher"]
                },
                "expires_at": "2024-01-15T11:00:00Z",
                "scopes": ["read", "write"]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.verify_token("eyJhbGciOiJIUzI1NiIs...")
        
        assert result.data["valid"] is True
        assert result.data["user"]["username"] == "john.doe"
        assert "read" in result.data["scopes"]
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client):
        """Test: Refresh access token"""
        mock_response = {
            "result": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...NEW",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.refresh_token("refresh_token_123")
        
        assert result.data["access_token"].endswith("NEW")
        assert result.data["expires_in"] == 3600
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self, client):
        """Test: Get user profile"""
        mock_response = {
            "result": {
                "user": {
                    "id": "user123",
                    "username": "john.doe",
                    "email": "john.doe@example.com",
                    "full_name": "John Doe",
                    "created_at": "2023-01-01T00:00:00Z",
                    "last_login": "2024-01-15T10:00:00Z",
                    "roles": ["researcher", "admin"],
                    "permissions": ["read:documents", "write:documents", "admin:users"],
                    "metadata": {
                        "department": "Research",
                        "institution": "Example University"
                    }
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_user_profile("user123")
        
        assert isinstance(result.data, User)
        assert result.data.username == "john.doe"
        assert len(result.data.roles) == 2
        assert "read:documents" in result.data.permissions
    
    @pytest.mark.asyncio
    async def test_check_permission(self, client):
        """Test: Check user permission"""
        mock_response = {
            "result": {
                "allowed": True,
                "reason": "User has admin role",
                "matched_rules": [
                    {"rule": "admin:*", "source": "role:admin"}
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.check_permission(
                user_id="user123",
                resource="documents",
                action="delete"
            )
        
        assert result.data["allowed"] is True
        assert "admin role" in result.data["reason"]
    
    @pytest.mark.asyncio
    async def test_list_roles(self, client):
        """Test: List available roles"""
        mock_response = {
            "result": {
                "roles": [
                    {
                        "id": "role1",
                        "name": "researcher",
                        "description": "Can read and analyze documents",
                        "permissions": ["read:documents", "analyze:documents"]
                    },
                    {
                        "id": "role2",
                        "name": "admin",
                        "description": "Full system access",
                        "permissions": ["admin:*"]
                    }
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.list_roles()
        
        assert len(result.data) == 2
        assert isinstance(result.data[0], Role)
        assert result.data[0].name == "researcher"
        assert result.data[1].permissions == ["admin:*"]
    
    @pytest.mark.asyncio
    async def test_create_api_key(self, client):
        """Test: Create API key"""
        mock_response = {
            "result": {
                "api_key": "kgas_prod_abcd1234efgh5678",
                "key_id": "key123",
                "created_at": "2024-01-15T10:00:00Z",
                "expires_at": "2025-01-15T10:00:00Z",
                "scopes": ["read:documents", "write:analytics"]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.create_api_key(
                name="Production API Key",
                scopes=["read:documents", "write:analytics"],
                expires_in_days=365
            )
        
        assert result.data["api_key"].startswith("kgas_prod_")
        assert len(result.data["scopes"]) == 2
    
    @pytest.mark.asyncio
    async def test_revoke_api_key(self, client):
        """Test: Revoke API key"""
        mock_response = {
            "result": {
                "revoked": True,
                "key_id": "key123",
                "revoked_at": "2024-01-15T11:00:00Z"
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.revoke_api_key("key123")
        
        assert result.data["revoked"] is True
        assert result.data["key_id"] == "key123"
    
    @pytest.mark.asyncio
    async def test_authenticate_saml(self, client):
        """Test: SAML authentication"""
        mock_response = {
            "result": {
                "saml_request": "<samlp:AuthnRequest...",
                "idp_url": "https://idp.example.com/sso",
                "relay_state": "state123"
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.initiate_saml(
                idp_name="university_sso"
            )
        
        assert result.data["saml_request"].startswith("<samlp:")
        assert "idp.example.com" in result.data["idp_url"]
    
    @pytest.mark.asyncio
    async def test_multi_factor_auth(self, client):
        """Test: Multi-factor authentication"""
        mock_response = {
            "result": {
                "mfa_required": True,
                "challenge_id": "mfa123",
                "methods": ["totp", "sms", "email"]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.initiate_mfa(
                user_id="user123",
                method="totp"
            )
        
        assert result.data["mfa_required"] is True
        assert "totp" in result.data["methods"]
    
    @pytest.mark.asyncio
    async def test_audit_log(self, client):
        """Test: Get authentication audit log"""
        mock_response = {
            "result": {
                "events": [
                    {
                        "event_id": "evt1",
                        "timestamp": "2024-01-15T10:00:00Z",
                        "event_type": "login_success",
                        "user_id": "user123",
                        "ip_address": "192.168.1.100",
                        "user_agent": "Mozilla/5.0..."
                    },
                    {
                        "event_id": "evt2",
                        "timestamp": "2024-01-15T09:55:00Z",
                        "event_type": "login_failed",
                        "user_id": "user123",
                        "ip_address": "192.168.1.100",
                        "reason": "invalid_password"
                    }
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_audit_log(
                user_id="user123",
                event_types=["login_success", "login_failed"],
                limit=10
            )
        
        assert len(result.data) == 2
        assert result.data[0]["event_type"] == "login_success"
        assert result.data[1]["reason"] == "invalid_password"
    
    @pytest.mark.asyncio
    async def test_session_management(self, client):
        """Test: Active session management"""
        mock_response = {
            "result": {
                "sessions": [
                    {
                        "session_id": "sess1",
                        "created_at": "2024-01-15T10:00:00Z",
                        "last_active": "2024-01-15T10:30:00Z",
                        "ip_address": "192.168.1.100",
                        "device": "Chrome on Windows"
                    }
                ],
                "total": 1
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_active_sessions("user123")
        
        assert result.data["total"] == 1
        assert result.data["sessions"][0]["session_id"] == "sess1"