"""
Tests to verify that critical syntax errors are fixed.
These tests should fail initially, then pass after fixes are applied.
"""
import py_compile
import tempfile
import subprocess
import sys
from pathlib import Path


def test_production_monitoring_compiles():
    """Test that production_monitoring.py compiles without syntax errors"""
    file_path = 'src/monitoring/production_monitoring.py'
    
    if not Path(file_path).exists():
        pytest.skip(f"File {file_path} does not exist")
    
    try:
        py_compile.compile(file_path, doraise=True)
        # If we get here, compilation succeeded
        assert True, "File compiles successfully"
    except py_compile.PyCompileError as e:
        # This should fail initially due to await outside async
        error_msg = str(e)
        if "await" in error_msg and "outside async function" in error_msg:
            assert False, f"Syntax error found: {error_msg}"
        else:
            # Some other compilation error
            assert False, f"Unexpected compilation error: {error_msg}"


def test_backup_manager_compiles():
    """Test that backup_manager.py compiles without indentation errors"""
    file_path = 'src/core/backup_manager.py'
    
    if not Path(file_path).exists():
        pytest.skip(f"File {file_path} does not exist")
    
    try:
        py_compile.compile(file_path, doraise=True)
        assert True, "File compiles successfully"
    except py_compile.PyCompileError as e:
        # This should fail initially due to indentation errors
        error_msg = str(e)
        assert False, f"Compilation error found: {error_msg}"


def test_metrics_collector_compiles():
    """Test that metrics_collector.py compiles without import errors"""
    file_path = 'src/core/metrics_collector.py'
    
    if not Path(file_path).exists():
        pytest.skip(f"File {file_path} does not exist")
    
    try:
        py_compile.compile(file_path, doraise=True)
        assert True, "File compiles successfully"
    except py_compile.PyCompileError as e:
        # This should fail initially due to import/indentation errors
        error_msg = str(e)
        assert False, f"Compilation error found: {error_msg}"


def test_all_python_files_compile():
    """Test that all Python files in src/ compile without syntax errors"""
    src_files = list(Path('src').glob('**/*.py'))
    
    compilation_errors = []
    
    for file_path in src_files:
        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as e:
            compilation_errors.append(f"{file_path}: {str(e)}")
    
    if compilation_errors:
        error_summary = "\n".join(compilation_errors)
        assert False, f"Found compilation errors in {len(compilation_errors)} files:\n{error_summary}"


def test_python_syntax_check():
    """Test Python syntax using Python's AST parser"""
    import ast
    
    critical_files = [
        'src/monitoring/production_monitoring.py',
        'src/core/backup_manager.py', 
        'src/core/metrics_collector.py'
    ]
    
    syntax_errors = []
    
    for file_path in critical_files:
        if not Path(file_path).exists():
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Try to parse the AST
            ast.parse(source_code, filename=file_path)
            
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}:{e.lineno}: {e.msg}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: Unexpected error: {str(e)}")
    
    if syntax_errors:
        error_summary = "\n".join(syntax_errors)
        assert False, f"Found syntax errors in critical files:\n{error_summary}"


if __name__ == "__main__":
    print("🧪 Testing syntax errors in critical files...")
    
    try:
        test_production_monitoring_compiles()
        print("✅ production_monitoring.py compiles successfully")
    except AssertionError as e:
        print(f"❌ production_monitoring.py: {e}")
    
    try:
        test_backup_manager_compiles()
        print("✅ backup_manager.py compiles successfully")
    except AssertionError as e:
        print(f"❌ backup_manager.py: {e}")
        
    try:
        test_metrics_collector_compiles()
        print("✅ metrics_collector.py compiles successfully")
    except AssertionError as e:
        print(f"❌ metrics_collector.py: {e}")
        
    try:
        test_python_syntax_check()
        print("✅ All critical files pass AST syntax check")
    except AssertionError as e:
        print(f"❌ AST syntax check: {e}")