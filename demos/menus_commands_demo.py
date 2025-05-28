"""
Menus and Commands Demo

Demonstrates the advanced menu and command components including:
- FluentMenu with animations
- FluentContextMenu
- FluentCommandPalette
- FluentRibbon interface
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QTextEdit, QLabel, QScrollArea)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction, QIcon

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.command.menus import FluentMenu, FluentContextMenu, FluentCommandPalette, FluentRibbon, FluentRibbonTab
from components.basic.card import FluentCard
from components.basic.button import FluentPushButton
from components.basic.label import FluentLabel
from theme.theme_manager import theme_manager


class MenusCommandsDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menus & Commands Demo - Fluent UI")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply theme
        theme_manager.apply_theme(self)
        
        self.setup_ui()
        self.setup_command_palette()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create ribbon
        self.setup_ribbon(main_layout)
        
        # Create content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Menu demos
        self.create_menu_demos(content_layout)
        
        # Right panel - Text area with context menu
        self.create_text_area(content_layout)
        
        main_layout.addLayout(content_layout)
        
    def setup_ribbon(self, parent_layout):
        """Setup ribbon interface"""
        self.ribbon = FluentRibbon()
        
        # Home tab
        home_tab = FluentRibbonTab("Home")
        
        # File group
        home_tab.add_group("File")
        home_tab.add_command("File", "New", "Create new document", self.new_document)
        home_tab.add_command("File", "Open", "Open existing document", self.open_document)
        home_tab.add_command("File", "Save", "Save current document", self.save_document)
        home_tab.add_command("File", "Save As", "Save document with new name", self.save_as_document)
        
        # Edit group
        home_tab.add_group("Edit")
        home_tab.add_command("Edit", "Cut", "Cut selected text", self.cut_text)
        home_tab.add_command("Edit", "Copy", "Copy selected text", self.copy_text)
        home_tab.add_command("Edit", "Paste", "Paste from clipboard", self.paste_text)
        home_tab.add_command("Edit", "Undo", "Undo last action", self.undo_action)
        
        # Format group
        home_tab.add_group("Format")
        home_tab.add_command("Format", "Bold", "Make text bold", self.format_bold)
        home_tab.add_command("Format", "Italic", "Make text italic", self.format_italic)
        home_tab.add_command("Format", "Underline", "Underline text", self.format_underline)
        
        self.ribbon.add_tab(home_tab)
        
        # Insert tab
        insert_tab = FluentRibbonTab("Insert")
        
        # Media group
        insert_tab.add_group("Media")
        insert_tab.add_command("Media", "Image", "Insert image", self.insert_image)
        insert_tab.add_command("Media", "Table", "Insert table", self.insert_table)
        insert_tab.add_command("Media", "Chart", "Insert chart", self.insert_chart)
        
        # Links group
        insert_tab.add_group("Links")
        insert_tab.add_command("Links", "Hyperlink", "Insert hyperlink", self.insert_hyperlink)
        insert_tab.add_command("Links", "Bookmark", "Insert bookmark", self.insert_bookmark)
        
        self.ribbon.add_tab(insert_tab)
        
        # View tab
        view_tab = FluentRibbonTab("View")
        
        # Zoom group
        view_tab.add_group("Zoom")
        view_tab.add_command("Zoom", "Zoom In", "Increase zoom level", self.zoom_in)
        view_tab.add_command("Zoom", "Zoom Out", "Decrease zoom level", self.zoom_out)
        view_tab.add_command("Zoom", "Fit to Window", "Fit content to window", self.fit_to_window)
        
        # Layout group
        view_tab.add_group("Layout")
        view_tab.add_command("Layout", "Print Layout", "Show print layout", self.print_layout)
        view_tab.add_command("Layout", "Web Layout", "Show web layout", self.web_layout)
        view_tab.add_command("Layout", "Outline", "Show outline view", self.outline_view)
        
        self.ribbon.add_tab(view_tab)
        
        parent_layout.addWidget(self.ribbon)
        
    def create_menu_demos(self, parent_layout):
        """Create menu demonstration panels"""
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # Title
        title = FluentLabel("Menu Demos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        left_layout.addWidget(title)
        
        # Standard menu demo
        self.create_standard_menu_demo(left_layout)
        
        # Command palette demo
        self.create_command_palette_demo(left_layout)
        
        parent_layout.addWidget(left_panel)
        
    def create_standard_menu_demo(self, parent_layout):
        """Create standard menu demo"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title
        card_title = FluentLabel("Standard Menu")
        card_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        card_layout.addWidget(card_title)
        
        # Menu button
        menu_btn = FluentPushButton("Show Menu")
        
        # Create menu
        self.standard_menu = FluentMenu()
        self.standard_menu.add_action("New File", self.new_document, "Ctrl+N")
        self.standard_menu.add_action("Open File", self.open_document, "Ctrl+O")
        self.standard_menu.add_action("Save File", self.save_document, "Ctrl+S")
        self.standard_menu.add_separator()
        self.standard_menu.add_action("Cut", self.cut_text, "Ctrl+X")
        self.standard_menu.add_action("Copy", self.copy_text, "Ctrl+C")
        self.standard_menu.add_action("Paste", self.paste_text, "Ctrl+V")
        self.standard_menu.add_separator()
        self.standard_menu.add_action("Exit", self.close)
        
        menu_btn.clicked.connect(lambda: self.show_menu_at_button(menu_btn))
        card_layout.addWidget(menu_btn)
        
        parent_layout.addWidget(card)
        
    def create_command_palette_demo(self, parent_layout):
        """Create command palette demo"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title
        card_title = FluentLabel("Command Palette")
        card_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        card_layout.addWidget(card_title)
        
        # Description
        desc = FluentLabel("Press Ctrl+Shift+P or click the button below to open the command palette")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 15px;")
        card_layout.addWidget(desc)
        
        # Command palette button
        palette_btn = FluentPushButton("Open Command Palette")
        palette_btn.clicked.connect(self.show_command_palette)
        card_layout.addWidget(palette_btn)
        
        parent_layout.addWidget(card)
        
    def setup_command_palette(self):
        """Setup command palette"""
        self.command_palette = FluentCommandPalette(self)
        
        # File commands
        self.command_palette.add_command("File: New", "Create a new document", self.new_document, "file")
        self.command_palette.add_command("File: Open", "Open an existing document", self.open_document, "file")
        self.command_palette.add_command("File: Save", "Save the current document", self.save_document, "file")
        self.command_palette.add_command("File: Save As", "Save document with a new name", self.save_as_document, "file")
        
        # Edit commands
        self.command_palette.add_command("Edit: Cut", "Cut selected text", self.cut_text, "edit")
        self.command_palette.add_command("Edit: Copy", "Copy selected text", self.copy_text, "edit")
        self.command_palette.add_command("Edit: Paste", "Paste from clipboard", self.paste_text, "edit")
        self.command_palette.add_command("Edit: Undo", "Undo last action", self.undo_action, "edit")
        self.command_palette.add_command("Edit: Redo", "Redo last undone action", self.redo_action, "edit")
        
        # Format commands
        self.command_palette.add_command("Format: Bold", "Make text bold", self.format_bold, "format")
        self.command_palette.add_command("Format: Italic", "Make text italic", self.format_italic, "format")
        self.command_palette.add_command("Format: Underline", "Underline text", self.format_underline, "format")
        
        # View commands
        self.command_palette.add_command("View: Zoom In", "Increase zoom level", self.zoom_in, "view")
        self.command_palette.add_command("View: Zoom Out", "Decrease zoom level", self.zoom_out, "view")
        self.command_palette.add_command("View: Fit to Window", "Fit content to window", self.fit_to_window, "view")
        
        # Application commands
        self.command_palette.add_command("Application: About", "Show about dialog", self.show_about, "app")
        self.command_palette.add_command("Application: Settings", "Open settings", self.open_settings, "app")
        self.command_palette.add_command("Application: Exit", "Exit application", self.close, "app")
        
    def create_text_area(self, parent_layout):
        """Create text area with context menu"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        
        # Title
        title = FluentLabel("Text Editor (Right-click for context menu)")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(title)
        
        # Text area
        self.text_area = QTextEdit()
        self.text_area.setPlainText("This is a demo text area.\n\nRight-click anywhere to show the context menu.\n\nYou can also use the ribbon commands above or the command palette (Ctrl+Shift+P) to perform actions.")
        self.text_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_area.customContextMenuRequested.connect(self.show_context_menu)
        right_layout.addWidget(self.text_area)
        
        parent_layout.addWidget(right_panel)
        
    def show_menu_at_button(self, button):
        """Show menu at button position"""
        pos = button.mapToGlobal(QPoint(0, button.height()))
        self.standard_menu.exec(pos)
        
    def show_context_menu(self, position):
        """Show context menu at cursor position"""
        global_pos = self.text_area.mapToGlobal(position)
        
        context_menu = FluentContextMenu(self.text_area)
        context_menu.add_action("Cut", self.cut_text, "Ctrl+X")
        context_menu.add_action("Copy", self.copy_text, "Ctrl+C")
        context_menu.add_action("Paste", self.paste_text, "Ctrl+V")
        context_menu.add_separator()
        context_menu.add_action("Select All", self.select_all, "Ctrl+A")
        context_menu.add_separator()
        context_menu.add_action("Format Bold", self.format_bold, "Ctrl+B")
        context_menu.add_action("Format Italic", self.format_italic, "Ctrl+I")
        context_menu.add_action("Format Underline", self.format_underline, "Ctrl+U")
        
        context_menu.exec(global_pos)
        
    def show_command_palette(self):
        """Show command palette"""
        self.command_palette.show_palette()
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_P and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self.show_command_palette()
        else:
            super().keyPressEvent(event)
            
    # Command handlers
    def new_document(self):
        print("New document created")
        self.text_area.clear()
        
    def open_document(self):
        print("Open document dialog would appear")
        
    def save_document(self):
        print("Document saved")
        
    def save_as_document(self):
        print("Save As dialog would appear")
        
    def cut_text(self):
        if self.text_area.textCursor().hasSelection():
            self.text_area.cut()
            print("Text cut to clipboard")
            
    def copy_text(self):
        if self.text_area.textCursor().hasSelection():
            self.text_area.copy()
            print("Text copied to clipboard")
            
    def paste_text(self):
        self.text_area.paste()
        print("Text pasted from clipboard")
        
    def select_all(self):
        self.text_area.selectAll()
        print("All text selected")
        
    def undo_action(self):
        self.text_area.undo()
        print("Action undone")
        
    def redo_action(self):
        self.text_area.redo()
        print("Action redone")
        
    def format_bold(self):
        print("Bold formatting applied")
        
    def format_italic(self):
        print("Italic formatting applied")
        
    def format_underline(self):
        print("Underline formatting applied")
        
    def insert_image(self):
        print("Insert image dialog would appear")
        
    def insert_table(self):
        print("Insert table dialog would appear")
        
    def insert_chart(self):
        print("Insert chart dialog would appear")
        
    def insert_hyperlink(self):
        print("Insert hyperlink dialog would appear")
        
    def insert_bookmark(self):
        print("Insert bookmark dialog would appear")
        
    def zoom_in(self):
        print("Zoomed in")
        
    def zoom_out(self):
        print("Zoomed out")
        
    def fit_to_window(self):
        print("Fit to window")
        
    def print_layout(self):
        print("Switched to print layout")
        
    def web_layout(self):
        print("Switched to web layout")
        
    def outline_view(self):
        print("Switched to outline view")
        
    def show_about(self):
        print("About dialog would appear")
        
    def open_settings(self):
        print("Settings dialog would appear")


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Menus & Commands Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent UI")
    
    # Create and show demo window
    demo = MenusCommandsDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
