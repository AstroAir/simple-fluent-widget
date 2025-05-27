#!/usr/bin/env python3
"""
Build and Test Script for Fluent UI Components

This script provides a convenient way to build, test, and package the Fluent UI components library.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import Optional


class FluentUIBuilder:
    """Build system for Fluent UI Components"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_exe = sys.executable
    def run_command(self, command: str, description: Optional[str] = None):
        """Run a command and handle errors"""
        if description:
            print(f"🔨 {description}...")
            print(f"🔨 {description}...")

        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, cwd=self.project_root)

        if result.returncode != 0:
            print(f"❌ Command failed with exit code {result.returncode}")
            return False

        print(f"✅ {description or 'Command'} completed successfully")
        return True

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("📋 Checking dependencies...")

        required_packages = [
            'PySide6',
            'psutil'
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} (missing)")
                missing_packages.append(package)

        if missing_packages:
            print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
            print("Run 'python build.py install-deps' to install them.")
            return False

        print("✅ All dependencies are installed")
        return True

    def install_dependencies(self):
        """Install required dependencies"""
        print("📦 Installing dependencies...")

        dependencies = [
            'PySide6>=6.5.0',
            'psutil>=5.9.0'
        ]

        for dep in dependencies:
            if not self.run_command(f"{self.python_exe} -m pip install {dep}", f"Installing {dep}"):
                return False

        return True

    def run_tests(self):
        """Run all tests"""
        print("🧪 Running tests...")

        # Run integration tests
        test_script = self.project_root / "tests" / "integration_test.py"
        if test_script.exists():
            if not self.run_command(f"{self.python_exe} {test_script}", "Running integration tests"):
                return False
        else:
            print("⚠️ Integration tests not found")

        return True

    def run_benchmarks(self):
        """Run performance benchmarks"""
        print("⚡ Running performance benchmarks...")

        benchmark_script = self.project_root / "tests" / "performance_benchmark.py"
        if benchmark_script.exists():
            if not self.run_command(f"{self.python_exe} {benchmark_script}", "Running benchmarks"):
                return False
        else:
            print("⚠️ Performance benchmarks not found")

        return True

    def run_demo(self):
        """Run the comprehensive demo"""
        print("🎬 Running comprehensive demo...")

        demo_script = self.project_root / "examples" / "comprehensive_demo.py"
        if demo_script.exists():
            if not self.run_command(f"{self.python_exe} {demo_script}", "Running demo"):
                return False
        else:
            print("⚠️ Demo script not found")

        return True

    def generate_docs(self):
        """Generate documentation"""
        print("📚 Generating documentation...")

        docs_script = self.project_root / "tools" / "generate_docs.py"
        if docs_script.exists():
            if not self.run_command(f"{self.python_exe} {docs_script}", "Generating documentation"):
                return False
        else:
            print("⚠️ Documentation generator not found")

        return True

    def clean(self):
        """Clean build artifacts"""
        print("🧹 Cleaning build artifacts...")

        patterns_to_clean = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.pytest_cache",
            "**/build",
            "**/dist",
            "**/*.egg-info"
        ]

        import shutil
        import glob

        for pattern in patterns_to_clean:
            for path in glob.glob(str(self.project_root / pattern), recursive=True):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        print(f"  Removed directory: {path}")
                    else:
                        os.remove(path)
                        print(f"  Removed file: {path}")
                except Exception as e:
                    print(f"  Warning: Could not remove {path}: {e}")

        print("✅ Cleanup completed")
        return True

    def lint_code(self):
        """Run code linting (if available)"""
        print("🔍 Running code linting...")

        # Try to run flake8 or other linters if available
        linters = ['flake8', 'pylint', 'black --check']

        for linter in linters:
            try:
                result = subprocess.run(
                    f"{linter} --version", shell=True, capture_output=True)
                if result.returncode == 0:
                    print(f"Running {linter}...")
                    self.run_command(
                        f"{linter} components/ core/ examples/ tools/", f"Linting with {linter}")
                    break
            except:
                continue
        else:
            print("ℹ️ No linters found, skipping code linting")

        return True

    def package(self):
        """Package the library"""
        print("📦 Packaging library...")

        # Check if pyproject.toml exists
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            return self.run_command(f"{self.python_exe} -m build", "Building package")
        else:
            print("⚠️ pyproject.toml not found, skipping packaging")
            return True

    def build_all(self):
        """Run complete build process"""
        print("🚀 Starting complete build process...\n")

        steps = [
            ("Checking dependencies", self.check_dependencies),
            ("Cleaning artifacts", self.clean),
            ("Running tests", self.run_tests),
            ("Running benchmarks", self.run_benchmarks),
            ("Generating documentation", self.generate_docs),
            ("Linting code", self.lint_code)
        ]

        for step_name, step_func in steps:
            print(f"\n{'='*60}")
            print(f"Step: {step_name}")
            print('='*60)

            if not step_func():
                print(f"❌ Build failed at step: {step_name}")
                return False

        print(f"\n{'='*60}")
        print("🎉 Build completed successfully!")
        print('='*60)
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Build and test Fluent UI Components")
    parser.add_argument('command', nargs='?', default='build',
                        choices=['build', 'test', 'benchmark', 'demo', 'docs', 'clean',
                                 'lint', 'package', 'install-deps', 'check-deps'],
                        help='Command to run')

    args = parser.parse_args()
    builder = FluentUIBuilder()

    commands = {
        'build': builder.build_all,
        'test': builder.run_tests,
        'benchmark': builder.run_benchmarks,
        'demo': builder.run_demo,
        'docs': builder.generate_docs,
        'clean': builder.clean,
        'lint': builder.lint_code,
        'package': builder.package,
        'install-deps': builder.install_dependencies,
        'check-deps': builder.check_dependencies
    }

    if args.command in commands:
        success = commands[args.command]()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
