# Add to your updated_universal_service_bot.py

class AdvancedErrorHandler:
    """Comprehensive error handling and recovery system"""
    
    def __init__(self, db_client: UniversalDatabaseClient):
        self.db_client = db_client
        self.error_patterns = ErrorPatternAnalyzer()
        self.recovery_strategies = RecoveryStrategyManager()
        self.circuit_breaker = CircuitBreaker()
        self.error_learning = ErrorLearningSystem()
        
    def handle_with_intelligent_recovery(self, func, context: Dict[str, Any], *args, **kwargs):
        """Intelligent error handling with learning and recovery"""
        operation_id = f"{func.__name__}_{int(time.time())}"
        
        try:
            # Check circuit breaker
            if self.circuit_breaker.is_open(func.__name__):
                return self._circuit_breaker_fallback(func.__name__, context)
            
            # Execute with monitoring
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record success
            self.circuit_breaker.record_success(func.__name__)
            self._record_successful_operation(operation_id, func.__name__, execution_time, context)
            
            return result
            
        except Exception as e:
            # Record failure
            self.circuit_breaker.record_failure(func.__name__)
            error_context = self._build_error_context(e, func.__name__, context, *args, **kwargs)
            
            # Analyze error pattern
            error_analysis = self.error_patterns.analyze_error(e, error_context)
            
            # Attempt intelligent recovery
            recovery_result = self.recovery_strategies.attempt_recovery(
                error_analysis, func, context, *args, **kwargs
            )
            
            # Learn from this error
            self.error_learning.record_error_outcome(error_analysis, recovery_result)
            
            return recovery_result
    
    def _build_error_context(self, error: Exception, func_name: str, context: Dict, *args, **kwargs) -> Dict:
        """Build comprehensive error context for analysis"""
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "function_name": func_name,
            "user_context": context,
            "args_summary": str(args)[:200],
            "kwargs_summary": str(kwargs)[:200],
            "timestamp": time.time(),
            "stack_trace": traceback.format_exc()[-500:],  # Last 500 chars
            "sector": context.get("sector", "unknown"),
            "user_id": context.get("user_id"),
            "session_state": context.get("session_state", {})
        }

class ErrorPatternAnalyzer:
    """Analyze error patterns to identify root causes"""
    
    def __init__(self):
        self.error_history = []
        self.pattern_cache = {}
        
    def analyze_error(self, error: Exception, context: Dict) -> Dict[str, Any]:
        """Analyze error and identify patterns"""
        error_signature = self._create_error_signature(error, context)
        
        # Check for known patterns
        if error_signature in self.pattern_cache:
            pattern_info = self.pattern_cache[error_signature]
            pattern_info["occurrence_count"] += 1
            pattern_info["last_seen"] = time.time()
        else:
            pattern_info = {
                "signature": error_signature,
                "error_type": type(error).__name__,
                "likely_cause": self._identify_likely_cause(error, context),
                "severity": self._assess_error_severity(error, context),
                "recovery_difficulty": self._assess_recovery_difficulty(error, context),
                "occurrence_count": 1,
                "first_seen": time.time(),
                "last_seen": time.time()
            }
            self.pattern_cache[error_signature] = pattern_info
        
        return {
            "pattern_info": pattern_info,
            "error_context": context,
            "recommended_strategy": self._recommend_recovery_strategy(pattern_info, error, context)
        }
    
    def _identify_likely_cause(self, error: Exception, context: Dict) -> str:
        """Identify likely cause based on error type and context"""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Database-related errors
        if "connection" in error_msg or "database" in error_msg:
            return "database_connectivity"
        elif "timeout" in error_msg:
            return "network_timeout"
        elif "not found" in error_msg and context.get("sector"):
            return "missing_sector_data"
        elif "openrouter" in error_msg or "api" in error_msg:
            return "external_api_failure"
        elif "json" in error_msg or "parse" in error_msg:
            return "data_format_error"
        elif error_type == "KeyError":
            return "missing_required_data"
        elif error_type == "ValueError":
            return "invalid_input_data"
        else:
            return "unknown_error"

