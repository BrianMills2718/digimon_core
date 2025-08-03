"""Security Validation Framework

Validates security configurations, checks for hardcoded credentials,
and ensures proper environment variable usage across the codebase.
"""

import os
import re
import ast
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from .logging_config import get_logger

logger = get_logger("core.security_validation")


@dataclass
class SecurityIssue:
    """Represents a security issue found during validation"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    recommendation: str


class SecurityValidator:
    """Validates security configurations and identifies potential issues"""
    
    def __init__(self):
        self.logger = get_logger("core.security_validation")
        self.issues: List[SecurityIssue] = []
        
        # Patterns to detect hardcoded credentials
        self.credential_patterns = {
            'password': [
                r'password\s*=\s*["\'][^"\']{3,}["\']',
                r'PASSWORD\s*=\s*["\'][^"\']{3,}["\']',
                r'pwd\s*=\s*["\'][^"\']{3,}["\']'
            ],
            'api_key': [
                r'api_key\s*=\s*["\'][a-zA-Z0-9]{10,}["\']',
                r'API_KEY\s*=\s*["\'][a-zA-Z0-9]{10,}["\']',
                r'apikey\s*=\s*["\'][a-zA-Z0-9]{10,}["\']'
            ],
            'secret': [
                r'secret\s*=\s*["\'][^"\']{8,}["\']',
                r'SECRET\s*=\s*["\'][^"\']{8,}["\']',
                r'token\s*=\s*["\'][a-zA-Z0-9]{10,}["\']'
            ],
            'database_url': [
                r'database_url\s*=\s*["\'][^"\']*://[^"\']*["\']',
                r'DATABASE_URL\s*=\s*["\'][^"\']*://[^"\']*["\']'
            ]
        }
        
        # Test/default credentials that should never be in production
        self.test_credentials = {
            'testpassword', 'password', 'admin', '123456', 'test',
            'default', 'changeme', 'secret', 'password123'
        }
        
        # Required environment variables
        self.required_env_vars = {
            'NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD',
            'OPENAI_API_KEY', 'GOOGLE_API_KEY'
        }
        
    def validate_codebase(self, root_path: str) -> List[SecurityIssue]:
        """Validate entire codebase for security issues
        
        Args:
            root_path: Root directory to scan
            
        Returns:
            List of security issues found
        """
        self.issues.clear()
        root = Path(root_path)
        
        # Scan Python files
        for py_file in root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            self._validate_python_file(py_file)
            
        # Scan configuration files
        for config_file in root.rglob("*.json"):
            if self._should_skip_file(config_file):
                continue
            self._validate_json_file(config_file)
            
        for config_file in root.rglob("*.yaml"):
            if self._should_skip_file(config_file):
                continue
            self._validate_yaml_file(config_file)
            
        for config_file in root.rglob("*.yml"):
            if self._should_skip_file(config_file):
                continue
            self._validate_yaml_file(config_file)
            
        # Validate environment configuration
        self._validate_environment_variables()
        
        self.logger.info(f"Security validation complete: {len(self.issues)} issues found")
        return self.issues
    
    def scan_file(self, file_path: str) -> List[SecurityIssue]:
        """Scan a single file for security issues
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of security issues found in the file
        """
        file_issues = []
        path = Path(file_path)
        
        if not path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return []
            
        # Store current issues to isolate file-specific issues
        original_issues = self.issues.copy()
        self.issues.clear()
        
        try:
            if path.suffix == '.py':
                self._validate_python_file(path)
            elif path.suffix in ['.json']:
                self._validate_json_file(path)
            elif path.suffix in ['.yaml', '.yml']:
                self._validate_yaml_file(path)
            else:
                # For other file types, try basic credential scanning
                self._validate_python_file(path)  # Use Python logic as fallback
                
            file_issues = self.issues.copy()
            
        except Exception as e:
            self.logger.error(f"Error scanning file {file_path}: {e}")
        finally:
            # Restore original issues
            self.issues = original_issues
            
        return file_issues
    
    def scan_directory(self, directory_path: str, file_extensions: List[str] = None) -> List[SecurityIssue]:
        """Scan directory for security issues
        
        Args:
            directory_path: Path to directory to scan
            file_extensions: Optional list of file extensions to include (e.g., ['.py'])
            
        Returns:
            List of security issues found in the directory
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            self.logger.warning(f"Directory not found: {directory_path}")
            return []
            
        directory_issues = []
        
        # If no extensions specified, use default extensions
        if file_extensions is None:
            file_extensions = ['.py', '.json', '.yaml', '.yml']
            
        # Scan all files with specified extensions
        for ext in file_extensions:
            for file_path in dir_path.rglob(f"*{ext}"):
                if not self._should_skip_file(file_path):
                    file_issues = self.scan_file(str(file_path))
                    directory_issues.extend(file_issues)
                    
        return directory_issues
    
    def calculate_security_score(self, issues: List[SecurityIssue], total_files: int = 1) -> float:
        """Calculate security score based on issues found
        
        Args:
            issues: List of security issues
            total_files: Total number of files scanned
            
        Returns:
            Security score (0-100, higher is better)
        """
        if not issues:
            return 100.0
            
        # Weight by severity
        severity_weights = {
            'critical': 10,
            'high': 5,
            'medium': 2,
            'low': 1
        }
        
        total_weight = sum(severity_weights.get(issue.severity, 1) for issue in issues)
        
        # Normalize by total files and apply score calculation
        # Base score starts at 100 and decreases based on issues
        base_score = 100.0
        penalty_per_file = total_weight / max(total_files, 1)
        
        # Apply penalty with diminishing returns
        score = base_score - min(penalty_per_file * 5, 95)  # Cap at 5% minimum score
        
        return max(score, 0.0)
    
    def get_security_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """Get security recommendations based on issues found
        
        Args:
            issues: List of security issues
            
        Returns:
            List of security recommendations
        """
        recommendations = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)
            
        # Generate recommendations based on issue types
        if 'password' in issue_types or 'api_key' in issue_types or 'secret' in issue_types:
            recommendations.append("Replace hardcoded credentials with environment variables")
            recommendations.append("Use a secure credential management system")
            
        if 'sql_injection' in issue_types:
            recommendations.append("Use parameterized queries to prevent SQL injection")
            recommendations.append("Validate and sanitize all user inputs")
            
        if 'insecure_import' in issue_types:
            recommendations.append("Review and update insecure library imports")
            recommendations.append("Use security-focused linting tools")
            
        # Add general recommendations based on severity
        critical_issues = [i for i in issues if i.severity == 'critical']
        if critical_issues:
            recommendations.append("Address critical security issues immediately")
            
        high_issues = [i for i in issues if i.severity == 'high']
        if high_issues:
            recommendations.append("Prioritize resolution of high-severity security issues")
            
        if not recommendations:
            recommendations.append("Security review complete - no major issues found")
            
        return recommendations
    
    def validate_environment_config(self, config: Dict[str, Any]) -> List[SecurityIssue]:
        """Validate environment configuration for security issues
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of security issues found in the configuration
        """
        config_issues = []
        
        def check_nested_config(data, path=""):
            """Recursively check nested configuration"""
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    check_nested_config(value, current_path)
            elif isinstance(data, str):
                # Check if this looks like a hardcoded credential
                for cred_type, patterns in self.credential_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, data, re.IGNORECASE):
                            # Check if it's an environment variable reference
                            if not (data.startswith('${') and data.endswith('}')):
                                config_issues.append(SecurityIssue(
                                    file_path="config",
                                    line_number=0,
                                    issue_type=cred_type,
                                    severity="high",
                                    description=f"Hardcoded {cred_type} in configuration at {path}",
                                    recommendation=f"Replace with environment variable reference like ${{{key.upper()}}}"
                                ))
                                
        check_nested_config(config)
        return config_issues
    
    def generate_security_report(self, directory_path: str) -> Dict[str, Any]:
        """Generate comprehensive security report for a directory
        
        Args:
            directory_path: Path to directory to analyze
            
        Returns:
            Comprehensive security report dictionary
        """
        # Scan the directory
        issues = self.scan_directory(directory_path)
        
        # Count files scanned
        dir_path = Path(directory_path)
        total_files = 0
        if dir_path.exists():
            for ext in ['.py', '.json', '.yaml', '.yml']:
                total_files += len(list(dir_path.rglob(f"*{ext}")))
        
        # Group issues by severity
        issues_by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for issue in issues:
            issues_by_severity[issue.severity].append(issue)
        
        # Calculate security score
        security_score = self.calculate_security_score(issues, total_files)
        
        # Get recommendations
        recommendations = self.get_security_recommendations(issues)
        
        return {
            'total_files': total_files,
            'total_issues': len(issues),
            'security_score': security_score,
            'issues_by_severity': {
                severity: len(issue_list) 
                for severity, issue_list in issues_by_severity.items()
            },
            'issues': issues,
            'recommendations': recommendations,
            'timestamp': Path(directory_path).stat().st_mtime if Path(directory_path).exists() else 0
        }
        
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during validation"""
        skip_patterns = {
            '__pycache__', '.git', '.pytest_cache', 'node_modules',
            '.venv', 'venv', '.env', 'test_', '_test.py',
            'backup', '.bak'
        }
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
        
    def _validate_python_file(self, file_path: Path):
        """Validate a Python file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for hardcoded credentials
                self._check_hardcoded_credentials(file_path, line_num, line)
                
                # Check for test credentials
                self._check_test_credentials(file_path, line_num, line)
                
                # Check for SQL injection vulnerabilities
                self._check_sql_injection(file_path, line_num, line)
                
                # Check for insecure imports
                self._check_insecure_imports(file_path, line_num, line)
                
        except Exception as e:
            self.logger.warning(f"Error validating file {file_path}: {e}")
            
    def _check_hardcoded_credentials(self, file_path: Path, line_num: int, line: str):
        """Check for hardcoded credentials in a line"""
        for cred_type, patterns in self.credential_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip if it's using environment variables
                    if 'os.getenv' in line or 'os.environ' in line:
                        continue
                        
                    # Skip if it's a comment
                    if line.strip().startswith('#'):
                        continue
                        
                    self.issues.append(SecurityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type='hardcoded_credential',
                        severity='critical',
                        description=f'Hardcoded {cred_type} detected',
                        recommendation=f'Replace with environment variable using os.getenv()'
                    ))
                    
    def _check_test_credentials(self, file_path: Path, line_num: int, line: str):
        """Check for test credentials that might be left in production code"""
        for test_cred in self.test_credentials:
            if f'"{test_cred}"' in line.lower() or f"'{test_cred}'" in line.lower():
                # Skip if it's in a comment or test file
                if line.strip().startswith('#') or 'test' in str(file_path).lower():
                    continue
                    
                self.issues.append(SecurityIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='test_credential',
                    severity='high',
                    description=f'Test credential "{test_cred}" found in production code',
                    recommendation='Remove test credentials and use proper configuration'
                ))
                
    def _check_sql_injection(self, file_path: Path, line_num: int, line: str):
        """Check for potential SQL injection vulnerabilities"""
        sql_patterns = [
            r'session\.run\s*\(\s*f["\']',  # f-string in Neo4j queries
            r'execute\s*\(\s*f["\']',       # f-string in SQL
            r'query\s*\(\s*f["\']',         # f-string in queries
            r'session\.run\s*\(\s*["\'][^"\']*\+',  # String concatenation
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, line):
                self.issues.append(SecurityIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='sql_injection',
                    severity='high',
                    description='Potential SQL injection vulnerability detected',
                    recommendation='Use parameterized queries instead of string formatting'
                ))
                
    def _check_insecure_imports(self, file_path: Path, line_num: int, line: str):
        """Check for insecure imports"""
        insecure_imports = [
            'pickle',  # Unsafe deserialization
            'eval',    # Code injection
            'exec',    # Code injection
        ]
        
        for insecure in insecure_imports:
            if f'import {insecure}' in line or f'from {insecure}' in line:
                self.issues.append(SecurityIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type='insecure_import',
                    severity='medium',
                    description=f'Potentially insecure import: {insecure}',
                    recommendation=f'Consider safer alternatives to {insecure}'
                ))
                
    def _validate_json_file(self, file_path: Path):
        """Validate JSON configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self._check_config_credentials(file_path, data)
            
        except Exception as e:
            self.logger.warning(f"Error validating JSON file {file_path}: {e}")
            
    def _validate_yaml_file(self, file_path: Path):
        """Validate YAML configuration file"""
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if data:
                self._check_config_credentials(file_path, data)
                
        except ImportError:
            self.logger.warning("PyYAML not available, skipping YAML validation")
        except Exception as e:
            self.logger.warning(f"Error validating YAML file {file_path}: {e}")
            
    def _check_config_credentials(self, file_path: Path, data: Any):
        """Check configuration data for hardcoded credentials"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    key_lower = key.lower()
                    if any(cred in key_lower for cred in ['password', 'secret', 'key', 'token']):
                        if value and not value.startswith('${') and value not in ['', 'null', 'None']:
                            self.issues.append(SecurityIssue(
                                file_path=str(file_path),
                                line_number=0,
                                issue_type='config_credential',
                                severity='critical',
                                description=f'Hardcoded credential in config: {key}',
                                recommendation='Use environment variables or secure configuration management'
                            ))
                elif isinstance(value, (dict, list)):
                    self._check_config_credentials(file_path, value)
        elif isinstance(data, list):
            for item in data:
                self._check_config_credentials(file_path, item)
                
    def _validate_environment_variables(self):
        """Validate required environment variables are set"""
        missing_vars = []
        
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            self.issues.append(SecurityIssue(
                file_path='environment',
                line_number=0,
                issue_type='missing_env_var',
                severity='high',
                description=f'Missing required environment variables: {", ".join(missing_vars)}',
                recommendation='Set all required environment variables for secure operation'
            ))
            
    def get_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report
        
        Returns:
            Dictionary with security validation results
        """
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        issue_types = {}
        
        for issue in self.issues:
            severity_counts[issue.severity] += 1
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = 0
            issue_types[issue.issue_type] += 1
            
        return {
            'total_issues': len(self.issues),
            'severity_breakdown': severity_counts,
            'issue_types': issue_types,
            'critical_files': [issue.file_path for issue in self.issues if issue.severity == 'critical'],
            'recommendations': self._get_top_recommendations(),
            'security_score': self._calculate_security_score()
        }
        
    def _get_top_recommendations(self) -> List[str]:
        """Get top security recommendations"""
        recommendations = set()
        for issue in self.issues:
            if issue.severity in ['critical', 'high']:
                recommendations.add(issue.recommendation)
        return list(recommendations)[:5]  # Top 5 recommendations
        
    def _calculate_security_score(self) -> float:
        """Calculate overall security score (0-100)"""
        if not self.issues:
            return 100.0
            
        # Weight issues by severity
        weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
        total_weight = sum(weights[issue.severity] for issue in self.issues)
        
        # Calculate score (lower is better, so invert)
        max_possible_weight = len(self.issues) * weights['critical']
        score = max(0, 100 - (total_weight / max_possible_weight * 100))
        
        return round(score, 2)
        
    def fix_hardcoded_credentials(self, dry_run: bool = True) -> List[str]:
        """Automatically fix hardcoded credentials by replacing with environment variables
        
        Args:
            dry_run: If True, only return what would be changed without making changes
            
        Returns:
            List of changes that were made or would be made
        """
        changes = []
        
        for issue in self.issues:
            if issue.issue_type == 'hardcoded_credential':
                try:
                    changes.extend(self._fix_credential_in_file(issue, dry_run))
                except Exception as e:
                    self.logger.error(f"Error fixing {issue.file_path}: {e}")
                    
        return changes
        
    def _fix_credential_in_file(self, issue: SecurityIssue, dry_run: bool) -> List[str]:
        """Fix a specific credential issue in a file"""
        changes = []
        
        try:
            with open(issue.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            original_line = lines[issue.line_number - 1]
            
            # Generate environment variable name
            env_var = self._generate_env_var_name(original_line)
            
            # Replace hardcoded value with environment variable
            new_line = self._replace_with_env_var(original_line, env_var)
            
            if new_line != original_line:
                change_desc = f"{issue.file_path}:{issue.line_number}: {original_line.strip()} -> {new_line.strip()}"
                changes.append(change_desc)
                
                if not dry_run:
                    lines[issue.line_number - 1] = new_line
                    with open(issue.file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                        
        except Exception as e:
            self.logger.error(f"Error processing {issue.file_path}: {e}")
            
        return changes
        
    def _generate_env_var_name(self, line: str) -> str:
        """Generate appropriate environment variable name from code line"""
        # Extract variable name from assignment
        if '=' in line:
            var_name = line.split('=')[0].strip()
            # Convert to uppercase environment variable format
            env_var = var_name.upper().replace('.', '_').replace('[', '').replace(']', '').replace('"', '').replace("'", '')
            return f"KGAS_{env_var}" if not env_var.startswith('KGAS_') else env_var
        return "KGAS_SECRET"
        
    def _replace_with_env_var(self, line: str, env_var: str) -> str:
        """Replace hardcoded value with environment variable call"""
        # Find the quoted string and replace it
        import re
        
        # Pattern to match quoted strings
        pattern = r'(["\'])[^"\']*\1'
        
        def replace_func(match):
            quote = match.group(1)
            return f'os.getenv({quote}{env_var}{quote})'
            
        new_line = re.sub(pattern, replace_func, line, count=1)
        
        # Add import if needed
        if 'os.getenv' in new_line and 'import os' not in new_line:
            # This is a simple replacement - in practice, we'd need to handle imports more carefully
            pass
            
        return new_line


def validate_security(root_path: str = None) -> Dict[str, Any]:
    """Validate security configuration for the entire codebase
    
    Args:
        root_path: Root directory to scan (defaults to current directory)
        
    Returns:
        Security validation report
    """
    if root_path is None:
        root_path = os.getcwd()
        
    validator = SecurityValidator()
    issues = validator.validate_codebase(root_path)
    
    return {
        'issues': [
            {
                'file': issue.file_path,
                'line': issue.line_number,
                'type': issue.issue_type,
                'severity': issue.severity,
                'description': issue.description,
                'recommendation': issue.recommendation
            }
            for issue in issues
        ],
        'report': validator.get_security_report()
    }