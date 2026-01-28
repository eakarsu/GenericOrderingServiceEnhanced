# Add to your menuIndexerIntentCalc.py

class RealTimeSectorAnalytics:
    """Real-time analytics for sector performance and optimization"""
    
    def __init__(self, indexer: UniversalMenuIndexer):
        self.indexer = indexer
        self.analytics_col = self._create_analytics_collection()
        self.performance_tracker = PerformanceTracker()
        self.trend_analyzer = TrendAnalyzer()
        
    def _create_analytics_collection(self):
        """Create analytics collection for tracking"""
        try:
            return self.indexer.client.get_collection("sector_analytics", self.indexer.embedder)
        except:
            return self.indexer.client.create_collection("sector_analytics", embedding_function=self.indexer.embedder)
    
    def track_sector_interaction(self, sector: str, query: str, result: Dict, user_context: Dict = None):
        """Track every sector interaction for analytics"""
        
        interaction_id = f"{sector}_{int(time.time())}_{hash(query) % 10000}"
        
        # Analyze interaction quality
        interaction_quality = self._analyze_interaction_quality(query, result)
        
        # Extract performance metrics
        performance_metrics = {
            "sector": sector,
            "query_type": self._classify_query_type(query),
            "result_quality": interaction_quality["quality_score"],
            "response_relevance": interaction_quality["relevance_score"], 
            "user_satisfaction_predicted": interaction_quality["satisfaction_prediction"],
            "query_complexity": self._calculate_query_complexity(query),
            "result_count": len(result.get("results", [])),
            "has_recommendations": bool(result.get("intelligent_recommendations")),
            "timestamp": time.time(),
            "hour_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday()
        }
        
        # Add user context if available
        if user_context:
            performance_metrics.update({
                "user_type": user_context.get("user_type", "unknown"),
                "session_length": user_context.get("session_length", 0),
                "repeat_user": user_context.get("repeat_user", False)
            })
        
        # Store in analytics database
        analytics_document = f"{sector} {query} {result.get('status', 'unknown')}"
        
        self.analytics_col.add(
            documents=[analytics_document],
            metadatas=[performance_metrics],
            ids=[interaction_id]
        )
        
        # Update real-time performance tracking
        self.performance_tracker.update_sector_performance(sector, performance_metrics)
    
    def generate_real_time_dashboard(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive real-time analytics dashboard"""
        
        # Get recent interactions
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        recent_analytics = self.analytics_col.get(
            where={"timestamp": {"$gte": cutoff_time}},
            include=["metadatas"]
        )
        
        if not recent_analytics or not recent_analytics.get("metadatas"):
            return {"status": "no_data", "time_window_hours": time_window_hours}
        
        analytics_data = recent_analytics["metadatas"]
        
        # Generate comprehensive dashboard
        dashboard = {
            "overview": self._generate_overview_metrics(analytics_data),
            "sector_performance": self._analyze_sector_performance(analytics_data),
            "user_behavior_patterns": self._analyze_user_patterns(analytics_data),
            "query_analysis": self._analyze_query_patterns(analytics_data),
            "recommendations": self._generate_optimization_recommendations(analytics_data),
            "trending_sectors": self._identify_trending_sectors(analytics_data),
            "performance_alerts": self._detect_performance_issues(analytics_data),
            "time_window_hours": time_window_hours,
            "last_updated": datetime.now().isoformat()
        }
        
        return dashboard
    
    def _analyze_interaction_quality(self, query: str, result: Dict) -> Dict[str, float]:
        """Analyze the quality of an interaction"""
        
        quality_factors = {
            "query_clarity": self._assess_query_clarity(query),
            "result_relevance": self._assess_result_relevance(query, result),
            "completeness": self._assess_result_completeness(result)
        }
        
        # Calculate overall quality score
        quality_score = sum(quality_factors.values()) / len(quality_factors)
        
        # Predict user satisfaction based on result characteristics
        satisfaction_prediction = self._predict_user_satisfaction(result, quality_score)
        
        return {
            "quality_score": quality_score,
            "relevance_score": quality_factors["result_relevance"],
            "satisfaction_prediction": satisfaction_prediction,
            "quality_factors": quality_factors
        }
    
    def _assess_query_clarity(self, query: str) -> float:
        """Assess how clear and specific the query is"""
        clarity_score = 0.5  # Base score
        
        # Longer queries with specific terms tend to be clearer
        if len(query.split()) > 3:
            clarity_score += 0.2
        
        # Check for specific item mentions
        specific_terms = ["omelet", "bagel", "sandwich", "salad", "appointment", "repair", "haircut"]
        if any(term in query.lower() for term in specific_terms):
            clarity_score += 0.3
        
        # Penalize very vague queries
        vague_terms = ["something", "anything", "stuff", "thing"]
        if any(term in query.lower() for term in vague_terms):
            clarity_score -= 0.2
        
        return max(0.0, min(1.0, clarity_score))
    
    def _assess_result_relevance(self, query: str, result: Dict) -> float:
        """Assess how relevant the results are to the query"""
        if not result.get("results"):
            return 0.0
        
        # Check if results contain query terms
        query_terms = set(query.lower().split())
        relevance_scores = []
        
        for item in result["results"]:
            item_text = f"{item.get('item', '')} {item.get('category', '')}".lower()
            item_terms = set(item_text.split())
            
            # Calculate term overlap
            overlap = len(query_terms.intersection(item_terms))
            max_terms = max(len(query_terms), len(item_terms), 1)
            
            relevance = overlap / max_terms
            relevance_scores.append(relevance)
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    def _generate_sector_performance_report(self, sector: str, days: int = 7) -> Dict[str, Any]:
        """Generate detailed performance report for a specific sector"""
        
        cutoff_time = time.time() - (days * 24 * 3600)
        
        sector_analytics = self.analytics_col.get(
            where={
                "sector": sector,
                "timestamp": {"$gte": cutoff_time}
            },
            include=["metadatas"]
        )
        
        if not sector_analytics or not sector_analytics.get("metadatas"):
            return {"sector": sector, "status": "no_data", "days": days}
        
        analytics_data = sector_analytics["metadatas"]
        
        # Calculate key metrics
        total_interactions = len(analytics_data)
        avg_quality = sum(data.get("result_quality", 0) for data in analytics_data) / total_interactions
        avg_satisfaction = sum(data.get("user_satisfaction_predicted", 0) for data in analytics_data) / total_interactions
        
        # Analyze trends
        daily_metrics = self._calculate_daily_trends(analytics_data, days)
        
        # Identify top performing queries
        query_performance = self._analyze_query_performance(analytics_data)
        
        # Generate recommendations
        optimization_suggestions = self._generate_sector_optimizations(sector, analytics_data)
        
        return {
            "sector": sector,
            "time_period_days": days,
            "summary_metrics": {
                "total_interactions": total_interactions,
                "average_quality_score": round(avg_quality, 3),
                "average_satisfaction": round(avg_satisfaction, 3),
                "interactions_per_day": round(total_interactions / days, 1)
            },
            "daily_trends": daily_metrics,
            "top_queries": query_performance["top_performing"][:10],
            "problematic_queries": query_performance["low_performing"][:5],
            "optimization_suggestions": optimization_suggestions,
            "performance_grade": self._calculate_performance_grade(avg_quality, avg_satisfaction)
        }

# Integration with your existing MultiIntentDetector
class AnalyticsEnabledMultiIntentDetector(MultiIntentDetector):
    def __init__(self, indexer: UniversalMenuIndexer):
        super().__init__(indexer)
        self.analytics = RealTimeSectorAnalytics(indexer)
        
    def detect_intents_with_analytics(self, user_query: str, user_context: Dict = None) -> Dict[str, Any]:
        """Enhanced intent detection with analytics tracking"""
        
        # Get standard intent detection result
        result = super().detect_intents(user_query)
        
        # Track the interaction for analytics
        primary_sector = result.get("primary_sector", "unknown")
        self.analytics.track_sector_interaction(primary_sector, user_query, result, user_context)
        
        # Add real-time performance context
        sector_performance = self.analytics.performance_tracker.get_sector_stats(primary_sector)
        
        result["performance_context"] = {
            "sector_quality_score": sector_performance.get("avg_quality", 0),
            "sector_popularity_rank": sector_performance.get("popularity_rank", 0),
            "recent_performance_trend": sector_performance.get("trend", "stable")
        }
        
        return result

