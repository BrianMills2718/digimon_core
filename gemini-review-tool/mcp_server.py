#!/usr/bin/env python3
"""
Gemini Review Tool MCP Server

A FastMCP server that exposes the gemini-review-tool functionality 
for use with Claude Code and other MCP clients.

Features:
- Run Gemini code reviews with precise file filtering
- Preview files before review
- Create validation configs for complex workflows
- No caching complexity - always fresh results
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add the current directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    import fastmcp
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastmcp"])
    import fastmcp
    from fastmcp import FastMCP

# We'll use subprocess calls instead of direct imports to avoid complexity

# Initialize MCP server
mcp = FastMCP("Gemini Review Tool")


@mcp.tool()
def run_gemini_review(
    prompt: str,
    include_patterns: str,
    exclude_patterns: str = "",
    working_dir: str = ""
) -> str:
    """
    Run Gemini code review with precise file filtering.
    
    Args:
        prompt: What you want Gemini to analyze/validate
        include_patterns: Files/directories to include (comma-separated)
        exclude_patterns: Files/patterns to exclude from included files (comma-separated)
        working_dir: Directory to run from (defaults to current directory)
    
    Returns:
        Gemini's analysis results
    
    Example:
        run_gemini_review(
            "Validate async database operations use real AsyncGraphDatabase",
            "src/core/neo4j_manager.py,src/core/database",
            "__pycache__,*.log,test_fixtures/*"
        )
    """
    try:
        # Set working directory
        original_dir = os.getcwd()
        if working_dir:
            os.chdir(working_dir)
        
        # Parse patterns
        include_list = [p.strip() for p in include_patterns.split(",") if p.strip()]
        exclude_list = [p.strip() for p in exclude_patterns.split(",") if p.strip()] if exclude_patterns else []
        
        # Create temporary config
        config_data = {
            "project_name": f"MCP Review {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "custom_prompt": prompt,
            "include_patterns": include_list,
            "exclude_patterns": exclude_list,
            "claims_of_success": [prompt]  # Use prompt as single claim
        }
        
        # Write temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f, indent=2)
            temp_config = f.name
        
        try:
            # Run gemini review
            result = subprocess.run([
                sys.executable, "gemini_review.py",
                "--config", temp_config,
                "--no-cache"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode != 0:
                return f"❌ Error running Gemini review:\n{result.stderr}\n{result.stdout}"
            
            return result.stdout
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_config)
            except:
                pass
                
    except Exception as e:
        return f"❌ Error: {str(e)}"
    finally:
        # Restore original directory
        os.chdir(original_dir)


@mcp.tool()
def preview_files(
    include_patterns: str,
    exclude_patterns: str = "",
    working_dir: str = ""
) -> str:
    """
    Preview what files would be included in the Gemini review.
    
    Args:
        include_patterns: Files/directories to include (comma-separated)
        exclude_patterns: Files/patterns to exclude (comma-separated)
        working_dir: Directory to run from (defaults to current directory)
    
    Returns:
        List of files that would be analyzed
    
    Example:
        preview_files("src/core", "*.log,__pycache__")
    """
    try:
        # Set working directory
        original_dir = os.getcwd()
        if working_dir:
            os.chdir(working_dir)
        
        # Parse patterns
        include_list = [p.strip() for p in include_patterns.split(",") if p.strip()]
        exclude_list = [p.strip() for p in exclude_patterns.split(",") if p.strip()] if exclude_patterns else []
        
        # Use repomix to get file list (dry run)
        cmd = ["npx", "repomix", "--dry-run"]
        
        # Add include patterns
        if include_list:
            cmd.extend(["--include", ",".join(include_list)])
        
        # Add exclude patterns
        if exclude_list:
            cmd.extend(["--ignore", ",".join(exclude_list)])
        
        cmd.append(".")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"❌ Error previewing files:\n{result.stderr}"
        
        # Parse the output to show just the files
        lines = result.stdout.split('\n')
        files = []
        for line in lines:
            if 'would include:' in line.lower() or 'including:' in line.lower():
                # Start collecting files after this line
                continue
            if line.strip() and not line.startswith('ℹ') and not line.startswith('✓'):
                files.append(line.strip())
        
        if not files:
            return "📁 No files found matching the patterns"
        
        return f"📁 Files to be analyzed ({len(files)} files):\n" + "\n".join(f"  • {f}" for f in files)
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
    finally:
        # Restore original directory
        os.chdir(original_dir)


@mcp.tool() 
def create_validation_config(
    project_name: str,
    include_patterns: str,
    exclude_patterns: str,
    custom_prompt: str,
    claims_of_success: str,
    working_dir: str = ""
) -> str:
    """
    Create a detailed validation config file for complex workflows.
    
    Args:
        project_name: Name for this validation
        include_patterns: Files/directories to include (comma-separated)
        exclude_patterns: Files/patterns to exclude (comma-separated)
        custom_prompt: Custom prompt for Gemini
        claims_of_success: Claims to validate (comma-separated or JSON list)
        working_dir: Directory to create config in (defaults to current directory)
    
    Returns:
        Path to created config file
    
    Example:
        create_validation_config(
            "Phase 2.1 Async Migration",
            "src/core/neo4j_manager.py,src/core/async_api_client.py",
            "*.log,__pycache__",
            "Validate async implementation claims",
            "Neo4j uses AsyncGraphDatabase,API client uses aiohttp sessions"
        )
    """
    try:
        # Set working directory
        original_dir = os.getcwd()
        if working_dir:
            os.chdir(working_dir)
        
        # Parse patterns
        include_list = [p.strip() for p in include_patterns.split(",") if p.strip()]
        exclude_list = [p.strip() for p in exclude_patterns.split(",") if p.strip()] if exclude_patterns else []
        
        # Parse claims - try JSON first, then comma-separated
        try:
            claims_list = json.loads(claims_of_success)
        except:
            claims_list = [c.strip() for c in claims_of_success.split(",") if c.strip()]
        
        # Create config data
        config_data = {
            "project_name": project_name,
            "custom_prompt": custom_prompt,
            "include_patterns": include_list,
            "exclude_patterns": exclude_list,
            "claims_of_success": claims_list,
            "created_at": datetime.now().isoformat(),
            "created_by": "MCP Server"
        }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_filename = f"validation-{timestamp}.yaml"
        
        # Write YAML config file
        import yaml
        with open(config_filename, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return f"✅ Created validation config: {config_filename}\n\nTo run:\npython gemini_review.py --config {config_filename} --no-cache"
        
    except Exception as e:
        return f"❌ Error creating config: {str(e)}"
    finally:
        # Restore original directory
        os.chdir(original_dir)


@mcp.tool()
def run_validation_from_config(
    config_file: str,
    working_dir: str = ""
) -> str:
    """
    Run validation using an existing config file.
    
    Args:
        config_file: Path to validation config file (.yaml or .json)
        working_dir: Directory to run from (defaults to current directory)
    
    Returns:
        Gemini's validation results
    
    Example:
        run_validation_from_config("validation-20250124_143000.yaml")
    """
    try:
        # Set working directory
        original_dir = os.getcwd()
        if working_dir:
            os.chdir(working_dir)
        
        # Check if config file exists
        if not os.path.exists(config_file):
            return f"❌ Config file not found: {config_file}"
        
        # Run gemini review with config
        result = subprocess.run([
            sys.executable, "gemini_review.py",
            "--config", config_file,
            "--no-cache"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            return f"❌ Error running validation:\n{result.stderr}\n{result.stdout}"
        
        return result.stdout
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
    finally:
        # Restore original directory
        os.chdir(original_dir)


@mcp.tool()
def list_validation_configs(working_dir: str = "") -> str:
    """
    List available validation config files.
    
    Args:
        working_dir: Directory to search in (defaults to current directory)
    
    Returns:
        List of available validation config files
    """
    try:
        # Set working directory
        original_dir = os.getcwd()
        if working_dir:
            os.chdir(working_dir)
        
        # Find validation config files
        config_files = []
        
        # Look for validation-*.yaml and validation-*.json files
        for pattern in ["validation-*.yaml", "validation-*.json"]:
            config_files.extend(Path(".").glob(pattern))
        
        if not config_files:
            return "📋 No validation config files found"
        
        # Sort by modification time (newest first)
        config_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        result = f"📋 Available validation configs ({len(config_files)} files):\n"
        for config_file in config_files:
            mtime = datetime.fromtimestamp(config_file.stat().st_mtime)
            result += f"  • {config_file.name} (modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')})\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
    finally:
        # Restore original directory
        os.chdir(original_dir)


@mcp.tool()
def get_validation_result(config_or_timestamp: str, working_dir: str = "") -> str:
    """
    Get the latest validation result from outputs directory.
    
    Args:
        config_or_timestamp: Config filename or timestamp to look for
        working_dir: Directory to search in (defaults to current directory)
    
    Returns:
        Latest validation result content
    """
    try:
        # Set working directory
        original_dir = os.getcwd()
        if working_dir:
            os.chdir(working_dir)
        
        outputs_dir = Path("outputs")
        if not outputs_dir.exists():
            return "📋 No outputs directory found. Run a validation first."
        
        # Look for the most recent output directory
        output_dirs = [d for d in outputs_dir.iterdir() if d.is_dir()]
        if not output_dirs:
            return "📋 No validation results found in outputs directory."
        
        # Sort by creation time (newest first)
        output_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # If specific timestamp provided, try to find matching directory
        if config_or_timestamp and not config_or_timestamp.endswith(('.yaml', '.json')):
            for output_dir in output_dirs:
                if config_or_timestamp in output_dir.name:
                    latest_dir = output_dir
                    break
            else:
                latest_dir = output_dirs[0]  # Fallback to newest
        else:
            latest_dir = output_dirs[0]  # Use newest
        
        # Look for review files in the latest directory
        review_files = []
        for pattern in ["*.md", "*/*.md"]:
            review_files.extend(latest_dir.glob(pattern))
        
        if not review_files:
            return f"📋 No review files found in {latest_dir.name}"
        
        # Read the main review file
        main_review = None
        for review_file in review_files:
            if "review" in review_file.name.lower():
                main_review = review_file
                break
        
        if not main_review:
            main_review = review_files[0]  # Use first file found
        
        with open(main_review, 'r') as f:
            content = f.read()
        
        return f"📋 Latest validation result from {latest_dir.name}:\n\n{content}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
    finally:
        # Restore original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()