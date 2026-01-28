# Enhancement for your orderProcessor.py

class IntelligentOrderProcessor(OrderProcessor):
    def __init__(self, indexer):
        super().__init__(indexer)
        self.recommendation_engine = SmartRecommendationEngine(indexer)
        self.price_optimizer = PriceOptimizer()
        self.dietary_analyzer = DietaryPreferenceAnalyzer()
        self.order_history_analyzer = OrderHistoryAnalyzer()
        
    def process_intelligent_order(self, query: str, user_context: Dict = None) -> Dict[str, Any]:
        """Enhanced order processing with AI-powered suggestions"""
        
        # Get base order processing result
        base_result = super().process_order(query)
        
        if base_result.get("status") == "no_results":
            return self._handle_no_results_intelligently(query, user_context)
        
        # Enhance results with intelligent features
        enhanced_result = base_result.copy()
        
        # Add smart recommendations
        if enhanced_result.get("results"):
            enhanced_result = self._add_intelligent_recommendations(enhanced_result, query, user_context)
        
        # Add price optimization suggestions
        if enhanced_result.get("results"):
            enhanced_result = self._add_price_optimizations(enhanced_result, user_context)
        
        # Add dietary analysis
        if user_context and user_context.get("dietary_preferences"):
            enhanced_result = self._add_dietary_analysis(enhanced_result, user_context)
        
        return enhanced_result
    
    def _handle_no_results_intelligently(self, query: str, user_context: Dict) -> Dict[str, Any]:
        """Handle no results with intelligent suggestions"""
        
        # Try fuzzy matching with your existing indexer
        fuzzy_results = self._fuzzy_search_alternatives(query)
        
        if fuzzy_results:
            return {
                "status": "fuzzy_suggestions",
                "message": "I couldn't find exact matches, but here are similar options:",
                "suggestions": fuzzy_results,
                "original_query": query
            }
        
        # Try category-based suggestions
        category_suggestions = self._suggest_by_category(query)
        
        if category_suggestions:
            return {
                "status": "category_suggestions", 
                "message": "I couldn't find that specific item, but here are options from related categories:",
                "suggestions": category_suggestions,
                "original_query": query
            }
        
        # Try popular items as last resort
        popular_items = self._get_popular_items(user_context)
        
        return {
            "status": "popular_suggestions",
            "message": "I couldn't find that item, but here are some popular choices:",
            "suggestions": popular_items,
            "original_query": query
        }
    
    def _fuzzy_search_alternatives(self, query: str) -> List[Dict]:
        """Fuzzy search using your existing unified_search"""
        alternatives = []
        
        # Split query into words for individual searching
        query_words = query.split()
        
        for word in query_words:
            if len(word) > 3:  # Only search meaningful words
                word_results = self.unified_search(word)
                
                for result in word_results[:3]:  # Top 3 per word
                    if result.get("score", 1.0) < 1.2:  # Reasonable similarity
                        alternatives.append({
                            "name": result["name"],
                            "type": result.get("type", "item"),
                            "similarity_score": 1 - result.get("score", 1.0),
                            "metadata": result.get("metadata", {})
                        })
        
        # Remove duplicates and sort by similarity
        seen_names = set()
        unique_alternatives = []
        
        for alt in sorted(alternatives, key=lambda x: x["similarity_score"], reverse=True):
            if alt["name"] not in seen_names:
                seen_names.add(alt["name"])
                unique_alternatives.append(alt)
        
        return unique_alternatives[:5]  # Top 5 alternatives
    
    def _add_intelligent_recommendations(self, result: Dict, query: str, user_context: Dict) -> Dict:
        """Add intelligent recommendations to existing results"""
        
        recommendations = []
        
        # Get complementary items using your existing database
        for item in result.get("results", []):
            complements = self._find_complementary_items(item, user_context)
            recommendations.extend(complements)
        
        # Add upgrade suggestions
        for item in result.get("results", []):
            upgrades = self._find_upgrade_suggestions(item)
            recommendations.extend(upgrades)
        
        # Remove duplicates
        seen_items = {item["item"] for item in result.get("results", [])}
        unique_recommendations = []
        
        for rec in recommendations:
            if rec["name"] not in seen_items:
                seen_items.add(rec["name"])
                unique_recommendations.append(rec)
        
        result["intelligent_recommendations"] = unique_recommendations[:5]
        return result
    
    def _find_complementary_items(self, item: Dict, user_context: Dict) -> List[Dict]:
        """Find items that complement the selected item"""
        complements = []
        
        item_name = item.get("item", "")
        category = item.get("category", "")
        
        # Rule-based complementary logic
        complementary_rules = {
            "breakfast": ["coffee", "juice", "fruit"],
            "sandwich": ["chips", "soup", "salad", "drink"],
            "salad": ["dressing", "bread", "soup"],
            "burger": ["fries", "onion rings", "drink"],
            "bagel": ["cream cheese", "coffee", "orange juice"]
        }
        
        item_lower = item_name.lower()
        for food_type, suggested_complements in complementary_rules.items():
            if food_type in item_lower:
                for complement in suggested_complements:
                    complement_results = self.unified_search(complement)
                    for comp_result in complement_results[:2]:  # Top 2 per complement
                        if comp_result.get("score", 1.0) < 0.8:
                            complements.append({
                                "name": comp_result["name"],
                                "type": "complement",
                                "reason": f"Goes well with {item_name}",
                                "metadata": comp_result.get("metadata", {}),
                                "price": comp_result.get("metadata", {}).get("price", 0)
                            })
        
        return complements
    
    def _add_price_optimizations(self, result: Dict, user_context: Dict) -> Dict:
        """Add price optimization suggestions"""
        
        price_suggestions = []
        
        for item in result.get("results", []):
            item_price = item.get("price", 0)
            base_price = item.get("base_price", item_price)
            
            # Check if this item has expensive add-ons
            if "selected_rules" in item:
                rules_data = item["selected_rules"]
                if isinstance(rules_data, str):
                    try:
                        rules = json.loads(rules_data)
                    except:
                        rules = []
                else:
                    rules = rules_data or []
                
                if rules:  # Item has customization options
                    price_suggestions.append({
                        "type": "customization_savings",
                        "item": item["item"],
                        "message": f"Customize your {item['item']} to control the final price",
                        "base_price": base_price,
                        "estimated_range": f"${base_price:.2f} - ${base_price + 5:.2f}"
                    })
            
            # Suggest similar but cheaper alternatives
            if item_price > 8.0:  # For expensive items
                cheaper_alternatives = self._find_cheaper_alternatives(item)
                if cheaper_alternatives:
                    price_suggestions.append({
                        "type": "cheaper_alternative",
                        "item": item["item"],
                        "alternatives": cheaper_alternatives[:2],
                        "potential_savings": max(0, item_price - min(alt["price"] for alt in cheaper_alternatives))
                    })
        
        result["price_optimizations"] = price_suggestions
        return result
    
    def _find_cheaper_alternatives(self, item: Dict) -> List[Dict]:
        """Find cheaper alternatives to an item"""
        alternatives = []
        
        category = item.get("category", "")
        item_price = item.get("price", 0)
        
        if category:
            # Query items in same category
            try:
                category_items = self.indexer.items_col.get(
                    where={"category": category}
                )
                
                if category_items and category_items.get("documents"):
                    for i, doc in enumerate(category_items["documents"]):
                        meta = category_items["metadatas"][i]
                        alt_price = meta.get("price", 0)
                        
                        # Only suggest if it's cheaper and not the same item
                        if alt_price < item_price and doc != item.get("item"):
                            alternatives.append({
                                "name": doc,
                                "price": alt_price,
                                "savings": item_price - alt_price,
                                "category": meta.get("category", "")
                            })
            
            except Exception as e:
                print(f"[DEBUG] Error finding alternatives: {e}")
        
        return sorted(alternatives, key=lambda x: x["price"])[:3]

