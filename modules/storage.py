"""
Data Storage and Management Module

This module handles all database operations for the personal finance tool,
including SQLite database management, transaction storage, and data retrieval.

Designed for beginners with clear documentation and error handling.
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages SQLite database operations for the personal finance tool.
    
    This class handles:
    - Database initialization and schema creation
    - Transaction storage and retrieval
    - Category management
    - User preferences storage
    - Data validation and cleaning
    """
    
    def __init__(self, db_path: str = "data/finance_tool.db"):
        """
        Initialize database manager with specified database path.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Database manager initialized with database: {db_path}")
    
    def _init_database(self):
        """
        Initialize database with required tables and schema.
        
        Creates tables for:
        - transactions: Main transaction data
        - categories: Transaction categories
        - user_preferences: User settings and preferences
        - csv_mappings: Saved CSV column mappings
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create transactions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT DEFAULT 'Uncategorized',
                        subcategory TEXT,
                        balance REAL,
                        reference TEXT,
                        is_recurring BOOLEAN DEFAULT FALSE,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create categories table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        parent_category TEXT,
                        color TEXT DEFAULT '#3498db',
                        icon TEXT DEFAULT '📦',
                        budget_limit REAL,
                        is_income BOOLEAN DEFAULT FALSE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create user preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create CSV mappings table for saved configurations
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS csv_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        bank_name TEXT,
                        date_column TEXT NOT NULL,
                        amount_column TEXT NOT NULL,
                        description_column TEXT NOT NULL,
                        balance_column TEXT,
                        reference_column TEXT,
                        date_format TEXT DEFAULT '%Y-%m-%d',
                        amount_format TEXT DEFAULT 'decimal',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount)")
                
                conn.commit()
                
                # Initialize default categories if table is empty
                self._init_default_categories(cursor)
                conn.commit()
                
                logger.info("Database schema initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _init_default_categories(self, cursor):
        """
        Initialize default transaction categories if none exist.
        
        Args:
            cursor: SQLite cursor object
        """
        # Check if categories already exist
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            return  # Categories already exist
        
        # Default categories based on common spending patterns
        default_categories = [
            # Income categories
            ("Salary", None, "#27ae60", "💰", None, True, "Regular salary and wages"),
            ("Freelance", None, "#2ecc71", "💼", None, True, "Freelance and contract work"),
            ("Investment Returns", None, "#16a085", "📈", None, True, "Dividends, interest, capital gains"),
            ("Other Income", None, "#1abc9c", "💵", None, True, "Other income sources"),
            
            # Expense categories
            ("Housing", None, "#e74c3c", "🏠", None, False, "Rent, mortgage, utilities"),
            ("Transportation", None, "#e67e22", "🚗", None, False, "Gas, public transport, car maintenance"),
            ("Food & Dining", None, "#f39c12", "🍽️", None, False, "Groceries, restaurants, dining out"),
            ("Shopping", None, "#9b59b6", "🛍️", None, False, "Clothing, electronics, general shopping"),
            ("Healthcare", None, "#e91e63", "🏥", None, False, "Medical expenses, insurance, medications"),
            ("Entertainment", None, "#673ab7", "🎬", None, False, "Movies, games, hobbies, subscriptions"),
            ("Bills & Utilities", None, "#607d8b", "📞", None, False, "Phone, internet, electricity, gas"),
            ("Insurance", None, "#795548", "🛡️", None, False, "Life, health, car, home insurance"),
            ("Banking & Finance", None, "#455a64", "🏦", None, False, "Bank fees, loan payments, transfers"),
            ("Education", None, "#ff9800", "📚", None, False, "Tuition, books, courses, training"),
            ("Travel", None, "#4caf50", "✈️", None, False, "Flights, hotels, vacation expenses"),
            ("Personal Care", None, "#ff5722", "💄", None, False, "Haircuts, beauty, personal items"),
            ("Gifts & Donations", None, "#009688", "🎁", None, False, "Gifts, charity, donations"),
            ("Other Expenses", None, "#9e9e9e", "📦", None, False, "Miscellaneous expenses"),
        ]
        
        for category_data in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories 
                (name, parent_category, color, icon, budget_limit, is_income, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, category_data)
        
        logger.info("Default categories initialized")
    
    def save_transactions(self, transactions_df: pd.DataFrame) -> int:
        """
        Save transactions to database with data validation.
        
        Args:
            transactions_df (pd.DataFrame): DataFrame containing transaction data
            
        Returns:
            int: Number of transactions saved
            
        Raises:
            ValueError: If required columns are missing
            sqlite3.Error: If database operation fails
        """
        required_columns = ['date', 'amount', 'description']
        missing_columns = [col for col in required_columns if col not in transactions_df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Prepare data for insertion
        df = transactions_df.copy()
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        # Add default values for optional columns
        if 'category' not in df.columns:
            df['category'] = 'Uncategorized'
        if 'subcategory' not in df.columns:
            df['subcategory'] = None
        if 'balance' not in df.columns:
            df['balance'] = None
        if 'reference' not in df.columns:
            df['reference'] = None
        if 'is_recurring' not in df.columns:
            df['is_recurring'] = False
        if 'notes' not in df.columns:
            df['notes'] = None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert transactions, avoiding duplicates
                cursor = conn.cursor()
                saved_count = 0
                
                for _, row in df.iterrows():
                    # Check for duplicate (same date, amount, description)
                    cursor.execute("""
                        SELECT COUNT(*) FROM transactions 
                        WHERE date = ? AND amount = ? AND description = ?
                    """, (row['date'].strftime('%Y-%m-%d'), row['amount'], row['description']))
                    
                    if cursor.fetchone()[0] == 0:  # No duplicate found
                        cursor.execute("""
                            INSERT INTO transactions 
                            (date, amount, description, category, subcategory, balance, reference, is_recurring, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row['date'].strftime('%Y-%m-%d'),
                            row['amount'],
                            row['description'],
                            row['category'],
                            row['subcategory'],
                            row['balance'],
                            row['reference'],
                            row['is_recurring'],
                            row['notes']
                        ))
                        saved_count += 1
                
                conn.commit()
                logger.info(f"Saved {saved_count} new transactions to database")
                return saved_count
                
        except sqlite3.Error as e:
            logger.error(f"Error saving transactions: {e}")
            raise
    
    def get_all_transactions(self, start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Retrieve all transactions from database with optional date filtering.
        
        Args:
            start_date (Optional[datetime]): Start date for filtering
            end_date (Optional[datetime]): End date for filtering
            
        Returns:
            pd.DataFrame: DataFrame containing transaction data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM transactions"
                params = []
                
                # Add date filtering if provided
                if start_date or end_date:
                    conditions = []
                    if start_date:
                        conditions.append("date >= ?")
                        params.append(start_date.strftime('%Y-%m-%d'))
                    if end_date:
                        conditions.append("date <= ?")
                        params.append(end_date.strftime('%Y-%m-%d'))
                    
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY date DESC"
                
                df = pd.read_sql_query(query, conn, params=params)
                
                # Convert date column to datetime
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                
                return df
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving transactions: {e}")
            return pd.DataFrame()
    
    def get_transaction_count(self) -> int:
        """
        Get total number of transactions in database.
        
        Returns:
            int: Total number of transactions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM transactions")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Error getting transaction count: {e}")
            return 0
    
    def get_category_count(self) -> int:
        """
        Get total number of categories in database.
        
        Returns:
            int: Total number of categories
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM categories")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Error getting category count: {e}")
            return 0
    
    def get_date_range(self) -> Optional[Dict]:
        """
        Get the date range of transactions in database.
        
        Returns:
            Optional[Dict]: Dictionary with min_date, max_date, and days count
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
                result = cursor.fetchone()
                
                if result[0] and result[1]:
                    min_date = datetime.strptime(result[0], '%Y-%m-%d')
                    max_date = datetime.strptime(result[1], '%Y-%m-%d')
                    days = (max_date - min_date).days + 1
                    
                    return {
                        'min_date': min_date,
                        'max_date': max_date,
                        'days': days
                    }
                
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error getting date range: {e}")
            return None
    
    def get_categories(self, include_income: bool = True) -> pd.DataFrame:
        """
        Retrieve all categories from database.
        
        Args:
            include_income (bool): Whether to include income categories
            
        Returns:
            pd.DataFrame: DataFrame containing category data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM categories"
                if not include_income:
                    query += " WHERE is_income = FALSE"
                query += " ORDER BY is_income DESC, name ASC"
                
                return pd.read_sql_query(query, conn)
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving categories: {e}")
            return pd.DataFrame()
    
    def save_csv_mapping(self, mapping_name: str, bank_name: str, 
                        column_mapping: Dict[str, str]) -> bool:
        """
        Save CSV column mapping for reuse.
        
        Args:
            mapping_name (str): Name for this mapping configuration
            bank_name (str): Bank or institution name
            column_mapping (Dict[str, str]): Column mapping configuration
            
        Returns:
            bool: True if saved successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO csv_mappings 
                    (name, bank_name, date_column, amount_column, description_column, 
                     balance_column, reference_column)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    mapping_name,
                    bank_name,
                    column_mapping.get('date'),
                    column_mapping.get('amount'),
                    column_mapping.get('description'),
                    column_mapping.get('balance'),
                    column_mapping.get('reference')
                ))
                conn.commit()
                logger.info(f"Saved CSV mapping: {mapping_name}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error saving CSV mapping: {e}")
            return False
    
    def get_csv_mappings(self) -> pd.DataFrame:
        """
        Retrieve saved CSV mappings.
        
        Returns:
            pd.DataFrame: DataFrame containing saved CSV mappings
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query("SELECT * FROM csv_mappings ORDER BY name", conn)
        except sqlite3.Error as e:
            logger.error(f"Error retrieving CSV mappings: {e}")
            return pd.DataFrame()
    
    def update_transaction_category(self, transaction_id: int, category: str, 
                                   subcategory: Optional[str] = None) -> bool:
        """
        Update the category of a specific transaction.
        
        Args:
            transaction_id (int): ID of transaction to update
            category (str): New category name
            subcategory (Optional[str]): New subcategory name
            
        Returns:
            bool: True if updated successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE transactions 
                    SET category = ?, subcategory = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (category, subcategory, transaction_id))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Updated transaction {transaction_id} category to {category}")
                    return True
                else:
                    logger.warning(f"No transaction found with ID {transaction_id}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Error updating transaction category: {e}")
            return False
    
    def close(self):
        """
        Close database connection if needed.
        Note: We use context managers, so this is mainly for cleanup.
        """
        logger.info("Database manager closed")