class RecoveryStrategyManager:
    """Manage different recovery strategies for different error types"""
    
    def __init__(self):
        self.strategy_registry = self._initialize_strategies()
        self.fallback_responses = self._initialize_fallback_responses()
        
    def attempt_recovery(self, error_analysis: Dict, func, context: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Attempt recovery using appropriate strategy"""
        likely_cause = error_analysis["pattern_info"]["likely_cause"]
        recommended_strategy = error_analysis["recommended_strategy"]
        
        print(f"🔧 Attempting recovery for: {likely_cause} using strategy: {recommended_strategy}")
        
        if recommended_strategy in self.strategy_registry:
            try:
                return self.strategy_registry[recommended_strategy](error_analysis, func, context, *args, **kwargs)
            except Exception as recovery_error:
                print(f"❌ Recovery strategy failed: {recovery_error}")
                return self._ultimate_fallback(context, likely_cause)
        else:
            return self._ultimate_fallback(context, likely_cause)
    
    def _initialize_strategies(self) -> Dict:
        """Initialize recovery strategies"""
        return {
            "database_retry": self._database_retry_strategy,
            "cache_fallback": self._cache_fallback_strategy,
            "simplified_response": self._simplified_response_strategy,
            "user_clarification": self._user_clarification_strategy,
            "alternative_sector": self._alternative_sector_strategy,
            "graceful_degradation": self._graceful_degradation_strategy
        }
    
    def _database_retry_strategy(self, error_analysis: Dict, func, context: Dict, *args, **kwargs) -> Dict:
        """Retry database operations with exponential backoff"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                
                # Retry the original function
                result = func(*args, **kwargs)
                return {
                    "status": "recovered",
                    "strategy": "database_retry",
                    "attempt": attempt + 1,
                    "result": result
                }
            except Exception as retry_error:
                if attempt == max_retries - 1:
                    return self._cache_fallback_strategy(error_analysis, func, context, *args, **kwargs)
                continue
    
    def _cache_fallback_strategy(self, error_analysis: Dict, func, context: Dict, *args, **kwargs) -> Dict:
        """Use cached data when database is unavailable"""
        sector = context.get("sector", "unknown")
        user_input = args[0] if args else "unknown"
        
        # Try to provide a cached or simplified response
        return {
            "status": "fallback_mode",
            "strategy": "cache_fallback",
            "response": f"I'm experiencing technical difficulties, but I can still help you with {sector.replace('_', ' ')}. Could you tell me more specifically what you need?",
            "user_guidance": "Please try being more specific about your request.",
            "retry_suggested": True
        }
    
    def _user_clarification_strategy(self, error_analysis: Dict, func, context: Dict, *args, **kwargs) -> Dict:
        """Ask user for clarification when processing fails"""
        sector = context.get("sector", "unknown")
        user_input = args[0] if args else ""
        
        clarification_prompts = [
            f"I want to help you with {sector.replace('_', ' ')}, but I need a bit more information. Could you be more specific?",
            f"I'm having trouble understanding your request about {sector.replace('_', ' ')}. Could you rephrase that?",
            f"Let me help you better with {sector.replace('_', ' ')}. What exactly are you looking for?"
        ]
        
        import random
        prompt = random.choice(clarification_prompts)
        
        return {
            "status": "needs_clarification",
            "strategy": "user_clarification",
            "response": prompt,
            "suggestions": self._generate_sector_suggestions(sector),
            "original_query": user_input
        }

class CircuitBreaker:
    """Circuit breaker pattern for preventing cascade failures"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_counts = {}
        self.last_failure_times = {}
        self.states = {}  # "closed", "open", "half_open"
        
    def is_open(self, operation: str) -> bool:
        """Check if circuit breaker is open for this operation"""
        if operation not in self.states:
            self.states[operation] = "closed"
            return False
        
        if self.states[operation] == "open":
            # Check if timeout has passed
            if time.time() - self.last_failure_times[operation] > self.timeout:
                self.states[operation] = "half_open"
                return False
            return True
        
        return False
    
    def record_failure(self, operation: str):
        """Record a failure for this operation"""
        self.failure_counts[operation] = self.failure_counts.get(operation, 0) + 1
        self.last_failure_times[operation] = time.time()
        
        if self.failure_counts[operation] >= self.failure_threshold:
            self.states[operation] = "open"
            print(f"🚨 Circuit breaker OPENED for {operation}")
    
    def record_success(self, operation: str):
        """Record a success for this operation"""
        if operation in self.failure_counts:
            self.failure_counts[operation] = 0
        
        if self.states.get(operation) == "half_open":
            self.states[operation] = "closed"
            print(f"✅ Circuit breaker CLOSED for {operation}")

# Integration into your existing UniversalServiceBot
class EnhancedUniversalServiceBot(UniversalServiceBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_handler = AdvancedErrorHandler(self.db_client)
        self.cross_sector_intelligence = CrossSectorIntelligence(self.db_client)
        self.user_journey_tracker = UserJourneyTracker()
        
    def enhanced_chatAway(self, user_input: str, user_id: str = None, 
                         detected_sector: str = None, session_context: Dict = None) -> Dict[str, Any]:
        """Enhanced chatAway with comprehensive error handling"""
        
        # Build comprehensive context
        context = {
            "user_id": user_id,
            "sector": detected_sector,
            "session_context": session_context or {},
            "user_input": user_input,
            "timestamp": time.time()
        }
        
        # Execute with advanced error handling
        result = self.error_handler.handle_with_intelligent_recovery(
            self._execute_enhanced_chat,
            context,
            user_input, user_id, detected_sector, session_context
        )
        
        # Track user journey
        if user_id:
            self.user_journey_tracker.track_interaction(user_id, user_input, result, context)
        
        return result
    
    def _execute_enhanced_chat(self, user_input: str, user_id: str, 
                              detected_sector: str, session_context: Dict) -> Dict[str, Any]:
        """Execute the actual chat logic (can fail and be recovered)"""
        # This is your existing chatAway logic but wrapped for error handling
        response = self.chatAway(user_input, detected_sector, self.state.get("chat_history", []))
        
        return {
            "status": "success",
            "response": response,
            "sector": detected_sector,
            "user_id": user_id,
            "enhanced_features": True
        }

