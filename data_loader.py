import pandas as pd
import os

class DataLoader:
    """Load Chapati data from Excel or CSV files"""
    
    @staticmethod
    def load_excel(file_path):
        """Load data from Excel file"""
        try:
            # Try reading with multi-level headers first (raw format)
            df = pd.read_excel(file_path, header=[0, 1, 2])
            return df, "raw"
        except:
            # Fall back to simple header
            df = pd.read_excel(file_path)
            return df, "transformed"
    
    @staticmethod
    def load_csv(file_path):
        """Load data from CSV file"""
        try:
            # Try reading with multi-level headers first (raw format)
            df = pd.read_csv(file_path, header=[0, 1, 2])
            return df, "raw"
        except:
            # Fall back to simple header
            df = pd.read_csv(file_path)
            return df, "transformed"
    
    @staticmethod
    def load_file(file_path):
        """Load data from file (auto-detect format)"""
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return DataLoader.load_excel(file_path)
        elif file_path.endswith('.csv'):
            return DataLoader.load_csv(file_path)
        else:
            raise ValueError("Unsupported file format. Use .xlsx, .xls, or .csv")
    
    @staticmethod
    def save_excel(df, file_path):
        """Save data to Excel file"""
        df.to_excel(file_path, index=False)
        print(f"Saved to {file_path}")
    
    @staticmethod
    def save_csv(df, file_path):
        """Save data to CSV file"""
        df.to_csv(file_path, index=False)
        print(f"Saved to {file_path}")
