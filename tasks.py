"""Makefile-like commands for development."""

# You can run these commands with: poetry run python -m tasks <command>
# Or create shell scripts for convenience

import subprocess
import sys


def test():
    """Run tests with pytest."""
    subprocess.run([sys.executable, "-m", "pytest", "-v"])


def test_cov():
    """Run tests with coverage."""
    subprocess.run([
        sys.executable, "-m", "pytest",
        "--cov=src/random_file_picker",
        "--cov-report=html",
        "--cov-report=term"
    ])


def lint():
    """Run linting tools."""
    print("Running black...")
    subprocess.run([sys.executable, "-m", "black", "src", "tests"])
    
    print("\nRunning isort...")
    subprocess.run([sys.executable, "-m", "isort", "src", "tests"])
    
    print("\nRunning flake8...")
    subprocess.run([sys.executable, "-m", "flake8", "src", "tests"])


def type_check():
    """Run type checking with mypy."""
    subprocess.run([sys.executable, "-m", "mypy", "src"])


def format_code():
    """Format code with black and isort."""
    subprocess.run([sys.executable, "-m", "black", "src", "tests"])
    subprocess.run([sys.executable, "-m", "isort", "src", "tests"])


def clean():
    """Clean up build artifacts and cache."""
    import shutil
    from pathlib import Path
    
    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "dist",
        "build",
        "*.egg-info",
    ]
    
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
    
    print("Cleanup complete!")


if __name__ == "__main__":
    commands = {
        "test": test,
        "test-cov": test_cov,
        "lint": lint,
        "type-check": type_check,
        "format": format_code,
        "clean": clean,
    }
    
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("Available commands:")
        for cmd in commands:
            print(f"  - {cmd}")
        sys.exit(1)
    
    commands[sys.argv[1]]()
