import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from source.library_load_csv import format_date, checkout_duration

class TestFormatDate(unittest.TestCase):
    """Tests for the format_date function"""
    
    def setUp(self):
        """Generate the data before the test"""
        self.df = pd.DataFrame ({
            'checkout': ["\"20/01/2025\"", '"15/06/2025"', "'01/12/2024'"],
            'return': ['10/03/2025', "25/08/2025", "33/11/2024"],
            'name': ['A book about Mice', 'Spot plays With a ball', 'Mr Tall']
        })
    
    def test_date_conversion(self):
        result = format_date(self.df.copy(), ['checkout','return'])
        
        print(result['return'].dtypes)

        self.assertEqual(str(result['checkout'].dtype), 'datetime64[ns]')


    def test_date_quote_strip(self):
        result = format_date(self.df.copy(), ['checkout','return'])

        doublequotes = pd.Timestamp('2025-01-20')
        self.assertEqual(result['checkout'].iloc[0],doublequotes)
        mixedquotes1 = pd.Timestamp('2025-06-15')
        self.assertEqual(result['checkout'].iloc[1],mixedquotes1)
        mixedquotes2 = pd.Timestamp('2024-12-01')
        self.assertEqual(result['checkout'].iloc[2],mixedquotes2)


        expected4 = pd.Timestamp('2025-03-10')
        self.assertEqual(result['return'].iloc[0],expected4)
        expected5 = pd.Timestamp('2025-08-25')
        self.assertEqual(result['return'].iloc[1],expected5)


    def test_invalid_dates(self):
        result = format_date(self.df.copy(), ['checkout','return'])
        self.assertTrue(pd.isna(result['return'].iloc[2]))


class TestCheckoutDuration(unittest.TestCase):
    """Tests for the checkout_duration function"""
    
    def setUp(self):
        """Generate the data before the test"""
        self.df = pd.DataFrame ({
            'checkout': ["20/01/2025", "15/06/2025", "01/12/2024"],
            'return': ["10/03/2025", "25/08/2025", "33/11/2024"],
            'name': ["A book about Mice", "Spot plays With a ball", "Mr Tall"],
            'date_validity': ["Valid dates", "Valid dates", "Invalid dates"]
        })
        self.df['checkout'] = pd.to_datetime(self.df['checkout'], format='%d/%m/%Y', errors='coerce')
        self.df['return'] = pd.to_datetime(self.df['return'], format='%d/%m/%Y', errors='coerce')    
    
    def test_invalid_dates(self):
        result = checkout_duration(self.df.copy(), 
                                   'checkout', 
                                   'return', 
                                   'checkout_duration', 
                                   'date_validity', 
                                   "Valid dates")
    
        self.assertEqual(result['checkout_duration'].iloc[2], None)

if __name__ == "__main__":
    unittest.main()