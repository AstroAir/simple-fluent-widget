#!/usr/bin/env python3
"""
Performance Benchmark for Fluent UI Components

This module provides comprehensive performance benchmarks for all Fluent UI components
to ensure optimal performance in enterprise scenarios.
"""

import sys
import os
import time
import psutil
import gc
from typing import Dict, List, Any, Callable
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
from PySide6.QtCore import QTimer, QThread, Signal

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import all component modules
try:
    from components.data.charts import (
        FluentProgressRing, FluentBarChart, FluentLineChart, FluentPieChart
    )
    from components.data.entry import (
        FluentMaskedLineEdit, FluentAutoCompleteEdit, FluentRichTextEditor,
        FluentDateTimePicker, FluentSlider, FluentFileSelector
    )
    from components.data.tree import (
        FluentTreeWidget, FluentHierarchicalView, FluentOrgChart
    )
    from components.data.status import (
        FluentStatusIndicator, FluentProgressTracker, FluentNotification,
        FluentNotificationManager, FluentBadge
    )
    from components.layout.containers import (
        FluentCard, FluentExpander, FluentSplitter, FluentTabWidget,
        FluentInfoBar, FluentPivot
    )
    from components.media.players import (
        FluentImageViewer, FluentMediaPlayer, FluentRichContentViewer,
        FluentThumbnailGallery
    )
    from components.command.bars import (
        FluentCommandBar, FluentToolbar, FluentRibbon,
        FluentQuickAccessToolbar
    )
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import all components: {e}")
    COMPONENTS_AVAILABLE = False


class BenchmarkResult:
    """Container for benchmark results"""
    
    def __init__(self, name: str):
        self.name = name
        self.execution_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.errors: List[str] = []
    
    def add_measurement(self, execution_time: float, memory_mb: float, cpu_percent: float):
        """Add a measurement to the benchmark"""
        self.execution_times.append(execution_time)
        self.memory_usage.append(memory_mb)
        self.cpu_usage.append(cpu_percent)
    
    def add_error(self, error: str):
        """Add an error to the benchmark"""
        self.errors.append(error)
    
    def get_average_execution_time(self) -> float:
        """Get average execution time in seconds"""
        return sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
    
    def get_max_execution_time(self) -> float:
        """Get maximum execution time in seconds"""
        return max(self.execution_times) if self.execution_times else 0
    
    def get_average_memory_usage(self) -> float:
        """Get average memory usage in MB"""
        return sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
    
    def get_max_memory_usage(self) -> float:
        """Get maximum memory usage in MB"""
        return max(self.memory_usage) if self.memory_usage else 0
    
    def get_average_cpu_usage(self) -> float:
        """Get average CPU usage percentage"""
        return sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
    
    def has_errors(self) -> bool:
        """Check if benchmark has errors"""
        return len(self.errors) > 0
    
    def get_summary(self) -> str:
        """Get a summary of the benchmark results"""
        if self.has_errors():
            return f"{self.name}: FAILED - {len(self.errors)} errors"
        
        avg_time = self.get_average_execution_time() * 1000  # Convert to ms
        max_time = self.get_max_execution_time() * 1000
        avg_memory = self.get_average_memory_usage()
        max_memory = self.get_max_memory_usage()
        avg_cpu = self.get_average_cpu_usage()
        
        return (f"{self.name}: "
                f"Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms, "
                f"Memory: {avg_memory:.1f}MB (max: {max_memory:.1f}MB), "
                f"CPU: {avg_cpu:.1f}%")


