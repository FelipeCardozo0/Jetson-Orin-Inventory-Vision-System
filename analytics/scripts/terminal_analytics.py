#!/usr/bin/env python3
"""
Terminal Analytics for YOLOv8 Inventory Monitoring System
Simulates 1 million data points and outputs comprehensive statistics
"""

import random
import time
import statistics
from datetime import datetime, timedelta
import numpy as np

class TerminalAnalytics:
    def __init__(self):
        self.data_points = 1000000  # 1 million data points
        self.locations = 100
        self.start_time = time.time()
        
    def generate_simulation_data(self):
        """Generate 1 million data points for simulation"""
        print("Generating simulation data...")
        
        # Customer acquisition data
        customer_data = []
        total_customers = 0
        for month in range(36):
            base_acquisition = 3 + month * 0.3
            new_customers = int(base_acquisition + random.uniform(-2, 5))
            total_customers += new_customers
            customer_data.append({
                'month': month,
                'new_customers': new_customers,
                'total_customers': total_customers,
                'churn_rate': random.uniform(0.02, 0.05)
            })
        
        # Performance metrics (1M data points)
        performance_data = []
        for i in range(self.data_points):
            performance_data.append({
                'accuracy': random.uniform(95.0, 99.9),
                'fps': random.uniform(25, 35),
                'latency': random.uniform(100, 300),
                'cpu_usage': random.uniform(20, 80),
                'memory_usage': random.uniform(30, 90),
                'detection_confidence': random.uniform(85, 99),
                'false_positive_rate': random.uniform(0.5, 3.0),
                'uptime': random.uniform(95, 100)
            })
        
        # Cost savings data
        savings_data = []
        for location in range(self.locations):
            savings_data.append({
                'location_id': f'LOC_{location+1:03d}',
                'labor_savings': random.uniform(100000, 200000),
                'stockout_prevention': random.uniform(20000, 60000),
                'inventory_accuracy': random.uniform(15000, 40000),
                'maintenance_reduction': random.uniform(5000, 15000)
            })
        
        return {
            'customers': customer_data,
            'performance': performance_data,
            'savings': savings_data
        }
    
    def calculate_statistics(self, data):
        """Calculate comprehensive statistics"""
        print("Calculating statistics...")
        
        # Customer statistics
        customer_totals = [c['total_customers'] for c in data['customers']]
        customer_stats = {
            'total_customers': customer_totals[-1],
            'average_monthly_growth': statistics.mean([c['new_customers'] for c in data['customers']]),
            'average_churn_rate': statistics.mean([c['churn_rate'] for c in data['customers']]),
            'customer_growth_rate': ((customer_totals[-1] - customer_totals[0]) / customer_totals[0]) * 100
        }
        
        # Performance statistics
        perf_stats = {
            'accuracy': {
                'mean': statistics.mean([p['accuracy'] for p in data['performance']]),
                'median': statistics.median([p['accuracy'] for p in data['performance']]),
                'std': statistics.stdev([p['accuracy'] for p in data['performance']]),
                'min': min([p['accuracy'] for p in data['performance']]),
                'max': max([p['accuracy'] for p in data['performance']])
            },
            'fps': {
                'mean': statistics.mean([p['fps'] for p in data['performance']]),
                'median': statistics.median([p['fps'] for p in data['performance']]),
                'std': statistics.stdev([p['fps'] for p in data['performance']])
            },
            'latency': {
                'mean': statistics.mean([p['latency'] for p in data['performance']]),
                'median': statistics.median([p['latency'] for p in data['performance']]),
                'std': statistics.stdev([p['latency'] for p in data['performance']])
            },
            'uptime': {
                'mean': statistics.mean([p['uptime'] for p in data['performance']]),
                'median': statistics.median([p['uptime'] for p in data['performance']]),
                'min': min([p['uptime'] for p in data['performance']])
            }
        }
        
        # Savings statistics
        total_savings = sum([s['labor_savings'] + s['stockout_prevention'] + 
                           s['inventory_accuracy'] + s['maintenance_reduction'] 
                           for s in data['savings']])
        
        savings_stats = {
            'total_annual_savings': total_savings,
            'average_per_location': total_savings / len(data['savings']),
            'labor_savings_total': sum([s['labor_savings'] for s in data['savings']]),
            'stockout_prevention_total': sum([s['stockout_prevention'] for s in data['savings']]),
            'inventory_accuracy_total': sum([s['inventory_accuracy'] for s in data['savings']]),
            'maintenance_reduction_total': sum([s['maintenance_reduction'] for s in data['savings']])
        }
        
        return {
            'customers': customer_stats,
            'performance': perf_stats,
            'savings': savings_stats
        }
    
    def print_statistics(self, stats, data):
        """Print formatted statistics to terminal"""
        print("\n" + "="*80)
        print("YOLOv8 INVENTORY MONITORING SYSTEM - ANALYTICS REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data Points Analyzed: {self.data_points:,}")
        print(f"Processing Time: {time.time() - self.start_time:.2f} seconds")
        print("="*80)
        
        # Customer Statistics
        print("\nCUSTOMER ANALYSIS")
        print("-" * 40)
        print(f"Total Customers: {stats['customers']['total_customers']:,}")
        print(f"Average Monthly Growth: {stats['customers']['average_monthly_growth']:.1f} customers")
        print(f"Average Churn Rate: {stats['customers']['average_churn_rate']:.2f}%")
        print(f"Customer Growth Rate: {stats['customers']['customer_growth_rate']:.2f}%")
        
        # Performance Statistics
        print("\nSYSTEM PERFORMANCE ANALYSIS")
        print("-" * 40)
        print("Detection Accuracy:")
        print(f"  Mean: {stats['performance']['accuracy']['mean']:.2f}%")
        print(f"  Median: {stats['performance']['accuracy']['median']:.2f}%")
        print(f"  Standard Deviation: {stats['performance']['accuracy']['std']:.2f}%")
        print(f"  Range: {stats['performance']['accuracy']['min']:.2f}% - {stats['performance']['accuracy']['max']:.2f}%")
        
        print("\nProcessing Speed (FPS):")
        print(f"  Mean: {stats['performance']['fps']['mean']:.2f} FPS")
        print(f"  Median: {stats['performance']['fps']['median']:.2f} FPS")
        print(f"  Standard Deviation: {stats['performance']['fps']['std']:.2f} FPS")
        
        print("\nNetwork Latency:")
        print(f"  Mean: {stats['performance']['latency']['mean']:.2f} ms")
        print(f"  Median: {stats['performance']['latency']['median']:.2f} ms")
        print(f"  Standard Deviation: {stats['performance']['latency']['std']:.2f} ms")
        
        print("\nSystem Uptime:")
        print(f"  Mean: {stats['performance']['uptime']['mean']:.2f}%")
        print(f"  Median: {stats['performance']['uptime']['median']:.2f}%")
        print(f"  Minimum: {stats['performance']['uptime']['min']:.2f}%")
        
        # ROI Calculation
        system_cost = self.locations * 2000  # $2K per location
        roi_percentage = ((stats['savings']['total_annual_savings'] - system_cost) / system_cost) * 100
        payback_months = (system_cost / stats['savings']['total_annual_savings']) * 12
        
        print("\nROI ANALYSIS")
        print("-" * 40)
        print(f"Total System Investment: ${system_cost:,.2f}")
        print(f"Annual Return on Investment: {roi_percentage:.1f}%")
        print(f"Payback Period: {payback_months:.1f} months")
        print(f"Net Annual Profit: ${stats['savings']['total_annual_savings'] - system_cost:,.2f}")
        
        # Performance Percentiles
        accuracy_values = [p['accuracy'] for p in data['performance']]
        fps_values = [p['fps'] for p in data['performance']]
        latency_values = [p['latency'] for p in data['performance']]
        
        print("\nPERFORMANCE PERCENTILES")
        print("-" * 40)
        print("Detection Accuracy Percentiles:")
        for p in [25, 50, 75, 90, 95, 99]:
            value = np.percentile(accuracy_values, p)
            print(f"  {p}th percentile: {value:.2f}%")
        
        print("\nFPS Percentiles:")
        for p in [25, 50, 75, 90, 95, 99]:
            value = np.percentile(fps_values, p)
            print(f"  {p}th percentile: {value:.2f} FPS")
        
        print("\nLatency Percentiles:")
        for p in [25, 50, 75, 90, 95, 99]:
            value = np.percentile(latency_values, p)
            print(f"  {p}th percentile: {value:.2f} ms")
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)

def main():
    """Main execution function"""
    print("YOLOv8 Inventory Monitoring System - Terminal Analytics")
    print("Simulating 1,000,000 data points...")
    
    analytics = TerminalAnalytics()
    
    # Generate data
    data = analytics.generate_simulation_data()
    
    # Calculate statistics
    stats = analytics.calculate_statistics(data)
    
    # Print results
    analytics.print_statistics(stats, data)

if __name__ == "__main__":
    main()
