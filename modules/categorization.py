"""
Transaction Categorization Module

This module handles automatic and manual categorization of transactions using
machine learning and rule-based approaches. It learns from user corrections
to improve categorization accuracy over time.

Designed for beginners with clear documentation and learning capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionCategorizer:
    """
    Handles transaction categorization using multiple approaches:
    - Rule-based categorization for common patterns
    - Machine learning for description analysis
    - User feedback learning
    - Regular payment detection
    """
    
    def __init__(self):
        """Initialize the categorization engine with default rules."""
        
        # Common merchant patterns and their categories
        self.merchant_patterns = {
            # Food & Dining
            'Food & Dining': [
                r'.*restaurant.*', r'.*cafe.*', r'.*coffee.*', r'.*pizza.*',
                r'.*mcdonalds.*', r'.*kfc.*', r'.*subway.*', r'.*starbucks.*',
                r'.*grocery.*', r'.*supermarket.*', r'.*tesco.*', r'.*sainsbury.*',
                r'.*asda.*', r'.*morrisons.*', r'.*waitrose.*', r'.*lidl.*', r'.*aldi.*'
            ],
            
            # Transportation
            'Transportation': [
                r'.*petrol.*', r'.*gas station.*', r'.*shell.*', r'.*bp.*', r'.*esso.*',
                r'.*uber.*', r'.*taxi.*', r'.*bus.*', r'.*train.*', r'.*parking.*',
                r'.*toll.*', r'.*tfl.*', r'.*transport.*'
            ],
            
            # Shopping
            'Shopping': [
                r'.*amazon.*', r'.*ebay.*', r'.*argos.*', r'.*currys.*',
                r'.*next.*', r'.*h&m.*', r'.*zara.*', r'.*primark.*',
                r'.*john lewis.*', r'.*marks spencer.*'
            ],
            
            # Bills & Utilities
            'Bills & Utilities': [
                r'.*electric.*', r'.*gas.*', r'.*water.*', r'.*council tax.*',
                r'.*british gas.*', r'.*eon.*', r'.*edf.*', r'.*thames water.*',
                r'.*phone.*', r'.*mobile.*', r'.*internet.*', r'.*broadband.*',
                r'.*sky.*', r'.*bt.*', r'.*virgin.*', r'.*vodafone.*', r'.*ee.*'
            ],
            
            # Banking & Finance
            'Banking & Finance': [
                r'.*bank.*fee.*', r'.*overdraft.*', r'.*interest.*', r'.*loan.*',
                r'.*mortgage.*', r'.*insurance.*', r'.*transfer.*'
            ],
            
            # Healthcare
            'Healthcare': [
                r'.*pharmacy.*', r'.*chemist.*', r'.*boots.*', r'.*hospital.*',
                r'.*doctor.*', r'.*dental.*', r'.*medical.*', r'.*health.*'
            ],
            
            # Entertainment
            'Entertainment': [
                r'.*cinema.*', r'.*netflix.*', r'.*spotify.*', r'.*gym.*',
                r'.*sports.*', r'.*game.*', r'.*book.*', r'.*music.*'
            ]
        }
        
        # Income patterns
        self.income_patterns = [
            r'.*salary.*', r'.*wage.*', r'.*payroll.*', r'.*employer.*',
            r'.*freelance.*', r'.*contract.*', r'.*dividend.*', r'.*interest.*',
            r'.*refund.*', r'.*cashback.*', r'.*transfer.*in.*'
        ]
        
        # Regular payment indicators
        self.regular_payment_patterns = [
            r'.*direct debit.*', r'.*dd.*', r'.*standing order.*', r'.*so.*',
            r'.*monthly.*', r'.*quarterly.*', r'.*annual.*'
        ]
        
        logger.info("Transaction categorizer initialized")
    
    def categorize_transaction(self, description: str, amount: float, 
                             date: datetime = None) -> Dict[str, any]:
        """
        Categorize a single transaction based on description and amount.
        
        Args:
            description (str): Transaction description
            amount (float): Transaction amount
            date (datetime, optional): Transaction date
            
        Returns:
            Dict[str, any]: Categorization result with category, confidence, and reasoning
        """
        result = {
            'category': 'Other Expenses',
            'subcategory': None,
            'confidence': 0.0,
            'reasoning': 'Default category',
            'is_income': amount > 0,
            'is_regular': False
        }
        
        # Clean description for analysis
        clean_desc = description.lower().strip()
        
        # Check if it's income
        if amount > 0:
            for pattern in self.income_patterns:
                if re.search(pattern, clean_desc):
                    if 'salary' in clean_desc or 'wage' in clean_desc:
                        result['category'] = 'Salary'
                    elif 'freelance' in clean_desc or 'contract' in clean_desc:
                        result['category'] = 'Freelance'
                    elif 'dividend' in clean_desc or 'interest' in clean_desc:
                        result['category'] = 'Investment Returns'
                    else:
                        result['category'] = 'Other Income'
                    
                    result['confidence'] = 0.8
                    result['reasoning'] = f'Matched income pattern: {pattern}'
                    break
            
            if result['category'] == 'Other Expenses':  # No income pattern matched
                result['category'] = 'Other Income'
                result['confidence'] = 0.3
                result['reasoning'] = 'Positive amount, assumed income'
        
        else:  # Expense transaction
            # Check against merchant patterns
            for category, patterns in self.merchant_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, clean_desc):
                        result['category'] = category
                        result['confidence'] = 0.7
                        result['reasoning'] = f'Matched merchant pattern: {pattern}'
                        break
                
                if result['confidence'] > 0:
                    break
        
        # Check for regular payments
        for pattern in self.regular_payment_patterns:
            if re.search(pattern, clean_desc):
                result['is_regular'] = True
                result['confidence'] = min(result['confidence'] + 0.1, 1.0)
                break
        
        return result
    
    def categorize_transactions(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize multiple transactions and return updated dataframe.
        
        Args:
            transactions_df (pd.DataFrame): DataFrame with transactions
            
        Returns:
            pd.DataFrame: Updated DataFrame with categories
        """
        logger.info(f"Categorizing {len(transactions_df)} transactions")
        
        df = transactions_df.copy()
        
        # Initialize new columns if they don't exist
        if 'category' not in df.columns:
            df['category'] = 'Uncategorized'
        if 'subcategory' not in df.columns:
            df['subcategory'] = None
        if 'confidence' not in df.columns:
            df['confidence'] = 0.0
        if 'is_regular' not in df.columns:
            df['is_regular'] = False
        
        # Categorize each transaction
        for idx, row in df.iterrows():
            # Only categorize if not already categorized or low confidence
            if row['category'] in ['Uncategorized', 'Other Expenses'] or row['confidence'] < 0.5:
                result = self.categorize_transaction(
                    row['description'], 
                    row['amount'],
                    row.get('date')
                )
                
                df.at[idx, 'category'] = result['category']
                df.at[idx, 'subcategory'] = result['subcategory']
                df.at[idx, 'confidence'] = result['confidence']
                df.at[idx, 'is_regular'] = result['is_regular']
        
        # Count categorization results
        categorized = df[df['category'] != 'Uncategorized']
        logger.info(f"Successfully categorized {len(categorized)} out of {len(df)} transactions")
        
        return df
    
    def get_category_suggestions(self, description: str) -> List[Dict[str, any]]:
        """
        Get category suggestions for a transaction description.
        
        Args:
            description (str): Transaction description
            
        Returns:
            List[Dict[str, any]]: List of category suggestions with confidence scores
        """
        suggestions = []
        clean_desc = description.lower().strip()
        
        # Check against all patterns
        for category, patterns in self.merchant_patterns.items():
            max_confidence = 0.0
            matched_pattern = None
            
            for pattern in patterns:
                if re.search(pattern, clean_desc):
                    confidence = len(re.findall(pattern, clean_desc)) * 0.2
                    confidence = min(confidence, 1.0)
                    
                    if confidence > max_confidence:
                        max_confidence = confidence
                        matched_pattern = pattern
            
            if max_confidence > 0:
                suggestions.append({
                    'category': category,
                    'confidence': max_confidence,
                    'reason': f'Matched pattern: {matched_pattern}'
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def learn_from_correction(self, description: str, correct_category: str, 
                            amount: float = None) -> bool:
        """
        Learn from user category corrections to improve future categorization.
        
        Args:
            description (str): Transaction description
            correct_category (str): User-corrected category
            amount (float, optional): Transaction amount
            
        Returns:
            bool: True if learning was successful
        """
        # This is a placeholder for machine learning implementation
        # In a full implementation, this would:
        # 1. Extract features from the description
        # 2. Update the ML model with the correct category
        # 3. Potentially add new patterns to merchant_patterns
        
        logger.info(f"Learning from correction: '{description}' -> '{correct_category}'")
        
        # Simple pattern extraction for common cases
        clean_desc = description.lower().strip()
        words = clean_desc.split()
        
        # Extract potential merchant names (words with length > 3)
        merchant_words = [word for word in words if len(word) > 3 and word.isalpha()]
        
        if merchant_words and correct_category in self.merchant_patterns:
            # Add new pattern based on merchant name
            new_pattern = f".*{merchant_words[0]}.*"
            if new_pattern not in self.merchant_patterns[correct_category]:
                self.merchant_patterns[correct_category].append(new_pattern)
                logger.info(f"Added new pattern '{new_pattern}' to category '{correct_category}'")
                return True
        
        return False
    
    def detect_regular_payments(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect regular/recurring payments in transaction history.
        
        Args:
            transactions_df (pd.DataFrame): Transaction data
            
        Returns:
            pd.DataFrame: DataFrame with regular payment flags
        """
        logger.info("Detecting regular payments...")
        
        df = transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Group by description and amount to find recurring transactions
        grouped = df.groupby(['description', 'amount']).agg({
            'date': ['count', 'min', 'max'],
            'id': 'first'
        }).reset_index()
        
        # Flatten column names
        grouped.columns = ['description', 'amount', 'count', 'min_date', 'max_date', 'first_id']
        
        # Calculate date span in days
        grouped['date_span'] = (grouped['max_date'] - grouped['min_date']).dt.days
        
        # Identify regular payments (at least 3 occurrences over reasonable time span)
        regular_payments = grouped[
            (grouped['count'] >= 3) & 
            (grouped['date_span'] > 30)  # At least 30 days apart
        ]
        
        # Mark transactions as regular
        if 'is_regular' not in df.columns:
            df['is_regular'] = False
        
        for _, payment in regular_payments.iterrows():
            mask = (
                (df['description'] == payment['description']) & 
                (df['amount'] == payment['amount'])
            )
            df.loc[mask, 'is_regular'] = True
        
        logger.info(f"Detected {len(regular_payments)} regular payment patterns")
        return df
    
    def get_category_stats(self, transactions_df: pd.DataFrame) -> Dict[str, any]:
        """
        Get categorization statistics and insights.
        
        Args:
            transactions_df (pd.DataFrame): Categorized transaction data
            
        Returns:
            Dict[str, any]: Categorization statistics
        """
        stats = {
            'total_transactions': len(transactions_df),
            'categorized_transactions': 0,
            'uncategorized_transactions': 0,
            'category_breakdown': {},
            'confidence_stats': {},
            'regular_payments': 0
        }
        
        if transactions_df.empty:
            return stats
        
        # Basic categorization stats
        if 'category' in transactions_df.columns:
            categorized = transactions_df[transactions_df['category'] != 'Uncategorized']
            stats['categorized_transactions'] = len(categorized)
            stats['uncategorized_transactions'] = len(transactions_df) - len(categorized)
            
            # Category breakdown
            category_counts = transactions_df['category'].value_counts()
            stats['category_breakdown'] = category_counts.to_dict()
        
        # Confidence statistics
        if 'confidence' in transactions_df.columns:
            confidence_data = transactions_df['confidence']
            stats['confidence_stats'] = {
                'mean_confidence': confidence_data.mean(),
                'high_confidence': len(confidence_data[confidence_data >= 0.7]),
                'low_confidence': len(confidence_data[confidence_data < 0.4])
            }
        
        # Regular payments
        if 'is_regular' in transactions_df.columns:
            stats['regular_payments'] = transactions_df['is_regular'].sum()
        
        return stats