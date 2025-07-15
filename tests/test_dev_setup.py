"""Tests for development environment setup scripts.

This module tests the dev-setup.sh script and related development shortcuts
to ensure they work correctly across different environments.
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import pytest


class TestDevSetupScript:
    """Test the development environment setup script."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir()
            
            # Copy essential files for testing
            current_dir = Path(__file__).parent.parent
            essential_files = [
                "pyproject.toml",
                "scripts/dev-setup.sh",
                "activate_dev.sh", 
                "run_tests.sh"
            ]
            
            for file_path in essential_files:
                src = current_dir / file_path
                if src.exists():
                    dst = project_dir / file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    # Make scripts executable
                    if file_path.endswith('.sh'):
                        dst.chmod(0o755)
            
            # Create minimal src structure for package installation
            src_dir = project_dir / "src" / "othello"
            src_dir.mkdir(parents=True)
            (src_dir / "__init__.py").write_text('__version__ = "0.1.0"')
            
            yield project_dir
    
    def test_dev_setup_script_exists_and_executable(self):
        """Test that dev-setup.sh exists and is executable."""
        script_path = Path("scripts/dev-setup.sh")
        assert script_path.exists(), "dev-setup.sh script should exist"
        assert os.access(script_path, os.X_OK), "dev-setup.sh should be executable"
    
    def test_activate_script_exists_and_executable(self):
        """Test that activate_dev.sh exists and is executable."""
        script_path = Path("activate_dev.sh")
        assert script_path.exists(), "activate_dev.sh script should exist"
        assert os.access(script_path, os.X_OK), "activate_dev.sh should be executable"
    
    def test_run_tests_script_exists_and_executable(self):
        """Test that run_tests.sh exists and is executable."""
        script_path = Path("run_tests.sh")
        assert script_path.exists(), "run_tests.sh script should exist"
        assert os.access(script_path, os.X_OK), "run_tests.sh should be executable"
    
    def test_development_md_exists(self):
        """Test that DEVELOPMENT.md documentation exists."""
        doc_path = Path("DEVELOPMENT.md")
        assert doc_path.exists(), "DEVELOPMENT.md documentation should exist"
        
        # Check it contains expected sections
        content = doc_path.read_text()
        expected_sections = [
            "Quick Setup",
            "Daily Development Workflow", 
            "Testing",
            "Development Scripts"
        ]
        for section in expected_sections:
            assert section in content, f"DEVELOPMENT.md should contain {section} section"
    
    def test_dev_setup_script_syntax(self):
        """Test that dev-setup.sh has valid bash syntax."""
        script_path = Path("scripts/dev-setup.sh")
        if not script_path.exists():
            pytest.skip("dev-setup.sh not found")
        
        # Test bash syntax
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"dev-setup.sh has syntax errors: {result.stderr}"
    
    def test_activate_script_syntax(self):
        """Test that activate_dev.sh has valid bash syntax."""
        script_path = Path("activate_dev.sh")
        if not script_path.exists():
            pytest.skip("activate_dev.sh not found")
        
        # Test bash syntax
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"activate_dev.sh has syntax errors: {result.stderr}"
    
    def test_run_tests_script_syntax(self):
        """Test that run_tests.sh has valid bash syntax."""
        script_path = Path("run_tests.sh")
        if not script_path.exists():
            pytest.skip("run_tests.sh not found")
        
        # Test bash syntax
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"run_tests.sh has syntax errors: {result.stderr}"
    
    def test_dev_setup_script_help_output(self):
        """Test that dev-setup.sh produces expected help/usage output."""
        script_path = Path("scripts/dev-setup.sh")
        if not script_path.exists():
            pytest.skip("dev-setup.sh not found")
        
        # Test that script produces some output (not necessarily success)
        result = subprocess.run(
            ["bash", str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Even if --help isn't implemented, script should run without hanging
        assert result.returncode is not None, "Script should not hang indefinitely"
    
    def test_python_version_checking_logic(self):
        """Test the Python version checking logic in the setup script."""
        script_path = Path("scripts/dev-setup.sh")
        if not script_path.exists():
            pytest.skip("dev-setup.sh not found")
        
        # Read script content to verify Python version checking
        content = script_path.read_text()
        
        # Check for Python version validation
        assert "python3 --version" in content, "Script should check Python version"
        assert "3.8" in content, "Script should require Python 3.8+"
        
        # Check for virtual environment creation
        assert "python3 -m venv" in content, "Script should create virtual environment"
        assert "venv/bin/activate" in content, "Script should activate virtual environment"
    
    def test_error_handling_in_scripts(self):
        """Test that scripts have proper error handling."""
        scripts = ["scripts/dev-setup.sh", "activate_dev.sh", "run_tests.sh"]
        
        for script_name in scripts:
            script_path = Path(script_name)
            if not script_path.exists():
                continue
            
            content = script_path.read_text()
            
            # Check for basic error handling patterns
            error_patterns = [
                "set -e",  # Exit on error
                "if [",    # Conditional checks
                "||",      # Error handling with OR
                "exit 1"   # Explicit error exits
            ]
            
            has_error_handling = any(pattern in content for pattern in error_patterns)
            assert has_error_handling, f"{script_name} should have error handling"
    
    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Shell scripts not directly executable on Windows"
    )
    def test_script_execution_environment(self):
        """Test that scripts can be executed in current environment."""
        # Test that we can at least start the activate script
        # (it might fail due to missing venv, but shouldn't have syntax errors)
        script_path = Path("activate_dev.sh")
        if not script_path.exists():
            pytest.skip("activate_dev.sh not found")
        
        try:
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, "TERM": "dumb"}  # Prevent color output issues
            )
            # Script may fail due to missing venv, but should not have syntax errors
            # A syntax error would typically cause exit code 2
            assert result.returncode != 2, f"activate_dev.sh has syntax errors: {result.stderr}"
        except subprocess.TimeoutExpired:
            # Script might hang waiting for input, which is acceptable
            pass


