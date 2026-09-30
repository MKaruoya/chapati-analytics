import pandas as pd
import numpy as np
import config

class DataProcessor:
    def __init__(self, df):
        self.df = df.copy()
        self.processed_df = None
    
    def process(self):
        """Main processing pipeline"""
        self.processed_df = self.df.copy()
        self._clean_data()
        self._extract_hierarchical_structure()
        return self.processed_df
    
    def _clean_data(self):
        """Clean and standardize data"""
        self.processed_df = self.processed_df.dropna(how='all')
        
        numeric_cols = self.processed_df.select_dtypes(include=[np.number]).columns
        self.processed_df[numeric_cols] = self.processed_df[numeric_cols].fillna(0)
        
        string_cols = self.processed_df.select_dtypes(include=['object']).columns
        for col in string_cols:
            self.processed_df[col] = self.processed_df[col].str.strip()
    
    def _extract_hierarchical_structure(self):
        """Extract store, branch, product hierarchy"""
        if 'Customer Parent Name' in self.processed_df.columns:
            self.processed_df['store'] = self.processed_df['Customer Parent Name']
        
        if 'Customer Parent_Branch' in self.processed_df.columns:
            self.processed_df['branch'] = self.processed_df['Customer Parent_Branch']
        
        if 'Item Description' in self.processed_df.columns:
            self.processed_df['product'] = self.processed_df['Item Description']
