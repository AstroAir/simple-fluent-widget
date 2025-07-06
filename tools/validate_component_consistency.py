"""
Fluent UI Component Consistency Validator
Validates that all components follow the established patterns and interfaces
"""

import os
import ast
import inspect
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path

# Import base interfaces
from components.base.fluent_component_interface import (
    IFluentComponent, FluentComponentState, FluentComponentSize, 
    FluentComponentVariant, FluentComponentMixin
)
from components.base.enhanced_fluent_control_base import FluentControlBase


class ComponentAnalyzer:
    """Analyzes component files for consistency"""
    
    def __init__(self, components_dir: str = "components"):
        self.components_dir = Path(components_dir)
        self.issues: List[Dict[str, Any]] = []
        self.component_files: List[Path] = []
        self.analyzed_classes: Dict[str, Dict[str, Any]] = {}
    
    def analyze_all_components(self) -> Dict[str, Any]:
        """Analyze all components for consistency"""
        print("🔍 Starting Fluent UI Component Consistency Analysis...")
        
        # Find all component files
        self._find_component_files()
        print(f"📁 Found {len(self.component_files)} component files")
        
        # Analyze each file
        for file_path in self.component_files:
            self._analyze_file(file_path)
        
        # Generate report
        report = self._generate_report()
        return report
    
    def _find_component_files(self):
        """Find all Python component files"""
        for root, dirs, files in os.walk(self.components_dir):
            # Skip __pycache__ and other non-component directories
            dirs[:] = [d for d in dirs if not d.startswith('__')]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = Path(root) / file
                    self.component_files.append(file_path)
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single component file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Find classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._analyze_class(file_path, node, content)
                    
        except Exception as e:
            self.issues.append({
                'type': 'parsing_error',
                'file': str(file_path),
                'message': f"Failed to parse file: {e}",
                'severity': 'error'
            })
    
    def _analyze_class(self, file_path: Path, class_node: ast.ClassDef, content: str):
        """Analyze a single class for compliance"""
        class_name = class_node.name
        
        # Skip non-Fluent classes
        if not (class_name.startswith('Fluent') or 'fluent' in class_name.lower()):
            return
        
        print(f"  📋 Analyzing class: {class_name} in {file_path.name}")
        
        class_info = {
            'name': class_name,
            'file': str(file_path),
            'line': class_node.lineno,
            'base_classes': [base.id for base in class_node.bases if isinstance(base, ast.Name)],
            'methods': [],
            'signals': [],
            'properties': []
        }
        
        # Analyze methods and attributes
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                class_info['methods'].append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        class_info['properties'].append(target.id)
        
        self.analyzed_classes[class_name] = class_info
        
        # Run consistency checks
        self._check_base_class_compliance(class_info)
        self._check_naming_conventions(class_info)
        self._check_required_methods(class_info)
        self._check_signal_conventions(class_info)
        self._check_documentation(class_node, class_info)
    
    def _check_base_class_compliance(self, class_info: Dict[str, Any]):
        """Check if class properly inherits from base classes"""
        base_classes = class_info['base_classes']
        class_name = class_info['name']
        
        # Check for proper base class inheritance
        has_fluent_base = any(
            base in ['FluentControlBase', 'FluentBaseWidget', 'QWidget'] 
            for base in base_classes
        )
        
        if not has_fluent_base and class_name.startswith('Fluent'):
            self.issues.append({
                'type': 'base_class',
                'class': class_name,
                'file': class_info['file'],
                'line': class_info['line'],
                'message': f"Class {class_name} should inherit from FluentControlBase or similar",
                'severity': 'warning'
            })
    
    def _check_naming_conventions(self, class_info: Dict[str, Any]):
        """Check naming conventions"""
        class_name = class_info['name']
        
        # Check class naming
        if not class_name.startswith('Fluent'):
            self.issues.append({
                'type': 'naming',
                'class': class_name,
                'file': class_info['file'],
                'line': class_info['line'],
                'message': f"Component class should start with 'Fluent' prefix",
                'severity': 'warning'
            })
        
        # Check for consistent naming patterns
        methods = class_info['methods']
        
        # Check for consistent get/set patterns
        getters = [m for m in methods if m.startswith('get_')]
        setters = [m for m in methods if m.startswith('set_')]
        
        for getter in getters:
            property_name = getter[4:]  # Remove 'get_'
            expected_setter = f"set_{property_name}"
            if expected_setter not in setters:
                self.issues.append({
                    'type': 'naming',
                    'class': class_name,
                    'file': class_info['file'],
                    'message': f"Getter {getter} missing corresponding setter {expected_setter}",
                    'severity': 'info'
                })
    
    def _check_required_methods(self, class_info: Dict[str, Any]):
        """Check for required interface methods"""
        class_name = class_info['name']
        methods = class_info['methods']
        
        # Required methods for Fluent components
        required_methods = [
            '_apply_themed_styles',
            '_apply_state_styles',
            'get_value',
            'set_value'
        ]
        
        missing_methods = [m for m in required_methods if m not in methods]
        
        for method in missing_methods:
            self.issues.append({
                'type': 'interface',
                'class': class_name,
                'file': class_info['file'],
                'message': f"Missing required method: {method}",
                'severity': 'error'
            })
    
    def _check_signal_conventions(self, class_info: Dict[str, Any]):
        """Check signal naming and usage conventions"""
        class_name = class_info['name']
        
        # Common signal patterns that should be present
        expected_signals = ['clicked', 'value_changed', 'state_changed']
        
        # This is a simplified check - in practice, you'd parse the actual signal definitions
        # For now, we'll just check for common patterns in method names
        methods = class_info['methods']
        signal_related_methods = [m for m in methods if 'signal' in m.lower() or m.startswith('_on_')]
        
        if not signal_related_methods and class_name.endswith(('Button', 'Input', 'Box')):
            self.issues.append({
                'type': 'signals',
                'class': class_name,
                'file': class_info['file'],
                'message': f"Interactive component should have signal handling methods",
                'severity': 'info'
            })
    
    def _check_documentation(self, class_node: ast.ClassDef, class_info: Dict[str, Any]):
        """Check documentation standards"""
        class_name = class_info['name']
        
        # Check for class docstring
        if not ast.get_docstring(class_node):
            self.issues.append({
                'type': 'documentation',
                'class': class_name,
                'file': class_info['file'],
                'line': class_info['line'],
                'message': f"Class {class_name} missing docstring",
                'severity': 'warning'
            })
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate consistency analysis report"""
        # Categorize issues by severity
        errors = [i for i in self.issues if i['severity'] == 'error']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        info = [i for i in self.issues if i['severity'] == 'info']
        
        # Categorize by type
        issue_types = {}
        for issue in self.issues:
            issue_type = issue['type']
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        report = {
            'summary': {
                'total_files': len(self.component_files),
                'total_classes': len(self.analyzed_classes),
                'total_issues': len(self.issues),
                'errors': len(errors),
                'warnings': len(warnings),
                'info': len(info)
            },
            'issues': {
                'errors': errors,
                'warnings': warnings,
                'info': info
            },
            'issue_types': issue_types,
            'analyzed_classes': self.analyzed_classes
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted consistency report"""
        summary = report['summary']
        
        print("\n" + "="*60)
        print("🎯 FLUENT UI COMPONENT CONSISTENCY REPORT")
        print("="*60)
        
        print(f"\n📊 SUMMARY:")
        print(f"  Files analyzed: {summary['total_files']}")
        print(f"  Classes analyzed: {summary['total_classes']}")
        print(f"  Total issues: {summary['total_issues']}")
        print(f"  ❌ Errors: {summary['errors']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        print(f"  ℹ️  Info: {summary['info']}")
        
        # Print issues by category
        for severity in ['errors', 'warnings', 'info']:
            issues = report['issues'][severity]
            if issues:
                icon = {'errors': '❌', 'warnings': '⚠️', 'info': 'ℹ️'}[severity]
                print(f"\n{icon} {severity.upper()}:")
                for issue in issues[:10]:  # Limit to first 10
                    print(f"  • {issue.get('class', 'Unknown')}: {issue['message']}")
                    print(f"    📁 {issue['file']}")
                if len(issues) > 10:
                    print(f"    ... and {len(issues) - 10} more")
        
        # Print recommendations
        print(f"\n🔧 RECOMMENDATIONS:")
        if summary['errors'] > 0:
            print("  1. Fix all errors first - these break interface compliance")
        if summary['warnings'] > 0:
            print("  2. Address warnings to improve consistency")
        if summary['info'] > 0:
            print("  3. Review info items for best practices")
        
        # Calculate compliance score
        total_issues = summary['total_issues']
        total_classes = summary['total_classes']
        if total_classes > 0:
            compliance_score = max(0, 100 - (total_issues * 10 / total_classes))
            print(f"\n🏆 COMPLIANCE SCORE: {compliance_score:.1f}%")
            
            if compliance_score >= 90:
                print("   Excellent! Components are highly consistent.")
            elif compliance_score >= 75:
                print("   Good! Minor improvements needed.")
            elif compliance_score >= 50:
                print("   Fair. Significant improvements recommended.")
            else:
                print("   Poor. Major refactoring needed for consistency.")


def main():
    """Run the consistency analysis"""
    try:
        analyzer = ComponentAnalyzer()
        report = analyzer.analyze_all_components()
        analyzer.print_report(report)
        
        # Save detailed report to file
        import json
        with open('component_consistency_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Detailed report saved to: component_consistency_report.json")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
