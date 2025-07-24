#!/usr/bin/env python3
"""
Flexible configuration system for Gemini Code Review
Allows per-project configuration files
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, InitVar

@dataclass
class ReviewConfig:
    """Configuration for code review"""
    # Project info
    project_name: str = "Unknown Project"
    # New: support for multiple project paths. `project_path` is legacy.
    project_paths: List[str] = field(default_factory=lambda: ["."])
    
    # Review settings
    output_format: str = "xml"  # xml or markdown
    output_file: str = "gemini-review.md"
    keep_repomix: bool = False
    
    # Repomix options
    remove_empty_lines: bool = True  # Default for LLM review
    show_line_numbers: bool = False  # Optional for easier reference
    include_diffs: bool = False      # Optional for change review
    compress_code: bool = False      # Optional for large codebases
    token_count_encoding: str = "gemini-pro"  # Default for Gemini models
    
    # Include patterns for repomix (if specified, only these files are included)
    include_patterns: List[str] = field(default_factory=list)
    
    # Ignore patterns for repomix (applied after include patterns)
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "*.pyc", "__pycache__", ".git", ".venv", "venv", 
        "node_modules", "*.log", ".pytest_cache", "*.egg-info",
        "build", "dist", "gemini-review*.md", "repomix-output.*"
    ])
    
    # Documentation files to include
    documentation_files: List[str] = field(default_factory=list)
    
    # Claims to evaluate
    claims_of_success: Optional[str] = None
    
    # Custom prompt
    custom_prompt: Optional[str] = None
    
    # Review type templates
    review_templates: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "enterprise": {
            "prompt": "Evaluate against enterprise roadmap requirements",
            "focus": ["architecture", "scalability", "security", "maintainability"]
        },
        "security": {
            "prompt": "Perform a thorough security audit focusing on OWASP top 10",
            "focus": ["authentication", "authorization", "input validation", "secrets"]
        },
        "performance": {
            "prompt": "Identify performance bottlenecks and optimization opportunities",
            "focus": ["algorithms", "database queries", "caching", "async operations"]
        },
        "refactoring": {
            "prompt": "Identify technical debt and suggest refactoring opportunities",
            "focus": ["code duplication", "complex methods", "design patterns", "testability"]
        }
    })
    
    # This is a bit of a workaround for dataclasses not having an easy way
    # to handle deprecated fields during __init__ from a dict.
    # We accept `project_path` but don't store it as a main field.
    project_path: InitVar[Optional[str]] = None

    def __post_init__(self, project_path: Optional[str]):
        """Handle backward compatibility for project_path."""
        if project_path:
            # If project_paths is at its default value, use the legacy project_path
            if self.project_paths == ["."]:
                self.project_paths = [project_path]
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'ReviewConfig':
        """Load configuration from JSON or YAML file"""
        path = Path(config_path)
        
        if not path.exists():
            print(f"⚠️  Config file not found: {config_path}, using defaults")
            return cls()
            
        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif path.suffix == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {path.suffix}")
                    
            return cls(**data)
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            print(f"❌ Error parsing config file {config_path}: {e}")
            print("📋 Using default configuration")
            return cls()
    
    def save_to_file(self, config_path: str):
        """Save configuration to file"""
        path = Path(config_path)
        data = {
            'project_name': self.project_name,
            'project_paths': self.project_paths,
            'output_format': self.output_format,
            'output_file': self.output_file,
            'keep_repomix': self.keep_repomix,
            'remove_empty_lines': self.remove_empty_lines,
            'show_line_numbers': self.show_line_numbers,
            'include_diffs': self.include_diffs,
            'compress_code': self.compress_code,
            'token_count_encoding': self.token_count_encoding,
            'include_patterns': self.include_patterns,
            'ignore_patterns': self.ignore_patterns,
            'documentation_files': self.documentation_files,
            'claims_of_success': self.claims_of_success,
            'custom_prompt': self.custom_prompt,
            'review_templates': self.review_templates
        }
        
        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(data, f, indent=2)
                
    def get_review_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a predefined review template"""
        return self.review_templates.get(template_name)


def create_default_config(project_path) -> ReviewConfig:
    """Create a default configuration for a project"""
    # Handle case where project_path is a list (take first element)
    if isinstance(project_path, list):
        project_path = project_path[0] if project_path else "."
    
    project_name = Path(project_path).resolve().name
    
    config = ReviewConfig(
        project_name=project_name,
        project_paths=[project_path]
    )
    
    # Auto-detect common documentation patterns
    doc_patterns = [
        "README.md", "README.rst", "README.txt",
        "docs/*.md", "doc/*.md", "documentation/*.md",
        "ARCHITECTURE.md", "DESIGN.md", "API.md"
    ]
    
    for pattern in doc_patterns:
        matches = list(Path(project_path).glob(pattern))
        config.documentation_files.extend([str(m) for m in matches])
    
    return config


def find_config_file(start_path) -> Optional[str]:
    """Search for config file in current and parent directories"""
    search_names = [
        ".gemini-review.yaml",
        ".gemini-review.yml", 
        ".gemini-review.json",
        "gemini-review.yaml",
        "gemini-review.yml",
        "gemini-review.json"
    ]
    
    # Handle case where start_path is a list (take first element)
    if isinstance(start_path, list):
        start_path = start_path[0] if start_path else "."
    
    current = Path(start_path).resolve()
    
    while current != current.parent:
        for name in search_names:
            config_path = current / name
            if config_path.exists():
                return str(config_path)
        current = current.parent

    # Fallback: check the directory where this module lives (e.g. gemini-review-tool)
    tool_dir = Path(__file__).resolve().parent
    for name in search_names:
        tool_config = tool_dir / name
        if tool_config.exists():
            return str(tool_config)
 
    return None


if __name__ == "__main__":
    # Example: Create a default config
    config = create_default_config()
    config.save_to_file("example-config.yaml")
    print("Created example-config.yaml")