class PerformanceBenchmark:
    """Performance benchmark runner for Fluent UI components"""
    
    def __init__(self):
        self.app = None
        self.results: Dict[str, BenchmarkResult] = {}
        self.widgets: List[QWidget] = []
        
    def setup(self):
        """Setup the benchmark environment"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # Force garbage collection before starting
        gc.collect()
    
    def cleanup(self):
        """Cleanup after benchmarks"""
        for widget in self.widgets:
            if widget and hasattr(widget, 'close'):
                widget.close()
        self.widgets.clear()
        QApplication.processEvents()
        gc.collect()
    
    def measure_performance(self, name: str, func: Callable, iterations: int = 10) -> BenchmarkResult:
        """Measure performance of a function"""
        result = BenchmarkResult(name)
        
        for i in range(iterations):
            # Get initial memory and CPU
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                # Measure execution time
                start_time = time.time()
                func()
                end_time = time.time()
                
                # Process events to ensure UI updates
                QApplication.processEvents()
                
                # Get final memory and CPU
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                cpu_percent = process.cpu_percent()
                
                execution_time = end_time - start_time
                memory_usage = final_memory - initial_memory
                
                result.add_measurement(execution_time, memory_usage, cpu_percent)
                
            except Exception as e:
                result.add_error(f"Iteration {i}: {str(e)}")
        
        self.results[name] = result
        return result
    
    def benchmark_component_creation(self):
        """Benchmark component creation performance"""
        if not COMPONENTS_AVAILABLE:
            return
        
        component_classes = [
            ("ProgressRing", FluentProgressRing),
            ("BarChart", FluentBarChart),
            ("LineChart", FluentLineChart),
            ("PieChart", FluentPieChart),
            ("MaskedLineEdit", FluentMaskedLineEdit),
            ("AutoCompleteEdit", FluentAutoCompleteEdit),
            ("RichTextEditor", FluentRichTextEditor),
            ("DateTimePicker", FluentDateTimePicker),
            ("Slider", FluentSlider),
            ("FileSelector", FluentFileSelector),
            ("TreeWidget", FluentTreeWidget),
            ("StatusIndicator", FluentStatusIndicator),
            ("ProgressTracker", FluentProgressTracker),
            ("Badge", FluentBadge),
            ("Card", FluentCard),
            ("Expander", FluentExpander),
            ("InfoBar", FluentInfoBar),
            ("ImageViewer", FluentImageViewer),
            ("RichContentViewer", FluentRichContentViewer),
            ("CommandBar", FluentCommandBar),
            ("Toolbar", FluentToolbar),
            ("QuickAccessToolbar", FluentQuickAccessToolbar)
        ]
        
        for name, component_class in component_classes:
            def create_component():
                try:
                    if component_class == FluentSlider:
                        widget = component_class(orientation=1)  # Qt.Horizontal
                    elif component_class == FluentStatusIndicator:
                        widget = component_class("info")
                    elif component_class == FluentInfoBar:
                        widget = component_class("info")
                    else:
                        widget = component_class()
                    
                    self.widgets.append(widget)
                    return widget
                except Exception as e:
                    print(f"Error creating {name}: {e}")
                    return None
            
            self.measure_performance(f"Create {name}", create_component, 5)
    
    def benchmark_data_operations(self):
        """Benchmark data operations performance"""
        if not COMPONENTS_AVAILABLE:
            return
        
        # Benchmark Bar Chart with large dataset
        bar_chart = FluentBarChart()
        self.widgets.append(bar_chart)
        
        def set_large_bar_data():
            data = [
                {"label": f"Item {i}", "value": i * 10, "color": "#0078d4"}
                for i in range(100)
            ]
            bar_chart.setData(data)
        
        self.measure_performance("BarChart Large Dataset", set_large_bar_data, 3)
        
        # Benchmark Line Chart with many points
        line_chart = FluentLineChart()
        self.widgets.append(line_chart)
        
        def set_large_line_data():
            data = [{"x": i, "y": i * 2 + (i % 10)} for i in range(200)]
            line_chart.setData(data)
        
        self.measure_performance("LineChart Large Dataset", set_large_line_data, 3)
        
        # Benchmark Tree Widget with many items
        tree_widget = FluentTreeWidget()
        self.widgets.append(tree_widget)
        
        def populate_large_tree():
            tree_widget.clear()
            for i in range(50):
                parent = tree_widget.createItem([f"Parent {i}"])
                tree_widget.addTopLevelItem(parent)
                for j in range(10):
                    child = tree_widget.createItem([f"Child {i}-{j}"])
                    parent.addChild(child)
        
        self.measure_performance("TreeWidget Large Dataset", populate_large_tree, 3)
    
    def benchmark_ui_interactions(self):
        """Benchmark UI interaction performance"""
        if not COMPONENTS_AVAILABLE:
            return
        
        # Benchmark Progress Ring updates
        progress_ring = FluentProgressRing()
        self.widgets.append(progress_ring)
        
        def update_progress():
            for i in range(0, 101, 10):
                progress_ring.setValue(i)
                progress_ring.setText(f"{i}%")
                QApplication.processEvents()
        
        self.measure_performance("ProgressRing Updates", update_progress, 5)
        
        # Benchmark Expander expand/collapse
        expander = FluentExpander()
        expander.setTitle("Test Expander")
        expander_content = QWidget()
        expander.setContent(expander_content)
        self.widgets.append(expander)
        
        def toggle_expander():
            for _ in range(10):
                expander.setExpanded(True)
                QApplication.processEvents()
                expander.setExpanded(False)
                QApplication.processEvents()
        
        self.measure_performance("Expander Toggle", toggle_expander, 3)
        
        # Benchmark Status Indicator animation
        status_indicator = FluentStatusIndicator("info")
        status_indicator.setAnimated(True)
        self.widgets.append(status_indicator)
        
        def animate_status():
            status_indicator.show()
            # Let animation run for a bit
            start_time = time.time()
            while time.time() - start_time < 0.5:  # 500ms
                QApplication.processEvents()
        
        self.measure_performance("StatusIndicator Animation", animate_status, 5)
    
    def benchmark_memory_usage(self):
        """Benchmark memory usage patterns"""
        if not COMPONENTS_AVAILABLE:
            return
        
        def create_and_destroy_components():
            temp_widgets = []
            
            # Create many components
            for _ in range(20):
                temp_widgets.extend([
                    FluentProgressRing(),
                    FluentMaskedLineEdit(),
                    FluentCard(),
                    FluentStatusIndicator("info")
                ])
            
            # Process events
            QApplication.processEvents()
            
            # Destroy components
            for widget in temp_widgets:
                if hasattr(widget, 'close'):
                    widget.close()
            
            # Force garbage collection
            del temp_widgets
            gc.collect()
        
        self.measure_performance("Memory Stress Test", create_and_destroy_components, 5)
    
    def run_all_benchmarks(self) -> Dict[str, BenchmarkResult]:
        """Run all performance benchmarks"""
        print("🚀 Starting Fluent UI Performance Benchmarks...\n")
        
        self.setup()
        
        try:
            print("📊 Benchmarking component creation...")
            self.benchmark_component_creation()
            self.cleanup()
            
            print("📈 Benchmarking data operations...")
            self.benchmark_data_operations()
            self.cleanup()
            
            print("🖱️ Benchmarking UI interactions...")
            self.benchmark_ui_interactions()
            self.cleanup()
            
            print("🧠 Benchmarking memory usage...")
            self.benchmark_memory_usage()
            self.cleanup()
            
        except Exception as e:
            print(f"❌ Benchmark error: {e}")
        
        return self.results
    
    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*80)
        print("🏆 FLUENT UI COMPONENT PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        
        if not self.results:
            print("❌ No benchmark results available.")
            return
        
        # Group results by category
        categories = {
            "Component Creation": [k for k in self.results.keys() if k.startswith("Create")],
            "Data Operations": [k for k in self.results.keys() if "Dataset" in k],
            "UI Interactions": [k for k in self.results.keys() if k in ["ProgressRing Updates", "Expander Toggle", "StatusIndicator Animation"]],
            "Memory Tests": [k for k in self.results.keys() if "Memory" in k]
        }
        
        for category, result_names in categories.items():
            if result_names:
                print(f"\n📋 {category}:")
                print("-" * 60)
                
                for name in result_names:
                    if name in self.results:
                        result = self.results[name]
                        print(f"  {result.get_summary()}")
                        
                        if result.has_errors():
                            print(f"    ⚠️ Errors: {len(result.errors)}")
        
        # Overall performance summary
        print(f"\n📊 Overall Performance Summary:")
        print("-" * 60)
        
        total_tests = len(self.results)
        failed_tests = sum(1 for r in self.results.values() if r.has_errors())
        passed_tests = total_tests - failed_tests
        
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        
        if passed_tests > 0:
            avg_times = [r.get_average_execution_time() * 1000 for r in self.results.values() if not r.has_errors()]
            avg_memory = [r.get_average_memory_usage() for r in self.results.values() if not r.has_errors()]
            
            if avg_times:
                print(f"  Average Execution Time: {sum(avg_times) / len(avg_times):.2f}ms")
            if avg_memory:
                print(f"  Average Memory Impact: {sum(avg_memory) / len(avg_memory):.2f}MB")
        
        # Performance recommendations
        print(f"\n💡 Performance Recommendations:")
        print("-" * 60)
        
        slow_operations = [
            (name, result) for name, result in self.results.items()
            if result.get_average_execution_time() > 0.1 and not result.has_errors()
        ]
        
        if slow_operations:
            print("  Consider optimizing these operations:")
            for name, result in slow_operations:
                print(f"    • {name}: {result.get_average_execution_time() * 1000:.2f}ms average")
        else:
            print("  ✅ All operations are performing well!")
        
        high_memory = [
            (name, result) for name, result in self.results.items()
            if result.get_average_memory_usage() > 10 and not result.has_errors()
        ]
        
        if high_memory:
            print("  Consider optimizing memory usage for:")
            for name, result in high_memory:
                print(f"    • {name}: {result.get_average_memory_usage():.1f}MB average")


def main():
    """Main entry point for performance benchmarks"""
    benchmark = PerformanceBenchmark()
    
    # Run all benchmarks
    results = benchmark.run_all_benchmarks()
    
    # Print results
    benchmark.print_results()
    
    print("\n🎯 Benchmark completed!")


if __name__ == "__main__":
    main()
