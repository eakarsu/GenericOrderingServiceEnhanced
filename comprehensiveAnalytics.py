# Add comprehensive analytics to your system

class ComprehensiveAnalyticsDashboard:
    """Real-time analytics dashboard for your universal service bot"""
    
    def __init__(self, db_client: UniversalDatabaseClient):
        self.db_client = db_client
        self.metrics_collector = MetricsCollector()
        self.performance_monitor = PerformanceMonitor()
        self.business_intelligence = BusinessIntelligence()
        
    def generate_real_time_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive real-time dashboard"""
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "overview": self._generate_overview_metrics(),
            "sector_performance": self._analyze_sector_performance(),
            "user_behavior": self._analyze_user_behavior(),
            "error_analysis": self._analyze_error_patterns(),
            "performance_metrics": self._get_performance_metrics(),
            "business_insights": self._generate_business_insights(),
            "alerts": self._get_active_alerts()
        }
        
        return dashboard
    
    def _generate_overview_metrics(self) -> Dict[str, Any]:
        """Generate high-level overview metrics"""
        
        # Query your existing database for metrics
        total_interactions = self._count_total_interactions()
        active_sectors = self._count_active_sectors()
        user_satisfaction = self._calculate_average_satisfaction()
        
        return {
            "total_interactions_24h": total_interactions,
            "active_sectors": active_sectors,
            "average_satisfaction": user_satisfaction,
            "system_health": self._assess_system_health(),
            "response_time_avg": self._calculate_avg_response_time(),
            "error_rate": self._calculate_error_rate()
        }
    
    def _analyze_sector_performance(self) -> Dict[str, Any]:
        """Analyze performance across all sectors"""
        sector_metrics = {}
        
        # Get all sectors from your database
        try:
            all_sectors = self.db_client.items_col.get(include=["metadatas"])
            sectors_data = {}
            
            if all_sectors and all_sectors.get("metadatas"):
                for meta in all_sectors["metadatas"]:
                    sector = meta.get("sector", "unknown")
                    if sector not in sectors_data:
                        sectors_data[sector] = []
                    sectors_data[sector].append(meta)
            
            # Analyze each sector
            for sector, items in sectors_data.items():
                sector_metrics[sector] = {
                    "total_items": len(items),
                    "avg_price": self._calculate_avg_price(items),
                    "item_variety": self._calculate_item_variety(items),
                    "usage_frequency": self._get_sector_usage_frequency(sector),
                    "user_satisfaction": self._get_sector_satisfaction(sector),
                    "error_rate": self._get_sector_error_rate(sector)
                }
        
        except Exception as e:
            print(f"Error analyzing sector performance: {e}")
            sector_metrics = {"error": "Could not analyze sector performance"}
        
        return sector_metrics

class MetricsCollector:
    """Collect various metrics from your system"""
    
    def __init__(self):
        self.metrics_cache = {}
        self.collection_history = []
        
    def collect_performance_metrics(self, operation: str, execution_time: float, 
                                  success: bool, context: Dict):
        """Collect performance metrics from operations"""
        
        metric = {
            "operation": operation,
            "execution_time": execution_time,
            "success": success,
            "timestamp": time.time(),
            "context": context
        }
        
        # Add to cache
        if operation not in self.metrics_cache:
            self.metrics_cache[operation] = []
        
        self.metrics_cache[operation].append(metric)
        
        # Keep only recent metrics (last 1000 per operation)
        if len(self.metrics_cache[operation]) > 1000:
            self.metrics_cache[operation] = self.metrics_cache[operation][-1000:]
    
    def get_operation_statistics(self, operation: str, time_window: int = 3600) -> Dict:
        """Get statistics for a specific operation"""
        
        if operation not in self.metrics_cache:
            return {"error": f"No metrics found for operation: {operation}"}
        
        # Filter by time window
        cutoff_time = time.time() - time_window
        recent_metrics = [m for m in self.metrics_cache[operation] if m["timestamp"] >= cutoff_time]
        
        if not recent_metrics:
            return {"error": f"No recent metrics for operation: {operation}"}
        
        # Calculate statistics
        execution_times = [m["execution_time"] for m in recent_metrics]
        success_count = sum(1 for m in recent_metrics if m["success"])
        
        return {
            "operation": operation,
            "total_calls": len(recent_metrics),
            "success_rate": success_count / len(recent_metrics),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "p95_execution_time": self._calculate_percentile(execution_times, 95),
            "time_window_hours": time_window / 3600
        }
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

# Integration with your existing OrderProcessor
class EnhancedOrderProcessor(OrderProcessor):
    def __init__(self, indexer):
        super().__init__(indexer)
        self.metrics_collector = MetricsCollector()
        self.analytics = ComprehensiveAnalyticsDashboard(None)  # Pass your db_client
        
    def process_order_with_analytics(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Enhanced process_order with comprehensive analytics"""
        
        start_time = time.time()
        success = False
        result = None
        
        try:
            # Execute original process_order
            result = super().process_order(query)
            success = result.get("status") != "error"
            
        except Exception as e:
            result = {"status": "error", "message": str(e)}
            
        finally:
            # Collect metrics
            execution_time = time.time() - start_time
            self.metrics_collector.collect_performance_metrics(
                "process_order", execution_time, success, context or {}
            )
        
        # Add analytics metadata to result
        if isinstance(result, dict):
            result["analytics"] = {
                "execution_time": execution_time,
                "success": success,
                "timestamp": time.time()
            }
        
        return result

# Enhanced Integration Function
def integrate_comprehensive_analytics(bot: UniversalServiceBot):
    """Integrate comprehensive analytics into existing bot"""
    
    # Add analytics components
    bot.analytics_dashboard = ComprehensiveAnalyticsDashboard(bot.db_client)
    bot.metrics_collector = MetricsCollector()
    
    # Enhance existing processors with analytics
    for sector, processor in bot.sector_processors.items():
        if hasattr(processor, 'indexer'):
            enhanced_processor = EnhancedOrderProcessor(processor.indexer)
            bot.sector_processors[sector] = enhanced_processor
    
    # Add method to get dashboard
    def get_analytics_dashboard(self):
        return self.analytics_dashboard.generate_real_time_dashboard()
    
    bot.get_analytics_dashboard = get_analytics_dashboard.__get__(bot, UniversalServiceBot)
    
    print("✅ Comprehensive analytics integrated successfully")

# Usage example
if __name__ == "__main__":
    # Initialize your existing bot
    bot = UniversalServiceBot()
    
    # Add all advanced features
    integrate_comprehensive_analytics(bot)
    
    # Get real-time dashboard
    dashboard = bot.get_analytics_dashboard()
    print("Dashboard:", json.dumps(dashboard, indent=2))

