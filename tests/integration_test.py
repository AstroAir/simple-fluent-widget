#!/usr/bin/env python3
"""
Integration Tests for Fluent UI Components

This module contains comprehensive integration tests for all Fluent UI components
to ensure they work correctly together and follow consistent patterns.
"""

import sys
import os
import unittest
from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

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
    from core.theme import FluentThemeManager
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import all components: {e}")
    COMPONENTS_AVAILABLE = False


class ComponentIntegrationTest(unittest.TestCase):
    """Integration tests for Fluent UI components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        
        cls.theme_manager = FluentThemeManager()
    
    def setUp(self):
        """Set up each test"""
        self.widgets = []
    
    def tearDown(self):
        """Clean up after each test"""
        for widget in self.widgets:
            if widget and hasattr(widget, 'close'):
                widget.close()
        QApplication.processEvents()
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_data_visualization_components(self):
        """Test data visualization components"""
        # Test Progress Ring
        progress_ring = FluentProgressRing()
        self.widgets.append(progress_ring)
        
        progress_ring.setValue(50)
        self.assertEqual(progress_ring.getValue(), 50)
        
        progress_ring.setText("50%")
        self.assertEqual(progress_ring.getText(), "50%")
        
        # Test Bar Chart
        bar_chart = FluentBarChart()
        self.widgets.append(bar_chart)
        
        test_data = [
            {"label": "A", "value": 10, "color": "#0078d4"},
            {"label": "B", "value": 20, "color": "#106ebe"}
        ]
        bar_chart.setData(test_data)
        self.assertEqual(len(bar_chart.getData()), 2)
        
        # Test Line Chart
        line_chart = FluentLineChart()
        self.widgets.append(line_chart)
        
        test_points = [{"x": 1, "y": 10}, {"x": 2, "y": 20}]
        line_chart.setData(test_points)
        self.assertEqual(len(line_chart.getData()), 2)
        
        # Test Pie Chart
        pie_chart = FluentPieChart()
        self.widgets.append(pie_chart)
        
        pie_data = [
            {"label": "A", "value": 30, "color": "#0078d4"},
            {"label": "B", "value": 70, "color": "#106ebe"}
        ]
        pie_chart.setData(pie_data)
        self.assertEqual(len(pie_chart.getData()), 2)
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_data_entry_components(self):
        """Test data entry components"""
        # Test Masked Line Edit
        masked_edit = FluentMaskedLineEdit()
        self.widgets.append(masked_edit)
        
        masked_edit.setMask("###-###-####")
        self.assertEqual(masked_edit.getMask(), "###-###-####")
        
        # Test Auto Complete Edit
        auto_complete = FluentAutoCompleteEdit()
        self.widgets.append(auto_complete)
        
        suggestions = ["Python", "JavaScript", "TypeScript"]
        auto_complete.setSuggestions(suggestions)
        self.assertEqual(auto_complete.getSuggestions(), suggestions)
        
        # Test Rich Text Editor
        rich_editor = FluentRichTextEditor()
        self.widgets.append(rich_editor)
        
        test_text = "Test content"
        rich_editor.setPlainText(test_text)
        self.assertEqual(rich_editor.toPlainText(), test_text)
        
        # Test Date Time Picker
        datetime_picker = FluentDateTimePicker()
        self.widgets.append(datetime_picker)
        
        self.assertIsNotNone(datetime_picker.getDateTime())
        
        # Test Slider
        slider = FluentSlider(Qt.Horizontal)
        self.widgets.append(slider)
        
        slider.setRange(0, 100)
        slider.setValue(50)
        self.assertEqual(slider.value(), 50)
        
        # Test File Selector
        file_selector = FluentFileSelector()
        self.widgets.append(file_selector)
        
        file_types = ["*.txt", "*.py"]
        file_selector.setAcceptedTypes(file_types)
        self.assertEqual(file_selector.getAcceptedTypes(), file_types)
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_status_notification_components(self):
        """Test status and notification components"""
        # Test Status Indicator
        status_indicator = FluentStatusIndicator("success")
        self.widgets.append(status_indicator)
        
        status_indicator.setText("Success")
        self.assertEqual(status_indicator.getText(), "Success")
        
        status_indicator.setAnimated(True)
        self.assertTrue(status_indicator.isAnimated())
        
        # Test Progress Tracker
        progress_tracker = FluentProgressTracker()
        self.widgets.append(progress_tracker)
        
        steps = ["Step 1", "Step 2", "Step 3"]
        progress_tracker.setSteps(steps)
        self.assertEqual(progress_tracker.getSteps(), steps)
        
        progress_tracker.setCurrentStep(1)
        self.assertEqual(progress_tracker.getCurrentStep(), 1)
        
        # Test Notification
        notification = FluentNotification("info")
        self.widgets.append(notification)
        
        notification.setTitle("Test Title")
        notification.setMessage("Test Message")
        self.assertEqual(notification.getTitle(), "Test Title")
        self.assertEqual(notification.getMessage(), "Test Message")
        
        # Test Badge
        badge = FluentBadge()
        self.widgets.append(badge)
        
        badge.setText("Badge")
        badge.setCount(5)
        self.assertEqual(badge.getText(), "Badge")
        self.assertEqual(badge.getCount(), 5)
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_layout_container_components(self):
        """Test layout and container components"""
        # Test Card
        card = FluentCard()
        self.widgets.append(card)
        
        card.setTitle("Test Card")
        card.setContent("Test Content")
        self.assertEqual(card.getTitle(), "Test Card")
        self.assertEqual(card.getContent(), "Test Content")
        
        card.setClickable(True)
        self.assertTrue(card.isClickable())
        
        # Test Expander
        expander = FluentExpander()
        self.widgets.append(expander)
        
        expander.setTitle("Test Expander")
        self.assertEqual(expander.getTitle(), "Test Expander")
        
        expander.setExpanded(True)
        self.assertTrue(expander.isExpanded())
        
        # Test Splitter
        splitter = FluentSplitter(Qt.Horizontal)
        self.widgets.append(splitter)
        
        widget1 = QWidget()
        widget2 = QWidget()
        splitter.addWidget(widget1)
        splitter.addWidget(widget2)
        self.assertEqual(splitter.count(), 2)
        
        # Test Info Bar
        info_bar = FluentInfoBar("info")
        self.widgets.append(info_bar)
        
        info_bar.setTitle("Test Title")
        info_bar.setMessage("Test Message")
        self.assertEqual(info_bar.getTitle(), "Test Title")
        self.assertEqual(info_bar.getMessage(), "Test Message")
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_media_content_components(self):
        """Test media and content components"""
        # Test Image Viewer
        image_viewer = FluentImageViewer()
        self.widgets.append(image_viewer)
        
        self.assertIsNotNone(image_viewer.getZoomLevel())
        
        # Test Rich Content Viewer
        content_viewer = FluentRichContentViewer()
        self.widgets.append(content_viewer)
        
        test_content = "<h1>Test</h1>"
        content_viewer.setContent(test_content, "html")
        self.assertEqual(content_viewer.getContent(), test_content)
        
        # Test Thumbnail Gallery
        thumbnail_gallery = FluentThumbnailGallery()
        self.widgets.append(thumbnail_gallery)
        
        thumbnail_gallery.setThumbnailSize(128, 128)
        size = thumbnail_gallery.getThumbnailSize()
        self.assertEqual(size.width(), 128)
        self.assertEqual(size.height(), 128)
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_command_interface_components(self):
        """Test command interface components"""
        # Test Command Bar
        command_bar = FluentCommandBar()
        self.widgets.append(command_bar)
        
        command_bar.addPrimaryCommand("test", "Test", "Test command")
        commands = command_bar.getPrimaryCommands()
        self.assertTrue(len(commands) > 0)
        
        # Test Toolbar
        toolbar = FluentToolbar()
        self.widgets.append(toolbar)
        
        toolbar.addAction("test", "Test", "Test action")
        actions = toolbar.getActions()
        self.assertTrue(len(actions) > 0)
        
        # Test Quick Access Toolbar
        quick_access = FluentQuickAccessToolbar()
        self.widgets.append(quick_access)
        
        quick_access.addAction("test", "Test", "Test action")
        actions = quick_access.getActions()
        self.assertTrue(len(actions) > 0)
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_theme_integration(self):
        """Test theme integration across components"""
        # Create various components
        components = [
            FluentProgressRing(),
            FluentMaskedLineEdit(),
            FluentStatusIndicator("info"),
            FluentCard(),
            FluentImageViewer(),
            FluentCommandBar()
        ]
        
        self.widgets.extend(components)
        
        # Test theme application
        for component in components:
            # All components should have theme integration
            self.assertTrue(hasattr(component, 'theme_manager'))
            self.assertIsNotNone(component.theme_manager)
            
            # Theme should be properly applied
            if hasattr(component, 'apply_theme'):
                component.apply_theme()
    
    def test_component_consistency(self):
        """Test consistency across all components"""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        # Define expected interface patterns
        expected_methods = ['show', 'hide', 'setVisible', 'isVisible']
        
        # Test each component category
        component_classes = [
            FluentProgressRing, FluentBarChart, FluentLineChart, FluentPieChart,
            FluentMaskedLineEdit, FluentAutoCompleteEdit, FluentRichTextEditor,
            FluentStatusIndicator, FluentProgressTracker, FluentBadge,
            FluentCard, FluentExpander, FluentInfoBar,
            FluentImageViewer, FluentRichContentViewer,
            FluentCommandBar, FluentToolbar
        ]
        
        for component_class in component_classes:
            component = component_class()
            self.widgets.append(component)
            
            # Test basic widget interface
            for method in expected_methods:
                self.assertTrue(hasattr(component, method),
                              f"{component_class.__name__} missing {method}")


class PerformanceTest(unittest.TestCase):
    """Performance tests for Fluent UI components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up each test"""
        self.widgets = []
    
    def tearDown(self):
        """Clean up after each test"""
        for widget in self.widgets:
            if widget and hasattr(widget, 'close'):
                widget.close()
        QApplication.processEvents()
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_component_creation_performance(self):
        """Test component creation performance"""
        import time
        
        # Test creation time for various components
        component_classes = [
            FluentProgressRing, FluentBarChart, FluentMaskedLineEdit,
            FluentStatusIndicator, FluentCard, FluentImageViewer,
            FluentCommandBar
        ]
        
        creation_times = {}
        
        for component_class in component_classes:
            start_time = time.time()
            
            # Create multiple instances
            for _ in range(10):
                component = component_class()
                self.widgets.append(component)
            
            end_time = time.time()
            creation_times[component_class.__name__] = end_time - start_time
        
        # Verify all components can be created reasonably quickly
        for class_name, creation_time in creation_times.items():
            self.assertLess(creation_time, 1.0,  # Should create 10 instances in under 1 second
                          f"{class_name} creation took too long: {creation_time:.3f}s")
    
    @unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
    def test_large_dataset_performance(self):
        """Test component performance with large datasets"""
        # Test Tree Widget with many items
        tree_widget = FluentTreeWidget()
        self.widgets.append(tree_widget)
        
        # Add many items (simulate large dataset)
        for i in range(100):
            tree_widget.addTopLevelItem(tree_widget.createItem([f"Item {i}"]))
        
        # Should handle large datasets without significant delay
        QApplication.processEvents()
        
        # Test Bar Chart with many data points
        bar_chart = FluentBarChart()
        self.widgets.append(bar_chart)
        
        large_dataset = [
            {"label": f"Item {i}", "value": i * 10, "color": "#0078d4"}
            for i in range(50)
        ]
        bar_chart.setData(large_dataset)
        
        QApplication.processEvents()


def run_integration_tests():
    """Run all integration tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(ComponentIntegrationTest))
    suite.addTest(unittest.makeSuite(PerformanceTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Initialize QApplication for testing
    if not QApplication.instance():
        app = QApplication(sys.argv)
    
    # Run the tests
    success = run_integration_tests()
    
    if success:
        print("\n✅ All integration tests passed!")
    else:
        print("\n❌ Some integration tests failed!")
        sys.exit(1)