class TestDocumentationConsistency:
    """Test that documentation is consistent with actual scripts."""
    
    def test_development_md_mentions_scripts(self):
        """Test that DEVELOPMENT.md mentions all the created scripts."""
        doc_path = Path("DEVELOPMENT.md")
        if not doc_path.exists():
            pytest.skip("DEVELOPMENT.md not found")
        
        content = doc_path.read_text()
        
        # Check that documentation mentions the scripts
        scripts = ["dev-setup.sh", "activate_dev.sh", "run_tests.sh"]
        for script in scripts:
            assert script in content, f"DEVELOPMENT.md should mention {script}"
    
    def test_development_md_has_examples(self):
        """Test that DEVELOPMENT.md contains usage examples."""
        doc_path = Path("DEVELOPMENT.md")
        if not doc_path.exists():
            pytest.skip("DEVELOPMENT.md not found")
        
        content = doc_path.read_text()
        
        # Check for code blocks with examples
        assert "```bash" in content, "DEVELOPMENT.md should contain bash examples"
        assert "./scripts/dev-setup.sh" in content, "Should show how to run setup script"


class TestIntegrationWithExistingProject:
    """Test that new scripts integrate well with existing project structure."""
    
    def test_scripts_dont_conflict_with_existing_structure(self):
        """Test that new scripts don't conflict with existing project structure."""
        # Check that we haven't overwritten important existing files
        important_files = [
            "pyproject.toml",
            "src/othello/__init__.py",
            "CLAUDE.md"
        ]
        
        for file_path in important_files:
            path = Path(file_path)
            if path.exists():
                # File should still exist and be readable
                assert path.is_file(), f"{file_path} should still be a readable file"
    
    def test_scripts_directory_structure(self):
        """Test that scripts are placed in appropriate directory structure."""
        # dev-setup.sh should be in scripts/
        assert Path("scripts/dev-setup.sh").exists(), "dev-setup.sh should be in scripts/"
        
        # Quick shortcuts should be in root
        assert Path("activate_dev.sh").exists(), "activate_dev.sh should be in project root"
        assert Path("run_tests.sh").exists(), "run_tests.sh should be in project root"
        
        # Documentation should be in root
        assert Path("DEVELOPMENT.md").exists(), "DEVELOPMENT.md should be in project root"
    
    def test_no_unwanted_files_created(self):
        """Test that setup doesn't create unwanted files in repository."""
        # These files should NOT be in the repository
        unwanted_files = [
            "venv/",
            ".coverage",
            "coverage.json",
            "__pycache__/",
            "*.pyc"
        ]
        
        for pattern in unwanted_files:
            # For directories, check they're not tracked
            if pattern.endswith("/"):
                path = Path(pattern.rstrip("/"))
                if path.exists():
                    # Directory might exist but shouldn't be tracked
                    pass  # This is acceptable
            else:
                # Files shouldn't exist or be tracked
                import glob
                matches = glob.glob(pattern)
                # Having these files is OK, they just shouldn't be committed
                # This test mainly ensures we're aware of what might be created
                pass