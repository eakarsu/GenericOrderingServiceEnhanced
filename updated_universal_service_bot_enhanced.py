# Add to your updated_universal_service_bot.py
from updated_universal_service_bot import UniversalServiceBot,UniversalDatabaseClient
from typing import List, Dict, Any, Optional

class AdvancedConversationMemory:
    """Deep conversation memory with ChromaDB persistence"""
    def __init__(self, db_client: UniversalDatabaseClient):
        self.db_client = db_client
        self.conversation_col = self._get_or_create_conversation_collection()
        self.memory_patterns = ConversationPatternAnalyzer()
        self.context_builder = ContextualIntelligence()
        
    def _get_or_create_conversation_collection(self):
        """Create conversation memory collection"""
        try:
            return self.db_client.client.get_collection("conversation_memory", self.db_client.embedder)
        except:
            return self.db_client.client.create_collection("conversation_memory", embedding_function=self.db_client.embedder)
    
    def store_conversation_context(self, user_id: str, sector: str, conversation_data: Dict):
        """Store conversation with deep context analysis"""
        conversation_id = f"{user_id}_{sector}_{int(time.time())}"
        
        # Extract conversation patterns using your existing intent detection
        patterns = self.memory_patterns.analyze_conversation_patterns(conversation_data)
        
        # Build contextual metadata
        context_metadata = {
            "user_id": user_id,
            "sector": sector,
            "timestamp": time.time(),
            "conversation_length": len(conversation_data.get("messages", [])),
            "intent_progression": patterns.get("intent_flow", []),
            "user_preferences": patterns.get("preferences", {}),
            "completion_status": conversation_data.get("status", "ongoing"),
            "satisfaction_indicators": patterns.get("satisfaction_signals", []),
            "topics_covered": patterns.get("topics", []),
            "decision_points": patterns.get("decisions", [])
        }
        
        # Create searchable document
        conversation_summary = self._build_conversation_summary(conversation_data, patterns)
        
        self.conversation_col.add(
            documents=[conversation_summary],
            metadatas=[context_metadata],
            ids=[conversation_id]
        )
        
        return conversation_id
    
    def retrieve_relevant_context(self, user_id: str, current_query: str, sector: str = None) -> Dict:
        """Retrieve relevant conversation context for current query"""
        
        # Query similar conversations
        where_clause = {"user_id": user_id}
        if sector:
            where_clause["sector"] = sector
            
        similar_conversations = self.conversation_col.query(
            query_texts=[current_query],
            where=where_clause,
            n_results=5,
            include=["metadatas", "documents", "distances"]
        )
        
        # Build enhanced context
        enhanced_context = self.context_builder.build_context(
            similar_conversations, current_query, user_id
        )
        
        return enhanced_context
    
    def _build_conversation_summary(self, conversation_data: Dict, patterns: Dict) -> str:
        """Build searchable conversation summary"""
        messages = conversation_data.get("messages", [])
        
        # Extract key information
        user_requests = []
        ai_responses = []
        
        for msg in messages:
            if hasattr(msg, 'content'):
                if isinstance(msg, HumanMessage):
                    user_requests.append(msg.content[:100])  # First 100 chars
                elif isinstance(msg, AIMessage):
                    ai_responses.append(msg.content[:100])
        
        summary_parts = [
            f"User requests: {' | '.join(user_requests)}",
            f"Topics: {', '.join(patterns.get('topics', []))}",
            f"Preferences: {', '.join(patterns.get('preferences', {}).keys())}",
            f"Outcomes: {', '.join(patterns.get('decisions', []))}"
        ]
        
        return " ".join(summary_parts)

class ConversationPatternAnalyzer:
    """Analyze patterns in conversation data"""
    def __init__(self):
        self.preference_extractors = PreferenceExtractors()
        self.satisfaction_detectors = SatisfactionDetectors()
        
    def analyze_conversation_patterns(self, conversation_data: Dict) -> Dict:
        """Deep analysis of conversation patterns"""
        messages = conversation_data.get("messages", [])
        
        patterns = {
            "intent_flow": self._track_intent_progression(messages),
            "preferences": self._extract_user_preferences(messages),
            "satisfaction_signals": self._detect_satisfaction_indicators(messages),
            "topics": self._extract_conversation_topics(messages),
            "decisions": self._identify_decision_points(messages)
        }
        
        return patterns
    
    def _track_intent_progression(self, messages: List) -> List[str]:
        """Track how user intent evolves through conversation"""
        intent_progression = []
        
        for msg in messages:
            if hasattr(msg, 'content') and isinstance(msg, HumanMessage):
                # Use simple pattern matching for intent tracking
                content = msg.content.lower()
                
                if any(word in content for word in ["i want", "i need", "looking for"]):
                    intent_progression.append("seeking")
                elif any(word in content for word in ["yes", "okay", "sounds good"]):
                    intent_progression.append("agreeing")
                elif any(word in content for word in ["no", "not", "different"]):
                    intent_progression.append("rejecting")
                elif any(word in content for word in ["how much", "cost", "price"]):
                    intent_progression.append("pricing")
                elif any(word in content for word in ["when", "time", "schedule"]):
                    intent_progression.append("scheduling")
        
        return intent_progression
    
    def _extract_user_preferences(self, messages: List) -> Dict:
        """Extract user preferences from conversation"""
        preferences = {}
        
        for msg in messages:
            if hasattr(msg, 'content') and isinstance(msg, HumanMessage):
                content = msg.content.lower()
                
                # Extract preference patterns
                if "prefer" in content:
                    pref_match = re.search(r'prefer (.+?)(?:\.|$)', content)
                    if pref_match:
                        preferences["preference"] = pref_match.group(1).strip()
                
                if "favorite" in content:
                    fav_match = re.search(r'favorite (.+?)(?:\.|$)', content)
                    if fav_match:
                        preferences["favorite"] = fav_match.group(1).strip()
                
                # Time preferences
                if any(time_word in content for time_word in ["morning", "afternoon", "evening"]):
                    for time_word in ["morning", "afternoon", "evening"]:
                        if time_word in content:
                            preferences["time_preference"] = time_word
                            break
        
        return preferences

# Integration into UniversalServiceBot
class EnhancedUniversalServiceBot(UniversalServiceBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_memory = AdvancedConversationMemory(self.db_client)
        self.learning_engine = ContinuousLearningEngine(self.db_client)
        self.personalization = PersonalizationEngine()
        
    def enhanced_chatAway_with_memory(self, user_input: str, user_id: str = None, 
                                    detected_sector: str = None) -> Dict[str, Any]:
        """Enhanced chatAway with conversation memory"""
        
        # Retrieve conversation context
        context = {}
        if user_id:
            context = self.conversation_memory.retrieve_relevant_context(
                user_id, user_input, detected_sector
            )
        
        # Get base response using existing chatAway
        base_response = self.chatAway(user_input, detected_sector, self.state["chat_history"])
        
        # Enhance response with memory context
        if context.get("relevant_preferences"):
            personalized_response = self.personalization.personalize_response(
                base_response, context["relevant_preferences"]
            )
        else:
            personalized_response = base_response
        
        # Store conversation for future learning
        if user_id:
            conversation_data = {
                "messages": self.state["chat_history"] + [
                    HumanMessage(content=user_input),
                    AIMessage(content=personalized_response)
                ],
                "status": "ongoing"
            }
            
            self.conversation_memory.store_conversation_context(
                user_id, detected_sector or "unknown", conversation_data
            )
        
        return {
            "response": personalized_response,
            "context_used": context,
            "memory_stored": bool(user_id),
            "sector": detected_sector
        }

