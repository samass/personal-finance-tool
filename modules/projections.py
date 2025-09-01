"""
Projection Engine Module

This module provides financial projection and forecasting capabilities,
including regular spending projections, seasonal pattern analysis, and
multi-year financial forecasting.

Designed for beginners with clear documentation and realistic projections.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectionEngine:
    """
    Provides financial projection and forecasting capabilities.
    
    This class offers:
    - Regular spending projections (mortgages, utilities, etc.)
    - Seasonal spending pattern projections
    - Variable spending trend analysis
    - Multi-year financial forecasting
    - Scenario planning capabilities
    - Budget planning assistance
    """
    
    def __init__(self):
        """Initialize the projection engine."""
        
        # Seasonal adjustment factors for different categories
        self.seasonal_factors = {
            'Food & Dining': {
                1: 1.05, 2: 0.95, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0,
                7: 1.1, 8: 1.1, 9: 1.0, 10: 1.0, 11: 1.15, 12: 1.2
            },
            'Shopping': {
                1: 0.8, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.1, 6: 1.1,
                7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.3, 12: 1.4
            },
            'Transportation': {
                1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.1, 6: 1.2,
                7: 1.3, 8: 1.3, 9: 1.1, 10: 1.0, 11: 1.0, 12: 1.0
            },
            'Entertainment': {
                1: 0.9, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.1, 6: 1.2,
                7: 1.3, 8: 1.2, 9: 1.0, 10: 1.0, 11: 1.1, 12: 1.3
            }
        }
        
        logger.info("Projection engine initialized")
    
    def project_regular_spending(self, transactions_df: pd.DataFrame, 
                               months_ahead: int = 12) -> Dict[str, Any]:
        """
        Project regular/recurring spending patterns.
        
        Args:
            transactions_df (pd.DataFrame): Historical transaction data
            months_ahead (int): Number of months to project forward
            
        Returns:
            Dict[str, Any]: Regular spending projections
        """
        logger.info(f"Projecting regular spending for {months_ahead} months ahead")
        
        if transactions_df.empty:
            return {'error': 'No transaction data available'}
        
        df = transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Identify regular payments
        regular_payments = self._identify_regular_payments(df)
        
        projections = {
            'regular_payments': regular_payments,
            'monthly_projections': [],
            'annual_total': 0,
            'confidence_level': 'medium'
        }
        
        # Project each regular payment forward
        base_date = df['date'].max()
        
        for month_offset in range(1, months_ahead + 1):
            projection_date = base_date + timedelta(days=30 * month_offset)
            month_total = 0
            
            month_projection = {
                'month': projection_date.strftime('%Y-%m'),
                'payments': [],
                'total': 0
            }
            
            for payment in regular_payments:
                # Estimate next payment amount (could vary slightly)
                estimated_amount = payment['average_amount']
                
                # Add some variability for non-fixed payments
                if payment['payment_type'] != 'fixed':
                    variability = estimated_amount * 0.1  # 10% variability
                    estimated_amount += np.random.normal(0, variability)
                
                month_projection['payments'].append({
                    'description': payment['description'],
                    'estimated_amount': round(estimated_amount, 2),
                    'payment_type': payment['payment_type'],
                    'confidence': payment['confidence']
                })
                
                month_total += estimated_amount
            
            month_projection['total'] = round(month_total, 2)
            projections['monthly_projections'].append(month_projection)
        
        # Calculate annual total
        projections['annual_total'] = sum(
            month['total'] for month in projections['monthly_projections']
        )
        
        # Set confidence level based on data quality
        avg_confidence = np.mean([p['confidence'] for p in regular_payments]) if regular_payments else 0
        if avg_confidence > 0.8:
            projections['confidence_level'] = 'high'
        elif avg_confidence > 0.6:
            projections['confidence_level'] = 'medium'
        else:
            projections['confidence_level'] = 'low'
        
        return projections
    
    def project_variable_spending(self, transactions_df: pd.DataFrame, 
                                months_ahead: int = 12) -> Dict[str, Any]:
        """
        Project variable spending based on historical trends.
        
        Args:
            transactions_df (pd.DataFrame): Historical transaction data
            months_ahead (int): Number of months to project forward
            
        Returns:
            Dict[str, Any]: Variable spending projections
        """
        logger.info(f"Projecting variable spending for {months_ahead} months ahead")
        
        if transactions_df.empty:
            return {'error': 'No transaction data available'}
        
        df = transactions_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter out regular payments
        regular_payments = self._identify_regular_payments(df)
        regular_descriptions = [p['description'] for p in regular_payments]
        
        variable_df = df[~df['description'].isin(regular_descriptions)]
        variable_df = variable_df[variable_df['amount'] < 0].copy()  # Expenses only
        variable_df['amount'] = variable_df['amount'].abs()
        
        projections = {
            'monthly_projections': [],
            'category_projections': {},
            'trend_analysis': {},
            'annual_total': 0
        }
        
        # Analyze historical trends
        variable_df['month'] = variable_df['date'].dt.to_period('M')
        monthly_totals = variable_df.groupby('month')['amount'].sum()
        
        if len(monthly_totals) < 3:
            # Not enough data for reliable projections
            projections['error'] = 'Insufficient data for variable spending projections'
            return projections
        
        # Calculate trend
        trend_slope = self._calculate_trend(monthly_totals.values)
        base_monthly_spending = monthly_totals.mean()
        
        projections['trend_analysis'] = {
            'average_monthly': round(base_monthly_spending, 2),
            'trend_slope': round(trend_slope, 2),
            'trend_direction': 'increasing' if trend_slope > 0 else 'decreasing'
        }
        
        # Project by category if available
        if 'category' in variable_df.columns:
            category_projections = self._project_by_category(variable_df, months_ahead)
            projections['category_projections'] = category_projections
        
        # Generate monthly projections
        current_date = df['date'].max()
        
        for month_offset in range(1, months_ahead + 1):
            projection_date = current_date + timedelta(days=30 * month_offset)
            
            # Base projection with trend
            projected_amount = base_monthly_spending + (trend_slope * month_offset)
            
            # Apply seasonal adjustments
            seasonal_factor = self._get_seasonal_factor(projection_date.month, variable_df)
            projected_amount *= seasonal_factor
            
            # Add some uncertainty
            uncertainty_range = projected_amount * 0.15  # 15% uncertainty
            
            month_projection = {
                'month': projection_date.strftime('%Y-%m'),
                'projected_amount': round(projected_amount, 2),
                'uncertainty_range': round(uncertainty_range, 2),
                'seasonal_factor': round(seasonal_factor, 2)
            }
            
            projections['monthly_projections'].append(month_projection)
        
        # Calculate annual total
        projections['annual_total'] = sum(
            month['projected_amount'] for month in projections['monthly_projections']
        )
        
        return projections
    
    def create_budget_projections(self, transactions_df: pd.DataFrame, 
                                budget_goals: Dict[str, float] = None,
                                months_ahead: int = 12) -> Dict[str, Any]:
        """
        Create budget projections and compare with historical spending.
        
        Args:
            transactions_df (pd.DataFrame): Historical transaction data
            budget_goals (Dict[str, float]): Monthly budget goals by category
            months_ahead (int): Number of months to project
            
        Returns:
            Dict[str, Any]: Budget projections and analysis
        """
        logger.info(f"Creating budget projections for {months_ahead} months")
        
        if transactions_df.empty:
            return {'error': 'No transaction data available'}
        
        # Get historical spending by category
        expense_df = transactions_df[transactions_df['amount'] < 0].copy()
        expense_df['amount'] = expense_df['amount'].abs()
        expense_df['date'] = pd.to_datetime(expense_df['date'])
        
        # Default budget goals based on historical data if not provided
        if budget_goals is None:
            budget_goals = self._estimate_budget_goals(expense_df)
        
        projections = {
            'budget_goals': budget_goals,
            'historical_analysis': {},
            'monthly_projections': [],
            'annual_summary': {},
            'recommendations': []
        }
        
        # Analyze historical performance vs budget
        if 'category' in expense_df.columns:
            historical_monthly = expense_df.groupby(
                [expense_df['date'].dt.to_period('M'), 'category']
            )['amount'].sum().unstack(fill_value=0)
            
            projections['historical_analysis'] = self._analyze_budget_performance(
                historical_monthly, budget_goals
            )
        
        # Project monthly budgets
        current_date = expense_df['date'].max()
        
        for month_offset in range(1, months_ahead + 1):
            projection_date = current_date + timedelta(days=30 * month_offset)
            
            month_projection = {
                'month': projection_date.strftime('%Y-%m'),
                'categories': {},
                'total_budget': 0,
                'projected_actual': 0
            }
            
            for category, budget_amount in budget_goals.items():
                # Apply seasonal adjustment to budget
                seasonal_factor = self._get_seasonal_factor_for_category(
                    category, projection_date.month
                )
                adjusted_budget = budget_amount * seasonal_factor
                
                # Estimate actual spending based on historical patterns
                if category in historical_monthly.columns:
                    historical_avg = historical_monthly[category].mean()
                    projected_actual = historical_avg * seasonal_factor
                else:
                    projected_actual = adjusted_budget
                
                month_projection['categories'][category] = {
                    'budget': round(adjusted_budget, 2),
                    'projected_actual': round(projected_actual, 2),
                    'variance': round(projected_actual - adjusted_budget, 2)
                }
                
                month_projection['total_budget'] += adjusted_budget
                month_projection['projected_actual'] += projected_actual
            
            month_projection['total_budget'] = round(month_projection['total_budget'], 2)
            month_projection['projected_actual'] = round(month_projection['projected_actual'], 2)
            month_projection['total_variance'] = round(
                month_projection['projected_actual'] - month_projection['total_budget'], 2
            )
            
            projections['monthly_projections'].append(month_projection)
        
        # Annual summary
        annual_budget = sum(month['total_budget'] for month in projections['monthly_projections'])
        annual_projected = sum(month['projected_actual'] for month in projections['monthly_projections'])
        
        projections['annual_summary'] = {
            'total_budget': round(annual_budget, 2),
            'projected_spending': round(annual_projected, 2),
            'variance': round(annual_projected - annual_budget, 2),
            'budget_adherence_score': round((annual_budget / annual_projected) * 100, 1) if annual_projected > 0 else 100
        }
        
        # Generate recommendations
        projections['recommendations'] = self._generate_budget_recommendations(projections)
        
        return projections
    
    def scenario_analysis(self, transactions_df: pd.DataFrame, 
                         scenarios: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Perform scenario analysis for different financial situations.
        
        Args:
            transactions_df (pd.DataFrame): Historical transaction data
            scenarios (Dict[str, Dict[str, float]]): Different scenarios to analyze
            
        Returns:
            Dict[str, Any]: Scenario analysis results
        """
        logger.info("Performing scenario analysis")
        
        base_projections = self.project_variable_spending(transactions_df, 12)
        
        analysis = {
            'base_scenario': base_projections,
            'scenario_comparisons': {},
            'recommendations': []
        }
        
        # Analyze each scenario
        for scenario_name, adjustments in scenarios.items():
            scenario_projection = self._apply_scenario_adjustments(
                base_projections, adjustments
            )
            analysis['scenario_comparisons'][scenario_name] = scenario_projection
        
        return analysis
    
    def _identify_regular_payments(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify regular/recurring payments from transaction history."""
        
        # Group by description and amount to find recurring patterns
        expense_df = df[df['amount'] < 0].copy()
        expense_df['amount'] = expense_df['amount'].abs()
        
        grouped = expense_df.groupby(['description', 'amount']).agg({
            'date': ['count', 'min', 'max'],
            'amount': 'first'
        }).reset_index()
        
        # Flatten column names
        grouped.columns = ['description', 'amount', 'count', 'min_date', 'max_date', 'avg_amount']
        
        # Calculate regularity metrics
        grouped['date_span'] = (grouped['max_date'] - grouped['min_date']).dt.days
        grouped['frequency'] = grouped['count'] / (grouped['date_span'] / 30 + 1)  # Payments per month
        
        # Identify regular payments (at least 3 occurrences, reasonable frequency)
        regular_mask = (
            (grouped['count'] >= 3) & 
            (grouped['frequency'] >= 0.8) &  # At least 0.8 times per month
            (grouped['date_span'] >= 60)     # Over at least 2 months
        )
        
        regular_payments = []
        
        for _, payment in grouped[regular_mask].iterrows():
            # Determine payment type
            amount_variance = expense_df[
                (expense_df['description'] == payment['description'])
            ]['amount'].std()
            
            if amount_variance < payment['avg_amount'] * 0.05:  # Less than 5% variance
                payment_type = 'fixed'
                confidence = 0.9
            elif amount_variance < payment['avg_amount'] * 0.15:  # Less than 15% variance
                payment_type = 'semi_variable'
                confidence = 0.7
            else:
                payment_type = 'variable'
                confidence = 0.5
            
            regular_payments.append({
                'description': payment['description'],
                'average_amount': payment['avg_amount'],
                'frequency': payment['frequency'],
                'payment_type': payment_type,
                'confidence': confidence,
                'occurrences': payment['count']
            })
        
        return regular_payments
    
    def _calculate_trend(self, values: np.ndarray) -> float:
        """Calculate trend slope using linear regression."""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return slope
    
    def _get_seasonal_factor(self, month: int, df: pd.DataFrame) -> float:
        """Get seasonal adjustment factor for a given month."""
        if 'category' not in df.columns:
            return 1.0
        
        # Calculate seasonal factors based on historical data
        df['month'] = df['date'].dt.month
        monthly_spending = df.groupby('month')['amount'].sum()
        
        if len(monthly_spending) >= 12:
            # Use actual historical seasonal pattern
            annual_avg = monthly_spending.mean()
            month_avg = monthly_spending.get(month, annual_avg)
            return month_avg / annual_avg if annual_avg > 0 else 1.0
        else:
            # Use default seasonal factors
            return 1.0
    
    def _get_seasonal_factor_for_category(self, category: str, month: int) -> float:
        """Get seasonal factor for specific category and month."""
        if category in self.seasonal_factors:
            return self.seasonal_factors[category].get(month, 1.0)
        return 1.0
    
    def _project_by_category(self, df: pd.DataFrame, months_ahead: int) -> Dict[str, Any]:
        """Project spending by category."""
        category_projections = {}
        
        for category in df['category'].unique():
            category_df = df[df['category'] == category]
            monthly_amounts = category_df.groupby(
                category_df['date'].dt.to_period('M')
            )['amount'].sum()
            
            if len(monthly_amounts) >= 3:
                avg_monthly = monthly_amounts.mean()
                trend = self._calculate_trend(monthly_amounts.values)
                
                category_projections[category] = {
                    'monthly_average': round(avg_monthly, 2),
                    'trend': round(trend, 2),
                    'projected_annual': round((avg_monthly + trend * 6) * 12, 2)
                }
        
        return category_projections
    
    def _estimate_budget_goals(self, expense_df: pd.DataFrame) -> Dict[str, float]:
        """Estimate reasonable budget goals based on historical spending."""
        if 'category' not in expense_df.columns:
            return {'General': expense_df['amount'].sum() / max(1, len(expense_df['date'].dt.to_period('M').unique()))}
        
        monthly_by_category = expense_df.groupby(
            [expense_df['date'].dt.to_period('M'), 'category']
        )['amount'].sum().unstack(fill_value=0)
        
        # Set budget as 110% of historical average (allows for slight increase)
        budget_goals = {}
        for category in monthly_by_category.columns:
            avg_spending = monthly_by_category[category].mean()
            budget_goals[category] = round(avg_spending * 1.1, 2)
        
        return budget_goals
    
    def _analyze_budget_performance(self, historical_monthly: pd.DataFrame, 
                                  budget_goals: Dict[str, float]) -> Dict[str, Any]:
        """Analyze historical budget performance."""
        performance = {}
        
        for category, budget in budget_goals.items():
            if category in historical_monthly.columns:
                actual_spending = historical_monthly[category]
                avg_actual = actual_spending.mean()
                
                performance[category] = {
                    'budget': budget,
                    'average_actual': round(avg_actual, 2),
                    'variance': round(avg_actual - budget, 2),
                    'adherence_rate': round((budget / avg_actual) * 100, 1) if avg_actual > 0 else 100,
                    'months_over_budget': len(actual_spending[actual_spending > budget])
                }
        
        return performance
    
    def _generate_budget_recommendations(self, projections: Dict[str, Any]) -> List[str]:
        """Generate budget recommendations based on projections."""
        recommendations = []
        
        # Check overall budget adherence
        annual_summary = projections['annual_summary']
        if annual_summary['variance'] > 0:
            recommendations.append(
                f"Projected spending exceeds budget by ${annual_summary['variance']:,.2f} annually"
            )
        
        # Check category-specific issues
        for month_data in projections['monthly_projections'][:3]:  # Check first 3 months
            for category, data in month_data['categories'].items():
                if data['variance'] > data['budget'] * 0.2:  # More than 20% over budget
                    recommendations.append(
                        f"Consider reducing {category} spending - consistently over budget"
                    )
                    break  # Don't repeat for same category
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _apply_scenario_adjustments(self, base_projections: Dict[str, Any], 
                                  adjustments: Dict[str, float]) -> Dict[str, Any]:
        """Apply scenario adjustments to base projections."""
        adjusted = base_projections.copy()
        
        # Apply percentage adjustments to projections
        for month in adjusted['monthly_projections']:
            for adjustment_type, factor in adjustments.items():
                if adjustment_type == 'overall_spending':
                    month['projected_amount'] *= (1 + factor)
                elif adjustment_type == 'income_change':
                    # This would affect affordability but not historical projections
                    pass
        
        # Recalculate annual total
        adjusted['annual_total'] = sum(
            month['projected_amount'] for month in adjusted['monthly_projections']
        )
        
        return adjusted