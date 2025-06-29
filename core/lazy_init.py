"""
Lazy Initialization Helper for Fluent Components

This module provides utilities to delay Qt widget initialization until
QApplication is available, preventing the "Must construct a QApplication before a QWidget" error.
"""

from typing import Optional, Callable, Any
from PySide6.QtWidgets import QApplication


def require_qapp(func: Callable) -> Callable:
    """
    Decorator to ensure QApplication exists before calling function
    
    This decorator checks if QApplication is available and delays execution
    if needed, or raises a helpful error message.
    """
    def wrapper(*args, **kwargs):
        app = QApplication.instance()
        if app is None:
            raise RuntimeError(
                "QApplication must be created before using Fluent components. "
                "Please create QApplication first:\n"
                "app = QApplication(sys.argv)\n"
                "# Then create your components"
            )
        return func(*args, **kwargs)
    return wrapper


def is_qapp_available() -> bool:
    """Check if QApplication is available"""
    return QApplication.instance() is not None


class LazyProperty:
    """
    Lazy property descriptor that delays initialization until first access
    and QApplication is available
    """
    
    def __init__(self, initializer: Callable[[], Any]):
        self.initializer = initializer
        self.value = None
        self.initialized = False
    
    def __get__(self, obj, objtype=None):
        if not self.initialized:
            if not is_qapp_available():
                raise RuntimeError(
                    "QApplication must be created before accessing this property. "
                    "Please create QApplication first."
                )
            self.value = self.initializer()
            self.initialized = True
        return self.value
    
    def __set__(self, obj, value):
        self.value = value
        self.initialized = True


class LazyThemeManager:
    """
    Lazy wrapper for theme manager that delays initialization
    """
    
    def __init__(self):
        self._manager = None
    
    @property
    def manager(self):
        if self._manager is None:
            if not is_qapp_available():
                # Return a mock manager for import time
                return self._create_mock_manager()
            from .theme import FluentTheme
            self._manager = FluentTheme()
        return self._manager
    
    def _create_mock_manager(self):
        """Create a mock manager that can be safely imported"""
        class MockThemeManager:
            def __init__(self):
                # Create a mock signal that does nothing
                self.theme_changed = type('MockSignal', (), {
                    'connect': lambda self, *args: None,
                    'disconnect': lambda self, *args: None,
                    'emit': lambda self, *args: None
                })()
            
            def __getattr__(self, name):
                # Return safe defaults or lazy properties
                if name == 'current_theme':
                    return 'light'
                return lambda *args, **kwargs: None
        
        return MockThemeManager()
    
    def __getattr__(self, name):
        return getattr(self.manager, name)


# Global lazy theme manager instance
_lazy_theme_manager = LazyThemeManager()


def get_theme_manager():
    """Get the theme manager instance (lazy initialization)"""
    return _lazy_theme_manager


def safe_import_check():
    """
    Check if it's safe to import Qt widgets
    Returns True if QApplication exists, False otherwise
    """
    return is_qapp_available()
