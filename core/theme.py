"""
Fluent Design主题管理系统
支持亮色/暗色主题切换和自定义主题色
"""

from typing import Dict, Any, Optional
from enum import Enum
from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtGui import QColor, QPalette


class ThemeMode(Enum):
    """主题模式枚举"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class FluentTheme(QObject):
    """**Fluent Design主题管理器**"""
    
    # 主题改变信号
    theme_changed = Signal(str)  # theme_name
    mode_changed = Signal(ThemeMode)  # theme_mode
    
    def __init__(self):
        super().__init__()
        self._current_mode = ThemeMode.LIGHT
        self._current_theme = "default"
        self._custom_colors = {}
        self.settings = QSettings("FluentUI", "Theme")
        
        # **定义Fluent Design调色板**
        self._light_palette = {
            "primary": QColor("#0078d4"),
            "secondary": QColor("#106ebe"),
            "surface": QColor("#ffffff"),
            "background": QColor("#f3f2f1"),
            "card": QColor("#ffffff"),
            "border": QColor("#d1d1d1"),
            "text_primary": QColor("#323130"),
            "text_secondary": QColor("#605e5c"),
            "text_disabled": QColor("#a19f9d"),
            "accent_light": QColor("#deecf9"),
            "accent_medium": QColor("#c7e0f4"),
            "accent_dark": QColor("#004578"),
        }
        
        self._dark_palette = {
            "primary": QColor("#60cdff"),
            "secondary": QColor("#0078d4"),
            "surface": QColor("#2d2d30"),
            "background": QColor("#1e1e1e"),
            "card": QColor("#252526"),
            "border": QColor("#3e3e42"),
            "text_primary": QColor("#ffffff"),
            "text_secondary": QColor("#cccccc"),
            "text_disabled": QColor("#808080"),
            "accent_light": QColor("#0d2240"),
            "accent_medium": QColor("#1a3a5c"),
            "accent_dark": QColor("#60cdff"),
        }
        
        self.load_settings()
    
    def get_color(self, color_name: str) -> QColor:
        """**获取当前主题的颜色**"""
        if color_name in self._custom_colors:
            return self._custom_colors[color_name]
        
        palette = (self._light_palette if self._current_mode == ThemeMode.LIGHT 
                  else self._dark_palette)
        return palette.get(color_name, QColor("#000000"))
    
    def set_theme_mode(self, mode: ThemeMode):
        """**设置主题模式**"""
        if self._current_mode != mode:
            self._current_mode = mode
            self.save_settings()
            self.mode_changed.emit(mode)
            self.theme_changed.emit(self._current_theme)
    
    def set_custom_color(self, color_name: str, color: QColor):
        """**设置自定义颜色**"""
        self._custom_colors[color_name] = color
        self.theme_changed.emit(self._current_theme)
    
    def get_style_sheet(self, component_type: str) -> str:
        """**获取组件样式表**"""
        return self._generate_component_style(component_type)
    
    def _generate_component_style(self, component_type: str) -> str:
        """生成组件样式"""
        colors = {
            "primary": self.get_color("primary").name(),
            "surface": self.get_color("surface").name(),
            "background": self.get_color("background").name(),
            "border": self.get_color("border").name(),
            "text_primary": self.get_color("text_primary").name(),
            "text_secondary": self.get_color("text_secondary").name(),
        }
        
        # 根据组件类型返回对应的CSS样式
        return self._get_component_css(component_type, colors)
    
    def _get_component_css(self, component_type: str, colors: Dict[str, str]) -> str:
        """获取组件CSS样式"""
        styles = {
            "button": f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background-color: {colors['primary']}CC;
                }}
                QPushButton:pressed {{
                    background-color: {colors['primary']}AA;
                }}
                QPushButton:disabled {{
                    background-color: {colors['border']};
                    color: {colors['text_secondary']};
                }}
            """,
            "textbox": f"""
                QLineEdit {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: {colors['text_primary']};
                }}
                QLineEdit:focus {{
                    border-color: {colors['primary']};
                    border-width: 2px;
                }}
            """
        }
        return styles.get(component_type, "")
    
    def save_settings(self):
        """**保存主题设置**"""
        self.settings.setValue("theme_mode", self._current_mode.value)
        self.settings.setValue("current_theme", self._current_theme)
    
    def load_settings(self):
        """**加载主题设置**"""
        mode_value = self.settings.value("theme_mode", ThemeMode.LIGHT.value)
        self._current_mode = ThemeMode(mode_value)
        self._current_theme = self.settings.value("current_theme", "default")


# 全局主题实例
theme_manager = FluentTheme()