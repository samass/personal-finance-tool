"""
Basic tests for the personal finance tool modules.

These tests verify that the core functionality works as expected.
Run with: python tests/test_basic_functionality.py
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from storage import DatabaseManager
from csv_processor import CSVProcessor
from categorization import TransactionCategorizer
from visualization import VisualizationEngine

def test_database_manager_initialization():
    """Test that database manager initializes correctly."""
    # Create a temporary database file for testing
    import tempfile
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    db_manager = DatabaseManager(db_path=db_path)
    assert db_manager is not None
    assert db_manager.get_transaction_count() == 0

def test_csv_processor_initialization():
    """Test that CSV processor initializes correctly."""
    processor = CSVProcessor()
    assert processor is not None
    assert len(processor.date_formats) > 0

def test_transaction_categorizer_initialization():
    """Test that transaction categorizer initializes correctly."""
    categorizer = TransactionCategorizer()
    assert categorizer is not None
    assert len(categorizer.merchant_patterns) > 0

def test_visualization_engine_initialization():
    """Test that visualization engine initializes correctly."""
    viz_engine = VisualizationEngine()
    assert viz_engine is not None
    assert len(viz_engine.color_palette) > 0

def test_basic_transaction_processing():
    """Test basic transaction processing workflow."""
    # Create sample data
    sample_data = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Amount': [100.0, -50.0, -25.0],
        'Description': ['Salary', 'Grocery Store', 'Coffee Shop']
    })
    
    # Test CSV processing
    processor = CSVProcessor()
    column_mapping = {
        'date': 'Date',
        'amount': 'Amount',
        'description': 'Description'
    }
    
    processed_df = processor.process_csv(sample_data, column_mapping)
    
    assert len(processed_df) == 3
    assert 'date' in processed_df.columns
    assert 'amount' in processed_df.columns
    assert 'description' in processed_df.columns

def test_categorization():
    """Test transaction categorization."""
    categorizer = TransactionCategorizer()
    
    # Test income categorization
    result = categorizer.categorize_transaction("Salary Payment", 2500.0)
    assert result['is_income'] == True
    assert result['confidence'] > 0
    
    # Test expense categorization
    result = categorizer.categorize_transaction("Amazon Purchase", -150.0)
    assert result['is_income'] == False
    assert result['confidence'] > 0

if __name__ == "__main__":
    # Run tests directly
    test_database_manager_initialization()
    test_csv_processor_initialization() 
    test_transaction_categorizer_initialization()
    test_visualization_engine_initialization()
    test_basic_transaction_processing()
    test_categorization()
    print("✅ All tests passed!")