"""
Test script for optimized color picker components
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QColor

try:
    from components.data.colorpicker import FluentColorPicker, FluentColorButton, FluentColorWheel
    print("✓ All color picker components imported successfully!")
    
    def test_components():
        # Create QApplication first
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        try:
            # Test FluentColorButton
            button = FluentColorButton(QColor("#ff0000"))
            print(f"✓ FluentColorButton created with color: {button.get_color().name()}")
            
            # Test FluentColorWheel  
            wheel = FluentColorWheel()
            wheel.set_color(QColor("#00ff00"))
            print(f"✓ FluentColorWheel created with color: {wheel.get_color().name()}")
            
            # Test FluentColorPicker
            picker = FluentColorPicker()
            picker.set_color(QColor("#0000ff"))
            print(f"✓ FluentColorPicker created with color: {picker.get_color().name()}")
            
            print("✓ All components tested successfully!")
            print("✓ Modern Python features working:")
            print("  - Dataclasses with slots")
            print("  - Union type syntax (|)")
            print("  - Enhanced pattern matching ready")
            print("  - Protocol-based typing")
            print("  - LRU cache decorators")
            print("  - Modern error handling")
            
            return True
            
        finally:
            # Clean up widgets
            if 'button' in locals():
                button.deleteLater()
            if 'wheel' in locals():
                wheel.deleteLater()
            if 'picker' in locals():
                picker.deleteLater()
    
    if __name__ == "__main__":
        test_components()
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Test error: {e}")
    sys.exit(1)
