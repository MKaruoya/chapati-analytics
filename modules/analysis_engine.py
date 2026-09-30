import pandas as pd
import numpy as np
from scipy import stats
import config

class AnalysisEngine:
    def __init__(self, df):
        self.df = df
    
    def calculate_sales_metrics(self):
        """Calculate overall sales metrics"""
        sales_cols = [col for col in self.df.columns if 'Sum of Net Bales Sales' in col]
        returns_cols = [col for col in self.df.columns if 'Sum of Bales Returns' in col]
        
        total_sales = self.df[sales_cols].sum().sum()
        total_returns = self.df[returns_cols].sum().sum()
        
        return {
            'total_sales': total_sales,
            'total_returns': total_returns,
            'net_sales': total_sales - total_returns,
            'return_rate': total_returns / total_sales if total_sales > 0 else 0,
            'average_sales_per_store': total_sales / config.STORES if config.STORES > 0 else 0
        }
    
    def calculate_monthly_trends(self):
        """Calculate month-over-month trends"""
        trends = {}
        for month in config.MONTHS:
            sales_col = [col for col in self.df.columns if month in col and 'Net Bales Sales' in col]
            if sales_col:
                trends[month.split()[1]] = self.df[sales_col[0]].sum()
        return trends
    
    def get_store_performance_ranking(self):
        """Rank stores by performance"""
        sales_cols = [col for col in self.df.columns if 'Sum of Net Bales Sales' in col]
        returns_cols = [col for col in self.df.columns if 'Sum of Bales Returns' in col]
        
        store_sales = self.df.groupby('store')[sales_cols].sum().sum(axis=1)
        store_returns = self.df.groupby('store')[returns_cols].sum().sum(axis=1)
        
        performance = pd.DataFrame({
            'sales': store_sales,
            'returns': store_returns,
            'return_rate': store_returns / store_sales
        }).sort_values('sales', ascending=False)
        
        return performance
    
    def get_product_performance_ranking(self):
        """Rank products by performance"""
        sales_cols = [col for col in self.df.columns if 'Sum of Net Bales Sales' in col]
        returns_cols = [col for col in self.df.columns if 'Sum of Bales Returns' in col]
        
        product_sales = self.df.groupby('product')[sales_cols].sum().sum(axis=1)
        product_returns = self.df.groupby('product')[returns_cols].sum().sum(axis=1)
        
        performance = pd.DataFrame({
            'sales': product_sales,
            'returns': product_returns,
            'return_rate': product_returns / product_sales
        }).sort_values('sales', ascending=False)
        
        return performance
    
    def identify_high_returns(self):
        """Identify products/stores with high return rates"""
        sales_cols = [col for col in self.df.columns if 'Sum of Net Bales Sales' in col]
        returns_cols = [col for col in self.df.columns if 'Sum of Bales Returns' in col]
        
        total_sales = self.df[sales_cols].sum(axis=1)
        total_returns = self.df[returns_cols].sum(axis=1)
        
        return_rates = np.where(total_sales > 0, total_returns / total_sales, 0)
        high_return_idx = return_rates > config.HIGH_RETURN_RATE
        
        return self.df[high_return_idx][['store', 'product', 'branch']].to_dict('records')
