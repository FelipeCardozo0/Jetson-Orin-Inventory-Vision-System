#!/usr/bin/env python3
"""
Data Generator for YOLOv8 Inventory Analytics
Generates realistic business metrics and performance data for investor presentations
"""

import json
import random
import datetime
from typing import Dict, List, Any
import numpy as np

class AnalyticsDataGenerator:
    def __init__(self):
        self.base_date = datetime.datetime(2023, 1, 1)
        self.current_date = datetime.datetime.now()
        
    def generate_cost_savings(self, locations: int = 50) -> Dict:
        """Generate cost savings breakdown by category"""
        savings_data = {
            'labor_savings': {
                'amount': locations * random.uniform(120000, 180000),
                'percentage': 45,
                'description': 'Reduced manual inventory counting'
            },
            'stockout_prevention': {
                'amount': locations * random.uniform(30000, 60000),
                'percentage': 25,
                'description': 'Prevented lost sales from stockouts'
            },
            'inventory_accuracy': {
                'amount': locations * random.uniform(20000, 40000),
                'percentage': 20,
                'description': 'Reduced shrinkage and overstock'
            },
            'maintenance_reduction': {
                'amount': locations * random.uniform(10000, 20000),
                'percentage': 10,
                'description': 'Reduced system maintenance costs'
            }
        }
        
        return savings_data
    
    def generate_performance_metrics(self) -> Dict:
        """Generate system performance metrics"""
        return {
            'accuracy': {
                'current': round(random.uniform(98.0, 99.5), 1),
                'baseline': 85.0,
                'improvement': round(random.uniform(13.0, 14.5), 1)
            },
            'uptime': {
                'current': round(random.uniform(99.5, 99.9), 1),
                'baseline': 95.0,
                'improvement': round(random.uniform(4.5, 4.9), 1)
            },
            'processing_speed': {
                'fps': random.randint(25, 35),
                'latency_ms': random.randint(150, 250),
                'throughput': random.randint(800, 1200)
            },
            'scalability': {
                'max_cameras': random.randint(50, 100),
                'concurrent_users': random.randint(20, 50),
                'locations_supported': random.randint(100, 200)
            }
        }
    
    def generate_competitive_analysis(self) -> Dict:
        """Generate competitive analysis data"""
        return {
            'our_solution': {
                'deployment_time_weeks': random.randint(2, 4),
                'cost_per_location': random.randint(500, 2000),
                'accuracy_percentage': round(random.uniform(98.0, 99.5), 1),
                'maintenance_hours_monthly': random.randint(2, 8),
                'scalability_score': random.randint(90, 100)
            },
            'traditional_systems': {
                'deployment_time_weeks': random.randint(12, 24),
                'cost_per_location': random.randint(10000, 50000),
                'accuracy_percentage': round(random.uniform(85.0, 90.0), 1),
                'maintenance_hours_monthly': random.randint(20, 40),
                'scalability_score': random.randint(60, 80)
            },
            'market_alternatives': {
                'rfid_systems': {
                    'cost_per_location': random.randint(15000, 30000),
                    'accuracy_percentage': round(random.uniform(95.0, 98.0), 1),
                    'deployment_time_weeks': random.randint(8, 16)
                },
                'barcode_systems': {
                    'cost_per_location': random.randint(5000, 15000),
                    'accuracy_percentage': round(random.uniform(80.0, 90.0), 1),
                    'deployment_time_weeks': random.randint(4, 8)
                }
            }
        }
    
    def generate_customer_feedback(self, num_customers: int = 20) -> List[Dict]:
        """Generate realistic customer feedback data"""
        feedback_templates = [
            "Reduced inventory counting time by 80%",
            "Prevented 3 major stockouts this quarter",
            "Improved accuracy from 85% to 98%",
            "ROI achieved in 2.5 months",
            "Easy to deploy and maintain",
            "Real-time alerts are game-changing",
            "Reduced labor costs significantly",
            "Better visibility into inventory levels"
        ]
        
        customers = []
        for i in range(num_customers):
            customers.append({
                'customer_id': f'CUST_{i+1:03d}',
                'industry': random.choice(['Retail', 'Restaurant', 'Warehouse', 'Manufacturing']),
                'locations': random.randint(1, 10),
                'satisfaction_score': round(random.uniform(4.2, 5.0), 1),
                'feedback': random.choice(feedback_templates),
                'months_using': random.randint(1, 18),
                'annual_savings': random.randint(50000, 500000)
            })
            
        return customers
    
    def generate_market_data(self) -> Dict:
        """Generate market size and opportunity data"""
        return {
            'total_addressable_market': {
                'value_billions': 2.8,
                'growth_rate_percent': 12.5,
                'description': 'Global inventory management software market'
            },
            'serviceable_addressable_market': {
                'value_billions': 0.8,
                'growth_rate_percent': 15.2,
                'description': 'Real-time inventory monitoring segment'
            },
            'serviceable_obtainable_market': {
                'value_millions': 120,
                'growth_rate_percent': 25.0,
                'description': 'AI-powered inventory solutions'
            },
            'market_trends': [
                'Increasing demand for automation',
                'Rising labor costs driving efficiency needs',
                'COVID-19 accelerating digital transformation',
                'AI/ML becoming mainstream in business',
                'Edge computing reducing latency requirements'
            ]
        }
    
    def generate_all_data(self) -> Dict:
        """Generate complete dataset for analytics dashboard (excluding revenue, customers, and ROI)"""
        return {
            'cost_savings': self.generate_cost_savings(),
            'performance_metrics': self.generate_performance_metrics(),
            'competitive_analysis': self.generate_competitive_analysis(),
            'customer_feedback': self.generate_customer_feedback(),
            'market_data': self.generate_market_data(),
            'generated_at': datetime.datetime.now().isoformat(),
            'data_version': '1.0'
        }
    
    def save_data(self, filename: str = 'analytics_data.json'):
        """Save generated data to JSON file"""
        data = self.generate_all_data()
        
        with open(f'../data/{filename}', 'w') as f:
            json.dump(data, f, indent=2, default=str)
            
        print(f"Analytics data saved to {filename}")
        return data

def main():
    """Generate and save analytics data"""
    generator = AnalyticsDataGenerator()
    
    # Generate comprehensive dataset
    data = generator.save_data()
    
    # Print summary
    print("\n=== Analytics Data Summary ===")
    print(f"Customer feedback entries: {len(data['customer_feedback'])}")
    print(f"Total annual savings: ${data['cost_savings']['labor_savings']['amount']:,.0f}")
    print(f"System accuracy: {data['performance_metrics']['accuracy']['current']}%")
    
    # Generate additional data files
    generator.save_data('performance_data.json')

if __name__ == "__main__":
    main()
