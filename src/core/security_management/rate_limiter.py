"""
Rate Limiter

Handles rate limiting and IP blocking for abuse prevention.
"""

import time
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta

from .security_types import SecurityConfig, SecurityEvent, AuditAction, RateLimitExceededError
from .audit_logger import AuditLogger


class RateLimiter:
    """Manages rate limiting and IP blocking for abuse prevention."""
    
    def __init__(self, config: SecurityConfig, audit_logger: AuditLogger):
        self.config = config
        self.audit_logger = audit_logger
        self.rate_limits: Dict[str, List[float]] = {}
        self.blocked_ips: Set[str] = set()
        self.ip_block_timestamps: Dict[str, datetime] = {}
        self.logger = logging.getLogger(__name__)
    
    def check_rate_limit(self, identifier: str, 
                        requests_per_window: Optional[int] = None,
                        window_size: Optional[int] = None) -> bool:
        """
        Check rate limiting for identifier.
        
        Args:
            identifier: Rate limit identifier (IP, user ID, etc.)
            requests_per_window: Requests per time window
            window_size: Time window in seconds
            
        Returns:
            True if request allowed, False if rate limited
        """
        requests_per_window = requests_per_window or self.config.get('rate_limit_requests')
        window_size = window_size or self.config.get('rate_limit_window')
        
        current_time = time.time()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Clean old requests outside window
        self.rate_limits[identifier] = [
            req_time for req_time in self.rate_limits[identifier]
            if current_time - req_time < window_size
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[identifier]) >= requests_per_window:
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="rate_limit",
                timestamp=datetime.now(),
                ip_address=identifier if self._is_ip_address(identifier) else None,
                details={
                    'identifier': identifier,
                    'reason': 'rate_limit_exceeded',
                    'current_requests': len(self.rate_limits[identifier]),
                    'limit': requests_per_window
                },
                risk_level="medium"
            ))
            return False
        
        # Add current request
        self.rate_limits[identifier].append(current_time)
        return True
    
    def block_ip(self, ip_address: str, duration_hours: int = 24, reason: str = "manual_block") -> bool:
        """
        Block IP address for specified duration.
        
        Args:
            ip_address: IP address to block
            duration_hours: Block duration in hours
            reason: Reason for blocking
            
        Returns:
            True if IP was blocked
        """
        if not self._is_ip_address(ip_address):
            self.logger.warning(f"Invalid IP address format: {ip_address}")
            return False
        
        self.blocked_ips.add(ip_address)
        self.ip_block_timestamps[ip_address] = datetime.now()
        
        self.audit_logger.log_event(SecurityEvent(
            action=AuditAction.SECURITY_VIOLATION,
            user_id=None,
            resource="ip_blocking",
            timestamp=datetime.now(),
            ip_address=ip_address,
            details={
                'action': 'ip_blocked',
                'reason': reason,
                'duration_hours': duration_hours
            },
            risk_level="high"
        ))
        
        self.logger.warning(f"IP address blocked: {ip_address} for {duration_hours} hours. Reason: {reason}")
        return True
    
    def unblock_ip(self, ip_address: str, reason: str = "manual_unblock") -> bool:
        """
        Unblock IP address.
        
        Args:
            ip_address: IP address to unblock
            reason: Reason for unblocking
            
        Returns:
            True if IP was unblocked
        """
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            if ip_address in self.ip_block_timestamps:
                del self.ip_block_timestamps[ip_address]
            
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.DATA_MODIFICATION,
                user_id=None,
                resource="ip_blocking",
                timestamp=datetime.now(),
                ip_address=ip_address,
                details={
                    'action': 'ip_unblocked',
                    'reason': reason
                },
                risk_level="low"
            ))
            
            self.logger.info(f"IP address unblocked: {ip_address}. Reason: {reason}")
            return True
        
        return False
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """
        Check if IP address is blocked.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            True if IP is blocked
        """
        if ip_address in self.blocked_ips:
            # Log access attempt from blocked IP
            self.audit_logger.log_event(SecurityEvent(
                action=AuditAction.ACCESS_DENIED,
                user_id=None,
                resource="ip_blocking",
                timestamp=datetime.now(),
                ip_address=ip_address,
                details={'reason': 'ip_blocked_access_attempt'},
                risk_level="high"
            ))
            return True
        
        return False
    
    def auto_block_suspicious_ip(self, ip_address: str, violation_count: int = 1) -> bool:
        """
        Automatically block IP based on suspicious activity.
        
        Args:
            ip_address: IP address to potentially block
            violation_count: Number of violations to add
            
        Returns:
            True if IP was blocked
        """
        if not self._is_ip_address(ip_address):
            return False
        
        # Track violations for this IP
        violation_key = f"violations_{ip_address}"
        if violation_key not in self.rate_limits:
            self.rate_limits[violation_key] = []
        
        # Add violation timestamps
        current_time = time.time()
        for _ in range(violation_count):
            self.rate_limits[violation_key].append(current_time)
        
        # Clean old violations (1 hour window)
        violation_window = 3600  # 1 hour
        self.rate_limits[violation_key] = [
            v_time for v_time in self.rate_limits[violation_key]
            if current_time - v_time < violation_window
        ]
        
        # Auto-block if too many violations
        violation_threshold = 10  # Block after 10 violations in 1 hour
        if len(self.rate_limits[violation_key]) >= violation_threshold:
            return self.block_ip(ip_address, 24, "auto_block_suspicious_activity")
        
        return False
    
    def get_rate_limit_status(self, identifier: str) -> Dict[str, Any]:
        """
        Get rate limit status for identifier.
        
        Args:
            identifier: Rate limit identifier
            
        Returns:
            Rate limit status information
        """
        current_time = time.time()
        window_size = self.config.get('rate_limit_window')
        max_requests = self.config.get('rate_limit_requests')
        
        if identifier not in self.rate_limits:
            return {
                'identifier': identifier,
                'current_requests': 0,
                'max_requests': max_requests,
                'window_size_seconds': window_size,
                'requests_remaining': max_requests,
                'reset_time': None,
                'is_blocked': self.is_ip_blocked(identifier) if self._is_ip_address(identifier) else False
            }
        
        # Clean old requests
        recent_requests = [
            req_time for req_time in self.rate_limits[identifier]
            if current_time - req_time < window_size
        ]
        
        # Calculate reset time (when oldest request expires)
        reset_time = None
        if recent_requests:
            oldest_request = min(recent_requests)
            reset_time = datetime.fromtimestamp(oldest_request + window_size).isoformat()
        
        return {
            'identifier': identifier,
            'current_requests': len(recent_requests),
            'max_requests': max_requests,
            'window_size_seconds': window_size,
            'requests_remaining': max(0, max_requests - len(recent_requests)),
            'reset_time': reset_time,
            'is_blocked': self.is_ip_blocked(identifier) if self._is_ip_address(identifier) else False
        }
    
    def cleanup_expired_blocks(self) -> int:
        """
        Clean up expired IP blocks.
        
        Returns:
            Number of blocks removed
        """
        current_time = datetime.now()
        expired_ips = []
        
        # Default block duration (24 hours)
        default_duration = timedelta(hours=24)
        
        for ip_address, block_time in self.ip_block_timestamps.items():
            if current_time - block_time > default_duration:
                expired_ips.append(ip_address)
        
        # Remove expired blocks
        for ip_address in expired_ips:
            self.unblock_ip(ip_address, "automatic_expiration")
        
        return len(expired_ips)
    
    def get_blocked_ips_info(self) -> List[Dict[str, Any]]:
        """
        Get information about blocked IP addresses.
        
        Returns:
            List of blocked IP information
        """
        blocked_info = []
        current_time = datetime.now()
        
        for ip_address in self.blocked_ips:
            block_time = self.ip_block_timestamps.get(ip_address)
            info = {
                'ip_address': ip_address,
                'blocked_at': block_time.isoformat() if block_time else None,
                'blocked_duration': str(current_time - block_time) if block_time else None
            }
            blocked_info.append(info)
        
        return sorted(blocked_info, key=lambda x: x['blocked_at'] or '', reverse=True)
    
    def enforce_rate_limit(self, identifier: str, 
                          requests_per_window: Optional[int] = None) -> None:
        """
        Enforce rate limit and raise exception if exceeded.
        
        Args:
            identifier: Rate limit identifier
            requests_per_window: Requests per time window
            
        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        if not self.check_rate_limit(identifier, requests_per_window):
            status = self.get_rate_limit_status(identifier)
            raise RateLimitExceededError(
                f"Rate limit exceeded for {identifier}. "
                f"Current: {status['current_requests']}, "
                f"Max: {status['max_requests']}, "
                f"Reset: {status['reset_time']}"
            )
    
    def get_rate_limit_statistics(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        current_time = time.time()
        window_size = self.config.get('rate_limit_window')
        
        # Count active rate limits
        active_identifiers = 0
        total_recent_requests = 0
        
        for identifier, timestamps in self.rate_limits.items():
            if identifier.startswith('violations_'):
                continue  # Skip violation counters
            
            recent_requests = [t for t in timestamps if current_time - t < window_size]
            if recent_requests:
                active_identifiers += 1
                total_recent_requests += len(recent_requests)
        
        return {
            'active_identifiers': active_identifiers,
            'total_recent_requests': total_recent_requests,
            'blocked_ips': len(self.blocked_ips),
            'rate_limit_window_seconds': window_size,
            'max_requests_per_window': self.config.get('rate_limit_requests')
        }
    
    def _is_ip_address(self, identifier: str) -> bool:
        """Check if identifier appears to be an IP address."""
        import re
        # Simple IPv4 pattern
        ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        # Simple IPv6 pattern (basic)
        ipv6_pattern = r'^[0-9a-fA-F:]+$'
        
        return bool(re.match(ipv4_pattern, identifier) or re.match(ipv6_pattern, identifier))