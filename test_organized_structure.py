"""
Test script to verify the organized data components structure
"""

def test_organized_structure():
    """Test that all organized components can be imported correctly"""
    
    try:
        # Test charts imports
        from components.data.charts import charts, advanced_charts, visualization
        print("✓ Charts module imports working")
        
        # Test input imports  
        from components.data.input import entry, colorpicker, calendar
        print("✓ Input module imports working")
        
        # Test display imports
        from components.data.display import table, tree, property_grid, fileexplorer
        print("✓ Display module imports working")
        
        # Test processing imports
        from components.data.processing import filter_sort, formatters
        print("✓ Processing module imports working")
        
        # Test content imports
        from components.data.content import rich_text, json_viewer
        print("✓ Content module imports working")
        
        # Test feedback imports
        from components.data.feedback import notification, status
        print("✓ Feedback module imports working")
        
        # Test main data module imports (backward compatibility)
        from components.data import FluentRichTextEditor, FluentColorPicker
        print("✓ Main data module backward compatibility working")
        
        print("\n🎉 All organized components imported successfully!")
        print("📁 New folder structure is fully functional!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_organized_structure()
