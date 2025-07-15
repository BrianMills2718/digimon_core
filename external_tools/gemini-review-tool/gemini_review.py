#!/usr/bin/env python3
"""
Gemini Code Review Automation Tool

This tool automates the process of:
1. Using repomix to package your codebase
2. Sending it to Gemini AI for analysis
3. Returning the critique and guidance
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# Try to import config module
try:
    from gemini_review_config import ReviewConfig, find_config_file, create_default_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Load environment variables
load_dotenv()

class GeminiCodeReviewer:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize the code reviewer with API key."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env file or pass it as argument.")
        
        # Get model name from env or use default
        self.model_name = model_name or os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        print(f"🤖 Using model: {self.model_name}")
        
    def run_repomix(self, project_path: str, output_format: str = "xml", 
                     ignore_patterns: Optional[list[str]] = None) -> Path:
        """Run repomix to package the codebase."""
        print(f"📦 Running repomix on {project_path}...")
        
        # Determine output file extension
        ext = "xml" if output_format == "xml" else "md"
        output_file = Path(f"repomix-output.{ext}")
        
        # Build repomix command
        cmd = ["npx", "repomix@latest", "--style", output_format]
        
        # Add ignore patterns if provided
        if ignore_patterns:
            ignore_pattern = ",".join(ignore_patterns)
            cmd.extend(["--ignore", ignore_pattern])
        
        # Add path if not current directory
        if project_path != ".":
            cmd.append(project_path)
        
        try:
            # Run repomix
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Repomix completed successfully")
            
            if not output_file.exists():
                raise FileNotFoundError(f"Repomix output file {output_file} not found")
                
            return output_file
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Repomix failed: {e.stderr}")
            raise
        except FileNotFoundError:
            print("❌ npx not found. Please ensure Node.js is installed.")
            raise
            
    def read_repomix_output(self, file_path: Path) -> str:
        """Read the repomix output file."""
        print(f"📖 Reading repomix output from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check file size (Gemini has token limits)
        file_size_mb = len(content) / (1024 * 1024)
        print(f"📊 File size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 10:  # Rough estimate for token limit
            print("⚠️  Warning: Large file size may exceed token limits")
            
        return content
        
    def analyze_code(self, codebase_content: str, custom_prompt: Optional[str] = None, 
                     claims_of_success: Optional[str] = None, documentation: Optional[str] = None) -> str:
        """Send codebase to Gemini for analysis."""
        print("🤖 Sending to Gemini for analysis...")
        
        # Build the critical evaluation prompt
        if claims_of_success:
            base_prompt = f"""Critically evaluate this codebase in terms of it reflecting the documentation and the previous dubious claims of success:

{claims_of_success}

