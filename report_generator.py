#!/usr/bin/env python3
"""
report_generator.py - Monthly Inventory Performance Report Generator

This script analyzes logged inventory data from the SQLite database and generates
a comprehensive monthly report in CSV format. The report is then automatically
emailed to the configured recipient.

The report includes:
- Total consumed (sales) for each item
- Total restocked for each item
- Average stock level throughout the month
- End of month stock level

Usage:
    python report_generator.py [--month YYYY-MM] [--db inventory.db]
    
Examples:
    # Generate report for the previous month
    python report_generator.py
    
    # Generate report for a specific month
    python report_generator.py --month 2025-10
    
    # Use a different database file
    python report_generator.py --db /path/to/inventory.db
"""

import sqlite3
import csv
import logging
import argparse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from notify import send_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("report_generator.log"),
        logging.StreamHandler()
    ]
)


class InventoryReportGenerator:
    """Generates monthly inventory performance reports from logged data."""
    
    def __init__(self, db_path='inventory.db'):
        """
        Initialize the report generator.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
    
    def connect_database(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logging.info(f"Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            return False
    
    def close_database(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")
    
    def get_month_date_range(self, year_month=None):
        """
        Get the start and end dates for a given month.
        
        Args:
            year_month (str): Month in format 'YYYY-MM'. If None, uses previous month.
        
        Returns:
            tuple: (start_date, end_date, month_name, year)
        """
        if year_month:
            # Parse provided month
            target_date = datetime.strptime(year_month, '%Y-%m')
        else:
            # Use previous month (since we run on the 1st of each month)
            today = datetime.now()
            target_date = today - relativedelta(months=1)
        
        # First day of the month
        start_date = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Last day of the month (first day of next month minus 1 second)
        next_month = start_date + relativedelta(months=1)
        end_date = next_month - timedelta(seconds=1)
        
        month_name = start_date.strftime('%B')
        year = start_date.year
        
        logging.info(f"Report period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        return start_date, end_date, month_name, year
    
    def fetch_monthly_data(self, start_date, end_date):
        """
        Fetch all inventory data for the specified month.
        
        Args:
            start_date (datetime): Start of the reporting period
            end_date (datetime): End of the reporting period
        
        Returns:
            list: List of tuples (timestamp, item_name, item_count)
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT timestamp, item_name, item_count
            FROM inventory_log
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY item_name, timestamp
        '''
        
        cursor.execute(query, (
            start_date.strftime('%Y-%m-%d %H:%M:%S'),
            end_date.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        data = cursor.fetchall()
        logging.info(f"Fetched {len(data)} records from database")
        
        return data
    
    def calculate_metrics(self, data):
        """
        Calculate performance metrics for each item.
        
        Metrics calculated:
        - total_consumed: Sum of all count decreases (sales/consumption)
        - total_restocked: Sum of all count increases (restocking)
        - average_stock_level: Average count throughout the period
        - end_of_month_stock: Last recorded count
        
        Args:
            data (list): List of tuples (timestamp, item_name, item_count)
        
        Returns:
            dict: Dictionary mapping item_name to metrics dictionary
        """
        # Group data by item
        item_data = defaultdict(list)
        
        for timestamp, item_name, item_count in data:
            item_data[item_name].append((timestamp, item_count))
        
        # Calculate metrics for each item
        metrics = {}
        
        for item_name, records in item_data.items():
            # Sort by timestamp (should already be sorted, but just in case)
            records.sort(key=lambda x: x[0])
            
            counts = [count for _, count in records]
            
            # Calculate consumed and restocked
            total_consumed = 0
            total_restocked = 0
            
            for i in range(1, len(counts)):
                diff = counts[i] - counts[i-1]
                
                if diff < 0:
                    # Count decreased - item was consumed/sold
                    total_consumed += abs(diff)
                elif diff > 0:
                    # Count increased - item was restocked
                    total_restocked += diff
            
            # Calculate average stock level
            average_stock_level = sum(counts) / len(counts) if counts else 0
            
            # Get end of month stock (last recorded value)
            end_of_month_stock = counts[-1] if counts else 0
            
            metrics[item_name] = {
                'total_consumed': total_consumed,
                'total_restocked': total_restocked,
                'average_stock_level': round(average_stock_level, 2),
                'end_of_month_stock': end_of_month_stock
            }
            
            logging.debug(f"{item_name}: Consumed={total_consumed}, Restocked={total_restocked}, "
                         f"Avg={average_stock_level:.2f}, End={end_of_month_stock}")
        
        logging.info(f"Calculated metrics for {len(metrics)} unique items")
        
        return metrics
    
    def generate_csv_report(self, metrics, month_name, year):
        """
        Generate a CSV report file from the calculated metrics.
        
        Args:
            metrics (dict): Dictionary of item metrics
            month_name (str): Name of the month (e.g., 'October')
            year (int): Year of the report
        
        Returns:
            str: Filename of the generated CSV report
        """
        # Create filename with month and year
        filename = f"inventory_report_{year}-{month_name.lower()}.csv"
        
        # Write CSV file
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'Item Name',
                'Total Consumed (Sales)',
                'Total Restocked',
                'Average Stock Level',
                'End of Month Stock'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows (sorted by item name)
            for item_name in sorted(metrics.keys()):
                m = metrics[item_name]
                writer.writerow({
                    'Item Name': item_name,
                    'Total Consumed (Sales)': m['total_consumed'],
                    'Total Restocked': m['total_restocked'],
                    'Average Stock Level': m['average_stock_level'],
                    'End of Month Stock': m['end_of_month_stock']
                })
        
        logging.info(f"CSV report generated: {filename}")
        
        return filename
    
    def email_report(self, csv_filename, month_name, year):
        """
        Email the generated report using the notify.py send_email function.
        
        Args:
            csv_filename (str): Path to the CSV report file
            month_name (str): Name of the month
            year (int): Year of the report
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = f"Monthly Inventory Performance Report - {month_name} {year}"
        
        body = f"""Hello,

Please find attached the inventory performance report for {month_name} {year}.

This report includes:
- Total items consumed (sales) for each product
- Total items restocked
- Average stock levels throughout the month
- End of month inventory counts

The data was automatically compiled from the YOLOv8 inventory tracking system.

Best regards,
Automated Inventory System
"""
        
        logging.info(f"Attempting to email report to configured recipient...")
        
        success = send_email(subject, body, attachment_path=csv_filename)
        
        if success:
            logging.info("Report emailed successfully!")
        else:
            logging.error("Failed to email report")
        
        return success
    
    def generate_and_send_report(self, year_month=None):
        """
        Main method to generate and email the monthly report.
        
        Args:
            year_month (str): Optional month in format 'YYYY-MM'. If None, uses previous month.
        
        Returns:
            bool: True if report generated and sent successfully
        """
        logging.info("=" * 70)
        logging.info("Monthly Inventory Report Generator")
        logging.info("=" * 70)
        
        # Connect to database
        if not self.connect_database():
            return False
        
        try:
            # Get date range for the report
            start_date, end_date, month_name, year = self.get_month_date_range(year_month)
            
            # Fetch data from database
            data = self.fetch_monthly_data(start_date, end_date)
            
            if not data:
                logging.warning("No data found for the specified period. Report not generated.")
                return False
            
            # Calculate metrics
            metrics = self.calculate_metrics(data)
            
            if not metrics:
                logging.warning("No metrics calculated. Report not generated.")
                return False
            
            # Generate CSV report
            csv_filename = self.generate_csv_report(metrics, month_name, year)
            
            # Email the report
            success = self.email_report(csv_filename, month_name, year)
            
            logging.info("=" * 70)
            logging.info(f"Report generation {'completed successfully' if success else 'completed with errors'}")
            logging.info("=" * 70)
            
            return success
            
        except Exception as e:
            logging.error(f"Error generating report: {e}", exc_info=True)
            return False
            
        finally:
            self.close_database()


def main():
    """Main entry point for the script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Generate monthly inventory performance reports'
    )
    parser.add_argument(
        '--month',
        type=str,
        help='Month to generate report for (format: YYYY-MM). Default: previous month'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='inventory.db',
        help='Path to SQLite database file (default: inventory.db)'
    )
    
    args = parser.parse_args()
    
    # Validate month format if provided
    if args.month:
        try:
            datetime.strptime(args.month, '%Y-%m')
        except ValueError:
            logging.error("Invalid month format. Use YYYY-MM (e.g., 2025-10)")
            return
    
    # Create report generator and run
    generator = InventoryReportGenerator(db_path=args.db)
    generator.generate_and_send_report(year_month=args.month)


if __name__ == '__main__':
    main()

