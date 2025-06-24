#!/usr/bin/env python3
"""Simple test to check calendar import"""

import sys
from PySide6.QtWidgets import QApplication

# Create QApplication first
app = QApplication(sys.argv)

try:
    from components.data.calendar import OptimizedFluentCalendar
    print("✓ Calendar import successful")
    
    # Test creating a calendar instance
    calendar = OptimizedFluentCalendar()
    print("✓ Calendar instantiation successful")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed")
