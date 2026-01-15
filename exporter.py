"""
Data exporter module for saving scraped data to CSV/Excel
"""
import os
import logging
from typing import List, Dict
import pandas as pd
from datetime import datetime

import config
from utils import clean_text, format_price


class DataExporter:
    """Export scraped data to various formats"""
    
    def __init__(self):
        """Initialize the data exporter"""
        self.logger = logging.getLogger('NLScraper.DataExporter')
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    def _prepare_data_for_export(self, products: List[Dict], image_map: Dict = None) -> pd.DataFrame:
        """
        Prepare product data for export
        
        Args:
            products: List of product dictionaries
            image_map: Optional mapping of product URLs to downloaded image paths
            
        Returns:
            Pandas DataFrame ready for export
        """
        if not products:
            return pd.DataFrame()
        
        # Flatten product data
        rows = []
        
        for product in products:
            row = {
                'Product Name': clean_text(product.get('name', 'N/A')),
                'Price': format_price(product.get('price', 'N/A')),
                'Description': clean_text(product.get('description', 'N/A')),
                'Category': clean_text(product.get('category', 'N/A')),
                'SKU': product.get('sku', 'N/A'),
                'Rating': product.get('rating', 'N/A'),
                'Product URL': product.get('url', 'N/A'),
                'Image URLs': ', '.join(product.get('images', [])),
            }
            
            # Add local image paths if available
            if image_map and product.get('url') in image_map:
                local_images = image_map[product.get('url')]
                row['Local Image Paths'] = ', '.join(local_images)
            else:
                row['Local Image Paths'] = 'N/A'
            
            # Add specifications as separate columns
            specs = product.get('specifications', {})
            if specs and isinstance(specs, dict):
                for key, value in specs.items():
                    # Clean key for column name
                    col_name = f"Spec: {clean_text(key)}"
                    row[col_name] = clean_text(str(value))
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        return df
    
    def _prepare_trademe_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data in TradeMe compatible format
        
        Args:
            df: Original DataFrame
            
        Returns:
            TradeMe formatted DataFrame
        """
        # TradeMe typical columns (adjust based on actual requirements)
        trademe_df = pd.DataFrame()
        
        trademe_df['Title'] = df['Product Name']
        trademe_df['Category'] = df['Category']
        trademe_df['Description'] = df['Description']
        trademe_df['StartPrice'] = df['Price'].str.replace('$', '').str.replace(',', '')
        trademe_df['BuyNowPrice'] = trademe_df['StartPrice']
        
        # Add images
        if 'Local Image Paths' in df.columns:
            trademe_df['Photos'] = df['Local Image Paths']
        else:
            trademe_df['Photos'] = df['Image URLs']
        
        # Add condition (default to new for retail products)
        trademe_df['Condition'] = 'New'
        
        # Add shipping info (placeholder)
        trademe_df['ShippingInfo'] = 'Buyer pays shipping'
        
        # Add SKU
        if 'SKU' in df.columns:
            trademe_df['SKU'] = df['SKU']
        
        return trademe_df
    
    def export_to_csv(self, products: List[Dict], image_map: Dict = None, 
                      trademe_format: bool = False) -> str:
        """
        Export products to CSV file
        
        Args:
            products: List of product dictionaries
            image_map: Optional mapping of product URLs to downloaded image paths
            trademe_format: Whether to format for TradeMe compatibility
            
        Returns:
            Path to the created CSV file
        """
        self.logger.info("Exporting data to CSV...")
        
        df = self._prepare_data_for_export(products, image_map)
        
        if df.empty:
            self.logger.warning("No data to export")
            return None
        
        # Apply TradeMe format if requested
        if trademe_format and config.TRADEME_COMPATIBLE:
            df = self._prepare_trademe_format(df)
            suffix = '_trademe'
        else:
            suffix = ''
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{config.OUTPUT_FILENAME}{suffix}_{timestamp}.csv"
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        # Export to CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        self.logger.info(f"Data exported to CSV: {filepath}")
        self.logger.info(f"Total records: {len(df)}")
        
        return filepath
    
    def export_to_excel(self, products: List[Dict], image_map: Dict = None,
                        trademe_format: bool = False) -> str:
        """
        Export products to Excel file
        
        Args:
            products: List of product dictionaries
            image_map: Optional mapping of product URLs to downloaded image paths
            trademe_format: Whether to format for TradeMe compatibility
            
        Returns:
            Path to the created Excel file
        """
        self.logger.info("Exporting data to Excel...")
        
        df = self._prepare_data_for_export(products, image_map)
        
        if df.empty:
            self.logger.warning("No data to export")
            return None
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{config.OUTPUT_FILENAME}_{timestamp}.xlsx"
        filepath = os.path.join(config.OUTPUT_DIR, filename)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Products', index=False)
            
            # TradeMe format sheet if requested
            if trademe_format and config.TRADEME_COMPATIBLE:
                trademe_df = self._prepare_trademe_format(df)
                trademe_df.to_excel(writer, sheet_name='TradeMe Format', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total Products',
                    'Total Categories',
                    'Products with Images',
                    'Export Date'
                ],
                'Value': [
                    len(products),
                    len(set(p.get('category', 'N/A') for p in products)),
                    sum(1 for p in products if p.get('images')),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        self.logger.info(f"Data exported to Excel: {filepath}")
        self.logger.info(f"Total records: {len(df)}")
        
        return filepath
    
    def export(self, products: List[Dict], image_map: Dict = None) -> List[str]:
        """
        Export products to configured format(s)
        
        Args:
            products: List of product dictionaries
            image_map: Optional mapping of product URLs to downloaded image paths
            
        Returns:
            List of paths to created files
        """
        output_files = []
        
        if config.OUTPUT_FORMAT.lower() == 'csv':
            # Export standard CSV
            csv_file = self.export_to_csv(products, image_map, trademe_format=False)
            if csv_file:
                output_files.append(csv_file)
            
            # Export TradeMe CSV if enabled
            if config.TRADEME_COMPATIBLE:
                trademe_file = self.export_to_csv(products, image_map, trademe_format=True)
                if trademe_file:
                    output_files.append(trademe_file)
        
        elif config.OUTPUT_FORMAT.lower() == 'excel':
            excel_file = self.export_to_excel(products, image_map, 
                                              trademe_format=config.TRADEME_COMPATIBLE)
            if excel_file:
                output_files.append(excel_file)
        
        else:
            self.logger.error(f"Unsupported output format: {config.OUTPUT_FORMAT}")
        
        return output_files