Be thorough and skeptical. Look for discrepancies between the claims and the actual implementation."""
        else:
            # Fallback to standard prompt
            base_prompt = """You are an expert software architect and code reviewer. 
        Please analyze this codebase and provide:
        
        1. **Architecture Overview**: High-level assessment of the system design
        2. **Code Quality**: Identify issues with code structure, patterns, and best practices
        3. **Security Concerns**: Point out potential security vulnerabilities
        4. **Performance Issues**: Identify potential bottlenecks or inefficiencies
        5. **Technical Debt**: Areas that need refactoring or improvement
        6. **Recommendations**: Specific, actionable guidance for improvement
        
        Focus on providing practical, implementable suggestions."""
        
        if custom_prompt:
            prompt = f"{base_prompt}\n\nAdditional focus areas:\n{custom_prompt}\n\n"
        else:
            prompt = base_prompt + "\n\n"
        
        # Add documentation if provided
        if documentation:
            prompt += f"DOCUMENTATION:\n{documentation}\n\n"
            
        prompt += f"CODEBASE:\n{codebase_content}"
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            
            print("✅ Analysis complete")
            return response.text
            
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            raise
            
    def save_results(self, results: str, output_path: str = "gemini-review.md"):
        """Save the analysis results to a file."""
        print(f"💾 Saving results to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Gemini Code Review\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(results)
            
        print(f"✅ Results saved to {output_path}")
        
    def cleanup(self, repomix_file: Path):
        """Clean up temporary files."""
        if repomix_file.exists():
            repomix_file.unlink()
            print("🧹 Cleaned up temporary files")
            
    def review(self, project_path: str = ".", 
              custom_prompt: Optional[str] = None,
              output_format: str = "xml",
              keep_repomix: bool = False,
              ignore_patterns: Optional[list[str]] = None,
              claims_of_success: Optional[str] = None,
              documentation_files: Optional[list[str]] = None) -> str:
        """Main review process."""
        print(f"\n🚀 Starting Gemini Code Review for: {project_path}\n")
        
        repomix_file = None
        try:
            # Step 1: Run repomix
            repomix_file = self.run_repomix(project_path, output_format, ignore_patterns)
            
            # Step 2: Read the output
            codebase_content = self.read_repomix_output(repomix_file)
            
            # Step 3: Read documentation if provided
            documentation = ""
            if documentation_files:
                print("📚 Reading documentation files...")
                for doc_file in documentation_files:
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            documentation += f"\n\n--- {doc_file} ---\n\n"
                            documentation += f.read()
                    except Exception as e:
                        print(f"⚠️  Warning: Could not read {doc_file}: {e}")
            
            # Step 4: Analyze with Gemini
            results = self.analyze_code(codebase_content, custom_prompt, claims_of_success, documentation)
            
            # Step 4: Save results
            self.save_results(results)
            
            # Step 5: Cleanup (unless asked to keep)
            if not keep_repomix and repomix_file:
                self.cleanup(repomix_file)
                
            print("\n✨ Code review complete!")
            return results
            
        except Exception as e:
            print(f"\n❌ Error during review: {str(e)}")
            raise
        finally:
            # Ensure cleanup even on error
            if not keep_repomix and repomix_file and repomix_file.exists():
                self.cleanup(repomix_file)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Automated code review using Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review current directory
  python gemini_review.py
  
  # Review with config file
  python gemini_review.py --config project-review.yaml
  
  # Use a review template
  python gemini_review.py --template security
  
  # Initialize config for a new project
  python gemini_review.py --init
  
  # Review specific project
  python gemini_review.py /path/to/project
  
  # With custom focus
  python gemini_review.py --prompt "Focus on security vulnerabilities"
  
  # Use markdown format
  python gemini_review.py --format markdown
  
  # Keep repomix output
  python gemini_review.py --keep-repomix
        """
    )
    
    parser.add_argument(
        'project_path',
        nargs='?',
        default='.',
        help='Path to the project to review (default: current directory)'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        help='Additional prompt for specific review focus'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['xml', 'markdown'],
        default='xml',
        help='Repomix output format (default: xml)'
    )
    
    parser.add_argument(
        '--keep-repomix', '-k',
        action='store_true',
        help='Keep the repomix output file'
    )
    
    parser.add_argument(
        '--api-key',
        help='Gemini API key (can also be set via GEMINI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--ignore', '-i',
        action='append',
        help='Patterns to ignore in repomix (can be used multiple times)'
    )
    
    parser.add_argument(
        '--claims', '-c',
        help='Previous claims of success to evaluate against'
    )
    
    parser.add_argument(
        '--docs', '-d',
        action='append',
        help='Documentation files to include (can be used multiple times)'
    )
    
    parser.add_argument(
        '--config', '-C',
        help='Path to configuration file (YAML or JSON)'
    )
    
    parser.add_argument(
        '--template', '-t',
        help='Use a predefined review template (e.g., security, performance, refactoring)'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize a new configuration file for the project'
    )
    
    args = parser.parse_args()
    
    # Handle --init flag
    if args.init:
        if CONFIG_AVAILABLE:
            config = create_default_config(args.project_path or ".")
            config_path = ".gemini-review.yaml"
            config.save_to_file(config_path)
            print(f"✅ Created configuration file: {config_path}")
            print("📝 Edit this file to customize your review settings")
            sys.exit(0)
        else:
            print("❌ Config module not available. Please ensure gemini_review_config.py is in the same directory.")
            sys.exit(1)
    
    try:
        # Load configuration
        config = None
        if CONFIG_AVAILABLE:
            if args.config:
                # Use specified config file
                config = ReviewConfig.load_from_file(args.config)
            else:
                # Search for config file
                config_path = find_config_file(args.project_path or ".")
                if config_path:
                    print(f"📋 Using config file: {config_path}")
                    config = ReviewConfig.load_from_file(config_path)
        
        # Apply command-line overrides to config
        if config:
            if args.project_path:
                config.project_path = args.project_path
            if args.format:
                config.output_format = args.format
            if args.keep_repomix is not None:
                config.keep_repomix = args.keep_repomix
            if args.ignore:
                config.ignore_patterns.extend(args.ignore)
            if args.claims:
                config.claims_of_success = args.claims
            if args.docs:
                config.documentation_files.extend(args.docs)
            if args.prompt:
                config.custom_prompt = args.prompt
                
            # Apply template if specified
            if args.template:
                template = config.get_review_template(args.template)
                if template:
                    config.custom_prompt = template.get('prompt', config.custom_prompt)
                    print(f"📋 Using review template: {args.template}")
                else:
                    print(f"⚠️  Unknown template: {args.template}")
        
        # Initialize reviewer
        reviewer = GeminiCodeReviewer(api_key=args.api_key)
        
        # Run review with config or command-line args
        if config:
            reviewer.review(
                project_path=config.project_path,
                custom_prompt=config.custom_prompt,
                output_format=config.output_format,
                keep_repomix=config.keep_repomix,
                ignore_patterns=config.ignore_patterns,
                claims_of_success=config.claims_of_success,
                documentation_files=config.documentation_files
            )
        else:
            reviewer.review(
                project_path=args.project_path,
                custom_prompt=args.prompt,
                output_format=args.format,
                keep_repomix=args.keep_repomix,
                ignore_patterns=args.ignore,
                claims_of_success=args.claims,
                documentation_files=args.docs
            )
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()