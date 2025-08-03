"""
Audit Logger

Handles security event logging, audit trails, and security reporting.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .security_types import SecurityEvent, AuditAction, SecurityConfig


class AuditLogger:
    """Manages security audit logging and reporting."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.security_events: List[SecurityEvent] = []
        self.logger = logging.getLogger(__name__)
    
    def log_event(self, event: SecurityEvent) -> None:
        """
        Log security event for audit trail.
        
        Args:
            event: Security event to log
        """
        self.security_events.append(event)
        
        # Log to application logger with appropriate level
        log_level = self._get_log_level(event.risk_level)
        self.logger.log(
            log_level,
            f"Security Event: {event.action.value} - User: {event.user_id} - "
            f"Resource: {event.resource} - Risk: {event.risk_level}"
        )
        
        # Clean old events periodically
        self._cleanup_old_events()
    
    def get_events_by_user(self, user_id: str, limit: int = 100) -> List[SecurityEvent]:
        """Get security events for specific user."""
        user_events = [e for e in self.security_events if e.user_id == user_id]
        return sorted(user_events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_events_by_action(self, action: AuditAction, limit: int = 100) -> List[SecurityEvent]:
        """Get security events by action type."""
        action_events = [e for e in self.security_events if e.action == action]
        return sorted(action_events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_events_by_risk_level(self, risk_level: str, limit: int = 100) -> List[SecurityEvent]:
        """Get security events by risk level."""
        risk_events = [e for e in self.security_events if e.risk_level == risk_level]
        return sorted(risk_events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_events_by_ip(self, ip_address: str, limit: int = 100) -> List[SecurityEvent]:
        """Get security events by IP address."""
        ip_events = [e for e in self.security_events 
                    if e.ip_address and e.ip_address == ip_address]
        return sorted(ip_events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_recent_events(self, hours: int = 24, limit: int = 100) -> List[SecurityEvent]:
        """Get recent security events."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in self.security_events if e.timestamp > cutoff_time]
        return sorted(recent_events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_failed_login_attempts(self, hours: int = 24) -> List[SecurityEvent]:
        """Get failed login attempts in the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        failed_logins = [
            e for e in self.security_events
            if (e.action == AuditAction.ACCESS_DENIED and 
                e.resource == "authentication" and
                e.timestamp > cutoff_time)
        ]
        return sorted(failed_logins, key=lambda x: x.timestamp, reverse=True)
    
    def get_security_violations(self, hours: int = 24) -> List[SecurityEvent]:
        """Get security violations in the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        violations = [
            e for e in self.security_events
            if (e.action == AuditAction.SECURITY_VIOLATION and
                e.timestamp > cutoff_time)
        ]
        return sorted(violations, key=lambda x: x.timestamp, reverse=True)
    
    def get_suspicious_activity(self, hours: int = 24) -> List[SecurityEvent]:
        """Get suspicious activity events."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        suspicious_events = [
            e for e in self.security_events
            if (e.risk_level in ["high", "critical"] and
                e.timestamp > cutoff_time)
        ]
        return sorted(suspicious_events, key=lambda x: x.timestamp, reverse=True)
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive security report.
        
        Args:
            hours: Time period for the report in hours
            
        Returns:
            Security report with statistics and recommendations
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        period_events = [e for e in self.security_events if e.timestamp > cutoff_time]
        
        if not period_events:
            return {
                'report_period_hours': hours,
                'total_events': 0,
                'event_breakdown': {},
                'security_recommendations': [],
                'generated_at': datetime.now().isoformat()
            }
        
        # Event breakdown by action
        event_breakdown = {}
        for event in period_events:
            action = event.action.value
            event_breakdown[action] = event_breakdown.get(action, 0) + 1
        
        # Risk level breakdown
        risk_breakdown = {}
        for event in period_events:
            risk = event.risk_level
            risk_breakdown[risk] = risk_breakdown.get(risk, 0) + 1
        
        # IP address analysis
        ip_breakdown = {}
        for event in period_events:
            if event.ip_address:
                ip_breakdown[event.ip_address] = ip_breakdown.get(event.ip_address, 0) + 1
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(period_events, event_breakdown, risk_breakdown)
        
        # Top suspicious IPs (more than 10 events)
        suspicious_ips = [ip for ip, count in ip_breakdown.items() if count > 10]
        
        # Authentication statistics
        failed_logins = len([e for e in period_events 
                           if e.action == AuditAction.ACCESS_DENIED and e.resource == "authentication"])
        successful_logins = len([e for e in period_events 
                               if e.action == AuditAction.LOGIN])
        
        return {
            'report_period_hours': hours,
            'total_events': len(period_events),
            'event_breakdown': event_breakdown,
            'risk_breakdown': risk_breakdown,
            'authentication_stats': {
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'success_rate': (successful_logins / (successful_logins + failed_logins) * 100) 
                               if (successful_logins + failed_logins) > 0 else 0
            },
            'suspicious_ips': suspicious_ips,
            'high_risk_events': len([e for e in period_events if e.risk_level == "high"]),
            'critical_events': len([e for e in period_events if e.risk_level == "critical"]),
            'security_recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_events_for_compliance(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Export events for compliance reporting."""
        compliance_events = []
        
        for event in self.security_events:
            if start_date <= event.timestamp <= end_date:
                compliance_event = {
                    'timestamp': event.timestamp.isoformat(),
                    'action': event.action.value,
                    'user_id': event.user_id,
                    'resource': event.resource,
                    'ip_address': event.ip_address,
                    'risk_level': event.risk_level,
                    'details': event.details
                }
                compliance_events.append(compliance_event)
        
        return sorted(compliance_events, key=lambda x: x['timestamp'])
    
    def _cleanup_old_events(self) -> None:
        """Clean up old events based on retention policy."""
        retention_days = self.config.get('audit_retention_days')
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Only clean up periodically to avoid performance impact
        if len(self.security_events) > 10000:  # Clean when we have many events
            old_count = len(self.security_events)
            self.security_events = [e for e in self.security_events if e.timestamp > cutoff_date]
            cleaned_count = old_count - len(self.security_events)
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old security events")
    
    def _get_log_level(self, risk_level: str) -> int:
        """Get appropriate logging level for risk level."""
        risk_to_level = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }
        return risk_to_level.get(risk_level, logging.INFO)
    
    def _generate_security_recommendations(self, events: List[SecurityEvent], 
                                         event_breakdown: Dict[str, int],
                                         risk_breakdown: Dict[str, int]) -> List[str]:
        """Generate security recommendations based on event analysis."""
        recommendations = []
        total_events = len(events)
        
        if total_events == 0:
            return recommendations
        
        # Check for high number of failed login attempts
        failed_logins = event_breakdown.get('access_denied', 0)
        if failed_logins > total_events * 0.2:  # More than 20% failed attempts
            recommendations.append("High number of failed login attempts detected - consider implementing additional authentication measures")
        
        # Check for security violations
        violations = event_breakdown.get('security_violation', 0)
        if violations > 0:
            recommendations.append(f"Security violations detected ({violations}) - investigate potential security breaches")
        
        # Check for high-risk events
        high_risk = risk_breakdown.get('high', 0)
        critical_risk = risk_breakdown.get('critical', 0)
        if high_risk + critical_risk > total_events * 0.1:  # More than 10% high/critical
            recommendations.append("High percentage of high-risk security events - review security policies")
        
        # Check for suspicious IP patterns
        ip_events = [e for e in events if e.ip_address]
        if ip_events:
            ip_counts = {}
            for event in ip_events:
                ip_counts[event.ip_address] = ip_counts.get(event.ip_address, 0) + 1
            
            # Find IPs with many events
            suspicious_ips = [ip for ip, count in ip_counts.items() if count > 20]
            if suspicious_ips:
                recommendations.append(f"Suspicious IP activity detected from {len(suspicious_ips)} addresses - consider IP blocking")
        
        # Check for account lockouts
        lockouts = len([e for e in events 
                       if e.details.get('reason') == 'account_locked_failed_attempts'])
        if lockouts > 0:
            recommendations.append(f"Account lockouts detected ({lockouts}) - monitor for brute force attacks")
        
        return recommendations
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit logging statistics."""
        total_events = len(self.security_events)
        
        if total_events == 0:
            return {
                'total_events': 0,
                'events_by_action': {},
                'events_by_risk': {},
                'retention_days': self.config.get('audit_retention_days')
            }
        
        # Count by action
        action_counts = {}
        for event in self.security_events:
            action = event.action.value
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Count by risk level
        risk_counts = {}
        for event in self.security_events:
            risk = event.risk_level
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_events = len([e for e in self.security_events if e.timestamp > recent_cutoff])
        
        return {
            'total_events': total_events,
            'recent_events_24h': recent_events,
            'events_by_action': action_counts,
            'events_by_risk': risk_counts,
            'retention_days': self.config.get('audit_retention_days'),
            'oldest_event': min(e.timestamp for e in self.security_events).isoformat() if self.security_events else None,
            'newest_event': max(e.timestamp for e in self.security_events).isoformat() if self.security_events else None
        }