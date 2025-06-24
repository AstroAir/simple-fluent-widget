#!/usr/bin/env python3
"""
Script to fix all type errors in the fileexplorer_fixed.py file
"""

def fix_fileexplorer():
    """Fix all type errors in the file explorer"""
    
    # Read the original file
    with open('d:/Project/simple-fluent-widget/components/data/fileexplorer_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Replace all instances of self._model.filePath(index) with proper helper method
    fixed_content = content.replace(
        'self._model.filePath(index)',
        'self._get_file_path(index)'
    )
    
    # Fix 2: Fix the setCurrentPath issue
    fixed_content = fixed_content.replace(
        'QTimer.singleShot(50, lambda: self.sidebar.setCurrentPath(self._state.current_path))',
        'QTimer.singleShot(50, lambda: getattr(self.sidebar, "setCurrentPath", lambda x: None)(self._state.current_path))'
    )
    
    # Fix 3: Fix the setModel method signature
    fixed_content = fixed_content.replace(
        'def setModel(self, model: QFileSystemModel) -> None:',
        'def setModel(self, model) -> None:'
    )
    
    # Fix 4: Ensure all filePath method calls are properly handled
    old_pattern = '''if self._model and hasattr(self._model, 'filePath'):
            try:
                file_path = self._get_file_path(index)
                self.fileSelected.emit(file_path)
            except Exception:
                pass'''
    
    new_pattern = '''file_path = self._get_file_path(index)
        if file_path:
            self.fileSelected.emit(file_path)'''
    
    fixed_content = fixed_content.replace(old_pattern, new_pattern)
    
    # Similar for fileActivated
    old_pattern2 = '''if self._model and hasattr(self._model, 'filePath'):
            try:
                file_path = self._get_file_path(index)
                self.fileActivated.emit(file_path)
            except Exception:
                pass'''
    
    new_pattern2 = '''file_path = self._get_file_path(index)
        if file_path:
            self.fileActivated.emit(file_path)'''
    
    fixed_content = fixed_content.replace(old_pattern2, new_pattern2)
    
    # Write the fixed content
    with open('d:/Project/simple-fluent-widget/components/data/fileexplorer_final.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("File explorer fixed and saved as fileexplorer_final.py")

if __name__ == "__main__":
    fix_fileexplorer()
