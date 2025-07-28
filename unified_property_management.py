# ============================================================================
# FINAL SMART MULTI-FRAMEWORK PROPERTY MANAGEMENT SYSTEM
# OpenAI + Rule-Based + A2A Communication with Smart GPT Analysis
# ============================================================================

import asyncio
import nest_asyncio
import pandas as pd
from apify_client import ApifyClientAsync
import requests
import json
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from dotenv import load_dotenv
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional

load_dotenv()
nest_asyncio.apply()

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMAIL_CONFIG = {
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('GMAIL_APP_PASSWORD'),
    'cleaning_team_email': os.getenv('CLEANING_TEAM_EMAIL'),
    'demo_mode': False
}

LISTINGS = [
    ("Room N5 Downtown", "https://www.booking.com/hotel/ca/room-n5-in-a-shared-apartment-in-downtown-montreal.fr.html", 200),
    ("Room 1 Full Luxury", "https://www.booking.com/hotel/ca/room-1-full-equipped-in-big-luxury-apartment-in-downtown-montreal.fr.html", 300),
    ("Room 2 Luxury", "https://www.booking.com/hotel/ca/room-2-in-big-luxury-apartment-in-downtown-montreal.fr.html", 280),
    ("Room N3 Luxury", "https://www.booking.com/hotel/ca/room-n3-in-a-big-luxury-apartment-in-downtown-montreal.fr.html", 290),
    ("Room Shared A", "https://www.booking.com/hotel/ca/room-in-a-shared-apartment-in-downtown-montreal.fr.html", 150),
    ("Room Shared B", "https://www.booking.com/hotel/ca/room-in-shared-apartment-in-downtown-montreal.fr.html", 160),
    ("Room N7 Shared", "https://www.booking.com/hotel/ca/room-n7-in-a-shared-apartment-in-downtown-montreal.fr.html", 155),
]

# ============================================================================
# FRAMEWORK 1: SMART OPENAI AGENT - Analyzes EVERYTHING automatically
# ============================================================================

class SmartOpenAIAgent:
    """
    Smart OpenAI Agent that automatically detects ALL issues from guest comments
    No need for separate cleaning/maintenance functions - GPT is smart enough!
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agent_id = "smart_openai_agent"
        self.conversation_history = []
        self.performance_metrics = {"analyses_completed": 0, "confidence_avg": 0.0}
    
    def analyze_all_guest_feedback(self, positive_comments, negative_comments):
        """
        Smart unified analysis - GPT analyzes EVERYTHING automatically:
        cleaning, maintenance, AC, TV, bed, WiFi, satisfaction, pricing recommendations
        """
        if not positive_comments and not negative_comments:
            return self._empty_analysis()
        
        # Combine all comments for comprehensive analysis
        all_comments = []
        for i, comment in enumerate(positive_comments):
            all_comments.append(f"POSITIVE {i+1}: {comment}")
        for i, comment in enumerate(negative_comments):
            all_comments.append(f"NEGATIVE {i+1}: {comment}")
        
        comments_text = "\n".join(all_comments)
        
        # Smart GPT prompt - let GPT figure out everything
        smart_prompt = f"""
You are an expert property analyst. Analyze these REAL guest comments comprehensively.

GUEST COMMENTS:
{comments_text}

Provide a complete analysis in JSON format:
{{
    "satisfaction_score": "0-100 based on overall guest sentiment",
    "cleaning_issues": [
        {{
            "guest_comment": "exact guest quote",
            "problem": "specific cleaning issue (bathroom dirty, dust, stains, smell, etc.)",
            "location": "bathroom/kitchen/bedroom/general",
            "severity": "Low/Medium/High"
        }}
    ],
    "maintenance_issues": [
        {{
            "guest_comment": "exact guest quote",
            "problem": "specific maintenance issue (AC, TV, bed, WiFi, plumbing, electrical, etc.)",
            "category": "AC/TV/Bed/WiFi/Plumbing/Electrical/Noise/Other",
            "severity": "Low/Medium/High",
            "urgency": "Can wait/Soon/Urgent"
        }}
    ],
    "positive_highlights": [
        "things guests specifically loved about the property"
    ],
    "guest_sentiment": "overall emotional tone (very happy/satisfied/neutral/frustrated/angry)",
    "recommended_price_change": "percentage change from -25 to +20 based on satisfaction and issues",
    "summary": {{
        "main_problems": ["top 3 most mentioned issues"],
        "strongest_positives": ["top 2 things guests loved"],
        "immediate_actions": ["most urgent things to fix"],
        "overall_rating": "A/B/C/D/F grade for this property"
    }},
    "confidence": "0.0-1.0 confidence in this analysis"
}}

Be smart and comprehensive:
- Automatically detect ALL types of issues (cleaning, AC, TV, bed comfort, WiFi, plumbing, noise, etc.)
- Calculate satisfaction based on positive vs negative sentiment
- Recommend price changes based on guest feedback quality
- Identify what guests love most and what frustrates them most
- Give actionable insights for immediate improvement
"""
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert property management consultant with years of experience analyzing guest feedback. Provide comprehensive, actionable insights."
                        },
                        {
                            "role": "user",
                            "content": smart_prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                gpt_response = result["choices"][0]["message"]["content"].strip()
                
                try:
                    # Parse GPT's comprehensive analysis
                    analysis = json.loads(gpt_response)
                    
                    # Update performance metrics
                    self.performance_metrics["analyses_completed"] += 1
                    confidence = analysis.get("confidence", 0.5)
                    current_avg = self.performance_metrics["confidence_avg"]
                    count = self.performance_metrics["analyses_completed"]
                    self.performance_metrics["confidence_avg"] = (current_avg * (count-1) + confidence) / count
                    
                    # Log for learning
                    self.conversation_history.append({
                        "timestamp": datetime.now(),
                        "total_comments": len(all_comments),
                        "positive_count": len(positive_comments),
                        "negative_count": len(negative_comments),
                        "analysis": analysis,
                        "confidence": confidence
                    })
                    
                    return analysis
                    
                except json.JSONDecodeError:
                    print(f"GPT response wasn't valid JSON, using fallback")
                    return self._fallback_analysis(positive_comments, negative_comments)
                    
        except Exception as e:
            print(f"Error in smart GPT analysis: {e}")
            return self._fallback_analysis(positive_comments, negative_comments)
    
    def _fallback_analysis(self, positive_comments, negative_comments):
        """Simple fallback if GPT fails"""
        total = len(positive_comments) + len(negative_comments)
        if total == 0:
            return self._empty_analysis()
        
        satisfaction = (len(positive_comments) / total) * 100
        
        # Basic keyword detection
        cleaning_issues = []
        maintenance_issues = []
        
        all_negative = " ".join(negative_comments).lower()
        
        if any(word in all_negative for word in ['dirty', 'clean', 'dust', 'stain', 'smell', 'bathroom']):
            cleaning_issues.append({
                "guest_comment": "Multiple cleaning complaints detected",
                "problem": "General cleanliness issues",
                "location": "general",
                "severity": "Medium"
            })
        
        if any(word in all_negative for word in ['ac', 'tv', 'bed', 'wifi', 'broken', 'not working']):
            maintenance_issues.append({
                "guest_comment": "Multiple maintenance complaints detected", 
                "problem": "Equipment or facility issues",
                "category": "General",
                "severity": "Medium",
                "urgency": "Soon"
            })
        
        return {
            "satisfaction_score": satisfaction,
            "cleaning_issues": cleaning_issues,
            "maintenance_issues": maintenance_issues,
            "positive_highlights": positive_comments[:3] if positive_comments else [],
            "guest_sentiment": "neutral",
            "recommended_price_change": 0,
            "summary": {
                "main_problems": ["Analysis incomplete"],
                "overall_rating": "C"
            },
            "confidence": 0.4
        }
    
    def _empty_analysis(self):
        """Return empty analysis structure"""
        return {
            "satisfaction_score": 80,
            "cleaning_issues": [],
            "maintenance_issues": [],
            "positive_highlights": [],
            "guest_sentiment": "neutral",
            "recommended_price_change": 0,
            "summary": {"main_problems": [], "overall_rating": "B"},
            "confidence": 0.3
        }

# ============================================================================
# FRAMEWORK 2: RULE-BASED PRICING ENGINE - Transparent decisions
# ============================================================================

class RuleBasedPricingEngine:
    """
    Transparent rule-based pricing that combines GPT recommendations with business rules
    """
    
    def __init__(self):
        self.agent_id = "rule_based_pricing_engine"
        self.decision_history = []
        self.performance_metrics = {"decisions_made": 0, "avg_adjustment": 0.0}
        
        # Explicit business rules
        self.pricing_rules = {
            "satisfaction_bands": {
                (95, 100): {"base_adjustment": 0.15, "description": "Exceptional - premium pricing"},
                (90, 94): {"base_adjustment": 0.08, "description": "Excellent - price increase"},
                (85, 89): {"base_adjustment": 0.03, "description": "Good - small increase"},
                (80, 84): {"base_adjustment": 0.0, "description": "Average - maintain price"},
                (70, 79): {"base_adjustment": -0.08, "description": "Below average - reduce price"},
                (60, 69): {"base_adjustment": -0.15, "description": "Poor - significant reduction"},
                (0, 59): {"base_adjustment": -0.25, "description": "Critical - major reduction"}
            },
            "issue_penalties": {
                "high_severity_cleaning": -0.10,
                "medium_severity_cleaning": -0.05,
                "high_severity_maintenance": -0.08,
                "medium_severity_maintenance": -0.04,
                "multiple_issues": -0.03
            },
            "gpt_weight": 0.6,  # 60% weight to GPT recommendation, 40% to rules
            "max_total_adjustment": 0.25
        }
    
    def calculate_smart_pricing(self, property_name, gpt_analysis, base_price):
        """
        Smart pricing that combines GPT insights with transparent business rules
        """
        satisfaction_score = gpt_analysis.get("satisfaction_score", 80)
        gpt_price_rec = gpt_analysis.get("recommended_price_change", 0)
        cleaning_issues = gpt_analysis.get("cleaning_issues", [])
        maintenance_issues = gpt_analysis.get("maintenance_issues", [])
        confidence = gpt_analysis.get("confidence", 0.5)
        
        # Step 1: Rule-based adjustment from satisfaction
        rule_adjustment = 0.0
        rule_description = "No rule matched"
        
        for (min_score, max_score), rule in self.pricing_rules["satisfaction_bands"].items():
            if min_score <= satisfaction_score <= max_score:
                rule_adjustment = rule["base_adjustment"]
                rule_description = rule["description"]
                break
        
        # Step 2: Apply issue penalties
        issue_penalty = 0.0
        issue_details = []
        
        # Cleaning issue penalties
        high_cleaning = len([i for i in cleaning_issues if i.get("severity") == "High"])
        medium_cleaning = len([i for i in cleaning_issues if i.get("severity") == "Medium"])
        
        if high_cleaning > 0:
            penalty = self.pricing_rules["issue_penalties"]["high_severity_cleaning"]
            issue_penalty += penalty
            issue_details.append(f"High cleaning issues: {penalty:.1%}")
        
        if medium_cleaning > 0:
            penalty = self.pricing_rules["issue_penalties"]["medium_severity_cleaning"]
            issue_penalty += penalty
            issue_details.append(f"Medium cleaning issues: {penalty:.1%}")
        
        # Maintenance issue penalties
        high_maintenance = len([i for i in maintenance_issues if i.get("severity") == "High"])
        medium_maintenance = len([i for i in maintenance_issues if i.get("severity") == "Medium"])
        
        if high_maintenance > 0:
            penalty = self.pricing_rules["issue_penalties"]["high_severity_maintenance"]
            issue_penalty += penalty
            issue_details.append(f"High maintenance issues: {penalty:.1%}")
        
        if medium_maintenance > 0:
            penalty = self.pricing_rules["issue_penalties"]["medium_severity_maintenance"]
            issue_penalty += penalty
            issue_details.append(f"Medium maintenance issues: {penalty:.1%}")
        
        # Multiple issues penalty
        if len(cleaning_issues) > 0 and len(maintenance_issues) > 0:
            penalty = self.pricing_rules["issue_penalties"]["multiple_issues"]
            issue_penalty += penalty
            issue_details.append(f"Multiple issue types: {penalty:.1%}")
        
        # Step 3: Combine GPT recommendation with rules
        gpt_adjustment = gpt_price_rec / 100  # Convert percentage
        rule_total = rule_adjustment + issue_penalty
        
        # Weighted combination
        gpt_weight = self.pricing_rules["gpt_weight"]
        rule_weight = 1 - gpt_weight
        
        combined_adjustment = (gpt_adjustment * gpt_weight) + (rule_total * rule_weight)
        
        # Step 4: Apply confidence weighting
        combined_adjustment *= confidence
        
        # Step 5: Cap total adjustment
        max_adj = self.pricing_rules["max_total_adjustment"]
        combined_adjustment = max(-max_adj, min(max_adj, combined_adjustment))
        
        # Step 6: Calculate final pricing
        new_price = int(base_price * (1 + combined_adjustment))
        price_change = new_price - base_price
        percentage_change = combined_adjustment * 100
        
        # Step 7: Build decision record
        decision = {
            "property": property_name,
            "satisfaction_score": satisfaction_score,
            "base_price": base_price,
            "new_price": new_price,
            "price_change": price_change,
            "percentage_change": percentage_change,
            "gpt_recommendation": gpt_price_rec,
            "rule_adjustment": rule_total * 100,
            "final_adjustment": combined_adjustment * 100,
            "confidence": confidence,
            "rule_description": rule_description,
            "issue_penalties": issue_details,
            "decision_logic": {
                "gpt_weight": f"{gpt_weight:.0%}",
                "rule_weight": f"{rule_weight:.0%}",
                "confidence_applied": f"{confidence:.1%}"
            },
            "timestamp": datetime.now()
        }
        
        # Update metrics
        self.decision_history.append(decision)
        self.performance_metrics["decisions_made"] += 1
        current_avg = self.performance_metrics["avg_adjustment"]
        count = self.performance_metrics["decisions_made"]
        self.performance_metrics["avg_adjustment"] = (current_avg * (count-1) + abs(percentage_change)) / count
        
        return decision

# ============================================================================
# FRAMEWORK 3: A2A COMMUNICATION PROTOCOL - Inter-agent messaging
# ============================================================================

class A2ACommunicationLayer:
    """
    Structured agent-to-agent communication with full logging
    """
    
    def __init__(self):
        self.message_queue = []
        self.conversation_log = []
        self.registered_agents = {}
        
    def register_agent(self, agent_id: str, agent_instance):
        """Register an agent for communication"""
        self.registered_agents[agent_id] = {
            "instance": agent_instance,
            "inbox": [],
            "status": "active",
            "registered_at": datetime.now()
        }
        print(f"📡 A2A: Registered {agent_id}")
    
    def send_message(self, sender_id: str, recipient_id: str, message_type: str, payload: Dict[str, Any]) -> str:
        """Send structured message between agents"""
        message_id = f"a2a_{datetime.now().strftime('%H%M%S')}_{len(self.message_queue)}"
        
        message = {
            "id": message_id,
            "sender": sender_id,
            "recipient": recipient_id,
            "type": message_type,
            "payload": payload,
            "timestamp": datetime.now(),
            "status": "sent"
        }
        
        # Deliver message
        if recipient_id in self.registered_agents:
            self.registered_agents[recipient_id]["inbox"].append(message)
            message["status"] = "delivered"
            print(f"📤 A2A: {sender_id} → {recipient_id} ({message_type})")
        else:
            message["status"] = "failed"
            print(f"❌ A2A: Failed to deliver to {recipient_id}")
        
        self.message_queue.append(message)
        self.conversation_log.append(message)
        
        return message_id
    
    def get_messages(self, agent_id: str) -> List[Dict[str, Any]]:
        """Retrieve and clear messages for an agent"""
        if agent_id not in self.registered_agents:
            return []
        
        messages = self.registered_agents[agent_id]["inbox"].copy()
        self.registered_agents[agent_id]["inbox"].clear()
        
        return messages
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        if not self.conversation_log:
            return {"total_messages": 0}
        
        stats = {
            "total_messages": len(self.conversation_log),
            "by_sender": {},
            "by_type": {},
            "delivery_rate": 0,
            "recent_activity": []
        }
        
        delivered = 0
        for msg in self.conversation_log:
            # Count by sender
            sender = msg["sender"]
            stats["by_sender"][sender] = stats["by_sender"].get(sender, 0) + 1
            
            # Count by type
            msg_type = msg["type"]
            stats["by_type"][msg_type] = stats["by_type"].get(msg_type, 0) + 1
            
            # Count delivery success
            if msg["status"] == "delivered":
                delivered += 1
        
        stats["delivery_rate"] = (delivered / len(self.conversation_log)) * 100
        stats["recent_activity"] = self.conversation_log[-5:]  # Last 5 messages
        
        return stats

# ============================================================================
# LEARNING AND ADAPTATION SYSTEM
# ============================================================================

class CrossAgentLearningSystem:
    """
    Agents rate each other and adapt based on performance
    """
    
    def __init__(self):
        self.ratings = []
        self.adaptations = []
        
    def submit_rating(self, rater: str, rated: str, task: str, score: float, context: Dict[str, Any]):
        """Submit a rating from one agent to another"""
        rating = {
            "timestamp": datetime.now(),
            "rater": rater,
            "rated": rated,
            "task": task,
            "score": max(1.0, min(5.0, score)),  # 1-5 scale
            "context": context
        }
        
        self.ratings.append(rating)
        print(f"📊 Learning: {rater} rates {rated} = {score:.1f}/5.0 for {task}")
        
        # Check if adaptation needed
        recent_ratings = [r["score"] for r in self.ratings[-3:] if r["rated"] == rated and r["task"] == task]
        if len(recent_ratings) >= 2 and sum(recent_ratings) / len(recent_ratings) < 3.0:
            self._trigger_adaptation(rated, task, recent_ratings)
        
        return rating
    
    def _trigger_adaptation(self, agent: str, task: str, recent_scores: List[float]):
        """Trigger adaptation for underperforming agent"""
        avg_score = sum(recent_scores) / len(recent_scores)
        
        adaptation = {
            "timestamp": datetime.now(),
            "agent": agent,
            "task": task,
            "trigger_score": avg_score,
            "improvement_actions": []
        }
        
        if agent == "smart_openai_agent":
            adaptation["improvement_actions"] = [
                "Increase analysis confidence threshold",
                "Add more specific examples in prompts",
                "Request more detailed issue categorization"
            ]
        elif agent == "rule_based_pricing_engine":
            adaptation["improvement_actions"] = [
                "Adjust satisfaction score thresholds",
                "Recalibrate issue penalty weights",
                "Modify GPT-rule combination ratio"
            ]
        
        self.adaptations.append(adaptation)
        print(f"🔄 Learning: Adaptation triggered for {agent} (avg score: {avg_score:.1f})")
        
        return adaptation

# ============================================================================
# COMPREHENSIVE GUARDRAILS
# ============================================================================

class SystemGuardrails:
    """
    Safety systems to prevent failures and ensure reliability
    """
    
    def __init__(self):
        self.violations = []
        self.limits = {
            "max_price_change": 25,  # Max ±25% price change
            "max_api_calls_per_minute": 20,
            "max_cycle_iterations": 10,
            "min_confidence": 0.2
        }
        self.api_calls = []
        self.iteration_count = 0
    
    def check_pricing_safety(self, pricing_decision: Dict[str, Any]) -> bool:
        """Ensure pricing changes are safe"""
        change_pct = abs(pricing_decision.get("percentage_change", 0))
        
        if change_pct > self.limits["max_price_change"]:
            # Cap the change
            original = pricing_decision["base_price"]
            max_change = self.limits["max_price_change"] / 100
            
            if pricing_decision["percentage_change"] > 0:
                pricing_decision["new_price"] = int(original * (1 + max_change))
            else:
                pricing_decision["new_price"] = int(original * (1 - max_change))
            
            pricing_decision["percentage_change"] = self.limits["max_price_change"] * (1 if pricing_decision["percentage_change"] > 0 else -1)
            pricing_decision["guardrail_applied"] = True
            
            self._log_violation("price_change_capped", f"Capped change from {change_pct:.1f}% to {self.limits['max_price_change']}%")
        
        return True
    
    def check_api_limits(self) -> bool:
        """Prevent API overuse"""
        now = time.time()
        self.api_calls = [t for t in self.api_calls if now - t < 60]  # Last minute
        
        if len(self.api_calls) >= self.limits["max_api_calls_per_minute"]:
            self._log_violation("api_rate_limit", f"Hit API limit: {len(self.api_calls)} calls/minute")
            return False
        
        self.api_calls.append(now)
        return True
    
    def check_iteration_limit(self) -> bool:
        """Prevent infinite loops"""
        self.iteration_count += 1
        
        if self.iteration_count > self.limits["max_cycle_iterations"]:
            self._log_violation("iteration_limit", f"Exceeded {self.limits['max_cycle_iterations']} iterations")
            return False
        
        return True
    
    def _log_violation(self, violation_type: str, description: str):
        """Log safety violations"""
        violation = {
            "type": violation_type,
            "description": description,
            "timestamp": datetime.now()
        }
        self.violations.append(violation)
        print(f"🚨 GUARDRAIL: {violation_type} - {description}")
    
    def get_safety_report(self) -> Dict[str, Any]:
        """Get comprehensive safety report"""
        return {
            "total_violations": len(self.violations),
            "violation_types": list(set(v["type"] for v in self.violations)),
            "recent_violations": self.violations[-3:],
            "current_limits": self.limits,
            "api_calls_last_minute": len([t for t in self.api_calls if time.time() - t < 60])
        }

# ============================================================================
# MAIN SMART PROPERTY MANAGER - Orchestrates everything
# ============================================================================

class SmartPropertyManager:
    """
    Final smart property manager with multi-framework integration
    """
    
    def __init__(self):
        # Core data
        self.base_pricing = {name: price for name, url, price in LISTINGS}
        self.satisfaction_scores = {}
        self.detailed_analyses = {}  # Store full GPT analyses
        self.pricing_decisions = {}
        self.review_data = None
        
        # Multi-framework components
        self.smart_ai = SmartOpenAIAgent(OPENAI_API_KEY)
        self.pricing_engine = RuleBasedPricingEngine()
        self.communication = A2ACommunicationLayer()
        self.learning_system = CrossAgentLearningSystem()
        self.guardrails = SystemGuardrails()
        
        # Register for A2A communication
        self.communication.register_agent("smart_ai", self.smart_ai)
        self.communication.register_agent("pricing_engine", self.pricing_engine)
        self.communication.register_agent("coordinator", self)
        
        print("🚀 SMART MULTI-FRAMEWORK PROPERTY MANAGEMENT SYSTEM")
        print(f"🏠 Portfolio: {len(LISTINGS)} properties")
        print(f"🧠 Smart AI: GPT-4 analyzes everything automatically")
        print(f"⚙️ Rule Engine: Transparent pricing decisions")
        print(f"📡 A2A Protocol: Structured agent communication")
        print(f"🛡️ Guardrails: Comprehensive safety systems")
    
    async def fetch_reviews(self, name, url):
        """Fetch reviews with API safety"""
        if not self.guardrails.check_api_limits():
            print(f"⏳ API limit hit, waiting...")
            await asyncio.sleep(15)
        
        client = ApifyClientAsync(APIFY_API_KEY)
        actor = client.actor("voyager/booking-reviews-scraper")
        
        try:
            run = await actor.call(
                run_input={
                    "startUrls": [{"url": url}],
                    "maxReviewsPerHotel": 50,  # Limit for demo
                    "proxyConfiguration": {"useApifyProxy": True}
                },
                wait_secs=180
            )
            
            print(f"✅ Reviews fetched: {name}")
            
            dataset = client.dataset(run["defaultDatasetId"])
            result = await dataset.list_items()
            items = result.items or []
            
            reviews = []
            for item in items:
                date = (item.get("reviewDate") or "").split("T")[0]
                
                if item.get("likedText"):
                    reviews.append({
                        "listing": name,
                        "date": date,
                        "type": "positive",
                        "comment": item["likedText"]
                    })
                
                if item.get("dislikedText"):
                    reviews.append({
                        "listing": name,
                        "date": date,
                        "type": "negative", 
                        "comment": item["dislikedText"]
                    })
            
            return reviews
            
        except Exception as e:
            print(f"❌ Error fetching {name}: {e}")
            return []
    
    async def run_smart_analysis(self):
        """
        Run complete smart analysis with all frameworks
        """
        cycle_id = f"smart_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("\n🧠 SMART MULTI-FRAMEWORK ANALYSIS STARTING")
        print("=" * 70)
        print(f"🆔 Cycle: {cycle_id}")
        
        # Step 1: Fetch all reviews
        print(f"\n📋 STEP 1: FETCHING GUEST REVIEWS")
        print("-" * 40)
        
        all_reviews = []
        for name, url, base_price in LISTINGS:
            if not self.guardrails.check_iteration_limit():
                print("⚠️ Iteration limit reached")
                break
            
            print(f"🔄 Fetching: {name}")
            reviews = await self.fetch_reviews(name, url)
            all_reviews.extend(reviews)
        
        if not all_reviews:
            print("⚠️ No reviews collected")
            return {"error": "No reviews", "cycle_id": cycle_id}
        
        self.review_data = pd.DataFrame(all_reviews)
        print(f"✅ Collected {len(all_reviews)} reviews from {self.review_data['listing'].nunique()} properties")
        
        # Step 2: Smart GPT Analysis for each property
        print(f"\n🧠 STEP 2: SMART GPT ANALYSIS")
        print("-" * 40)
        
        for property_name in self.review_data['listing'].unique():
            property_data = self.review_data[self.review_data['listing'] == property_name]
            positive_comments = property_data[property_data['type'] == 'positive']['comment'].tolist()
            negative_comments = property_data[property_data['type'] == 'negative']['comment'].tolist()
            
            print(f"\n🏠 Analyzing: {property_name}")
            print(f"   📊 {len(positive_comments)} positive, {len(negative_comments)} negative comments")
            
            # Smart GPT analyzes EVERYTHING automatically
            gpt_analysis = self.smart_ai.analyze_all_guest_feedback(positive_comments, negative_comments)
            
            satisfaction_score = gpt_analysis.get("satisfaction_score", 80)
            self.satisfaction_scores[property_name] = satisfaction_score
            self.detailed_analyses[property_name] = gpt_analysis
            
            print(f"   🎯 Satisfaction: {satisfaction_score:.1f}%")
            print(f"   🧹 Cleaning issues: {len(gpt_analysis.get('cleaning_issues', []))}")
            print(f"   🔧 Maintenance issues: {len(gpt_analysis.get('maintenance_issues', []))}")
            print(f"   💭 Guest sentiment: {gpt_analysis.get('guest_sentiment', 'neutral')}")
            print(f"   🤖 GPT confidence: {gpt_analysis.get('confidence', 0.5):.2f}")
            
            # Send analysis via A2A to pricing engine
            message_id = self.communication.send_message(
                sender_id="smart_ai",
                recipient_id="pricing_engine",
                message_type="COMPREHENSIVE_ANALYSIS",
                payload={
                    "property": property_name,
                    "analysis": gpt_analysis,
                    "base_price": self.base_pricing[property_name]
                }
            )
            print(f"   📤 A2A message sent: {message_id}")
        
        # Step 3: Rule-based pricing decisions
        print(f"\n⚙️ STEP 3: SMART PRICING DECISIONS")
        print("-" * 40)
        
        pricing_messages = self.communication.get_messages("pricing_engine")
        total_revenue_impact = 0
        
        for message in pricing_messages:
            if message["type"] == "COMPREHENSIVE_ANALYSIS":
                payload = message["payload"]
                property_name = payload["property"]
                gpt_analysis = payload["analysis"]
                base_price = payload["base_price"]
                
                # Rule-based pricing decision
                pricing_decision = self.pricing_engine.calculate_smart_pricing(
                    property_name, gpt_analysis, base_price
                )
                
                # Apply guardrails
                self.guardrails.check_pricing_safety(pricing_decision)
                
                self.pricing_decisions[property_name] = pricing_decision
                
                if abs(pricing_decision["price_change"]) >= 5:  # Significant change
                    total_revenue_impact += pricing_decision["price_change"]
                    
                    trend = "📈" if pricing_decision["price_change"] > 0 else "📉"
                    guardrail_note = " (CAPPED)" if pricing_decision.get("guardrail_applied") else ""
                    
                    print(f"\n🏠 {property_name}:")
                    print(f"   💰 ${pricing_decision['base_price']} → ${pricing_decision['new_price']} ({pricing_decision['percentage_change']:+.1f}%) {trend}{guardrail_note}")
                    print(f"   🤖 GPT recommended: {pricing_decision['gpt_recommendation']:+.0f}%")
                    print(f"   ⚙️ Rule adjustment: {pricing_decision['rule_adjustment']:+.1f}%")
                    print(f"   🎯 Final decision: {pricing_decision['rule_description']}")
                    print(f"   🔒 Confidence: {pricing_decision['confidence']:.2f}")
                else:
                    print(f"\n🏠 {property_name}: ${base_price} (no significant change needed)")
        
        print(f"\n💵 Total Revenue Impact: ${total_revenue_impact:+.0f} per night")
        print(f"📅 Monthly Projection: ${total_revenue_impact * 30:+.0f}")
        
        # Step 4: Cross-agent learning
        print(f"\n🧠 STEP 4: CROSS-AGENT LEARNING")
        print("-" * 40)
        
        # Smart AI rates Pricing Engine
        for property_name, pricing_decision in self.pricing_decisions.items():
            gpt_analysis = self.detailed_analyses[property_name]
            gpt_rec = gpt_analysis.get("recommended_price_change", 0)
            final_change = pricing_decision["percentage_change"]
            
            # Rate based on how well pricing engine incorporated GPT insights
            if abs(final_change - gpt_rec) <= 5:
                ai_rating = 4.5  # Good alignment
            elif abs(final_change - gpt_rec) <= 10:
                ai_rating = 3.5  # Reasonable alignment
            else:
                ai_rating = 2.5  # Poor alignment
            
            self.learning_system.submit_rating(
                rater="smart_ai",
                rated="pricing_engine",
                task="pricing_decisions",
                score=ai_rating,
                context={
                    "property": property_name,
                    "gpt_recommendation": gpt_rec,
                    "final_decision": final_change,
                    "reasoning": f"GPT suggested {gpt_rec:+.0f}%, engine decided {final_change:+.1f}%"
                }
            )
        
        # Pricing Engine rates Smart AI
        for property_name, gpt_analysis in self.detailed_analyses.items():
            confidence = gpt_analysis.get("confidence", 0.5)
            issue_count = len(gpt_analysis.get("cleaning_issues", [])) + len(gpt_analysis.get("maintenance_issues", []))
            
            # Rate based on analysis quality
            if confidence > 0.8 and issue_count >= 0:
                pricing_rating = 4.5  # High confidence, good analysis
            elif confidence > 0.6:
                pricing_rating = 3.5  # Good analysis
            else:
                pricing_rating = 2.5  # Low confidence
            
            self.learning_system.submit_rating(
                rater="pricing_engine",
                rated="smart_ai",
                task="comprehensive_analysis",
                score=pricing_rating,
                context={
                    "property": property_name,
                    "confidence": confidence,
                    "issues_detected": issue_count,
                    "reasoning": f"Analysis confidence {confidence:.2f}, detected {issue_count} issues"
                }
            )
        
        # Step 5: Send smart notifications
        print(f"\n📧 STEP 5: SMART NOTIFICATIONS")
        print("-" * 40)
        
        emails_sent = 0
        
        # Cleaning alerts
        cleaning_properties = {name: analysis["cleaning_issues"] for name, analysis in self.detailed_analyses.items() if analysis.get("cleaning_issues")}
        if cleaning_properties:
            if self.send_smart_cleaning_alert(cleaning_properties):
                emails_sent += 1
                print(f"✅ Smart cleaning alert sent ({len(cleaning_properties)} properties)")
        
        # Maintenance alerts
        maintenance_properties = {name: analysis["maintenance_issues"] for name, analysis in self.detailed_analyses.items() if analysis.get("maintenance_issues")}
        if maintenance_properties:
            if self.send_smart_maintenance_alert(maintenance_properties):
                emails_sent += 1
                print(f"✅ Smart maintenance alert sent ({len(maintenance_properties)} properties)")
        
        # Pricing report
        significant_pricing_changes = {name: decision for name, decision in self.pricing_decisions.items() if abs(decision.get("price_change", 0)) >= 5}
        if significant_pricing_changes:
            if self.send_smart_pricing_report(significant_pricing_changes):
                emails_sent += 1
                print(f"✅ Smart pricing report sent ({len(significant_pricing_changes)} adjustments)")
        
        # Step 6: Final summary
        print(f"\n📋 FINAL SMART ANALYSIS SUMMARY")
        print("=" * 70)
        print(f"🆔 Cycle: {cycle_id}")
        print(f"🏠 Properties Analyzed: {len(self.satisfaction_scores)}")
        print(f"📈 Average Satisfaction: {sum(self.satisfaction_scores.values()) / len(self.satisfaction_scores):.1f}%")
        print(f"🧹 Properties with Cleaning Issues: {len(cleaning_properties)}")
        print(f"🔧 Properties with Maintenance Issues: {len(maintenance_properties)}")
        print(f"💰 Significant Pricing Changes: {len(significant_pricing_changes)}")
        print(f"💵 Revenue Impact: ${total_revenue_impact:+.0f} per night")
        print(f"📧 Emails Sent: {emails_sent}")
        
        # Multi-framework performance
        ai_performance = self.smart_ai.performance_metrics
        pricing_performance = self.pricing_engine.performance_metrics
        comm_stats = self.communication.get_communication_stats()
        safety_report = self.guardrails.get_safety_report()
        
        print(f"\n🤖 MULTI-FRAMEWORK PERFORMANCE:")
        print(f"   🧠 Smart AI: {ai_performance['analyses_completed']} analyses, avg confidence {ai_performance['confidence_avg']:.2f}")
        print(f"   ⚙️ Pricing Engine: {pricing_performance['decisions_made']} decisions, avg adjustment {pricing_performance['avg_adjustment']:.1f}%")
        print(f"   📡 A2A Messages: {comm_stats['total_messages']} sent, {comm_stats.get('delivery_rate', 100):.0f}% delivered")
        print(f"   🛡️ Safety Violations: {safety_report['total_violations']}")
        print(f"   🧠 Learning Events: {len(self.learning_system.adaptations)} adaptations triggered")
        
        print("=" * 70)
        
        return {
            "cycle_id": cycle_id,
            "properties_analyzed": len(self.satisfaction_scores),
            "average_satisfaction": sum(self.satisfaction_scores.values()) / len(self.satisfaction_scores) if self.satisfaction_scores else 0,
            "cleaning_issues": len(cleaning_properties),
            "maintenance_issues": len(maintenance_properties),
            "pricing_adjustments": len(significant_pricing_changes),
            "revenue_impact": total_revenue_impact,
            "emails_sent": emails_sent,
            "detailed_cleaning_data": cleaning_properties,
            "detailed_maintenance_data": maintenance_properties,
            "framework_performance": {
                "smart_ai_analyses": ai_performance["analyses_completed"],
                "pricing_decisions": pricing_performance["decisions_made"],
                "a2a_messages": comm_stats["total_messages"],
                "learning_events": len(self.learning_system.adaptations),
                "safety_violations": safety_report["total_violations"]
            }
        }
    
    def send_email(self, subject, content, recipient):
        """Send email with error handling"""
        if EMAIL_CONFIG['demo_mode']:
            print(f"📝 DEMO: Email would be sent to {recipient}")
            return True
        
        try:
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = recipient
            
            context = ssl.create_default_context()
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls(context=context)
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                server.send_message(msg)
            
            print(f"✅ Email sent to {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False
    
    def send_smart_cleaning_alert(self, cleaning_properties):
        """Send smart cleaning alert with GPT insights"""
        if not cleaning_properties:
            return False
        
        subject = f"🧹 SMART CLEANING ALERT - {len(cleaning_properties)} Properties Need Attention"
        
        content = f"""Hi Mourad,

Our Smart AI System analyzed guest reviews and detected cleaning issues:

SMART CLEANING ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for property_name, issues in cleaning_properties.items():
            content += f"🏠 {property_name} ({len(issues)} issues detected by AI):\n\n"
            
            for i, issue in enumerate(issues, 1):
                severity = issue.get('severity', 'Medium')
                location = issue.get('location', 'general')
                problem = issue.get('problem', 'cleaning issue')
                guest_comment = issue.get('guest_comment', '')
                
                severity_emoji = "🚨" if severity == "High" else "⚠️" if severity == "Medium" else "ℹ️"
                
                content += f"   {i}. {severity_emoji} {severity} Priority - {location.title()}\n"
                content += f"      Problem: {problem}\n"
                content += f"      Guest said: \"{guest_comment[:120]}{'...' if len(guest_comment) > 120 else ''}\"\n\n"
        
        content += f"""
AI RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Focus on HIGH priority issues first (🚨)
• Pay special attention to bathroom and kitchen areas
• Address guest-mentioned specific problems
• Total Properties: {len(cleaning_properties)}
• Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

This analysis was performed by GPT-4 AI analyzing real guest feedback.

- Smart Property Management System"""
        
        return self.send_email(subject, content, EMAIL_CONFIG['cleaning_team_email'])
    
    def send_smart_maintenance_alert(self, maintenance_properties):
        """Send smart maintenance alert with detailed breakdown"""
        if not maintenance_properties:
            return False
        
        subject = f"🔧 SMART MAINTENANCE ALERT - {len(maintenance_properties)} Properties Need Service"
        
        content = f"""Hi Ahmed,

Smart AI analysis of guest reviews found maintenance issues:

SMART MAINTENANCE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for property_name, issues in maintenance_properties.items():
            content += f"🏠 {property_name}:\n\n"
            
            for i, issue in enumerate(issues, 1):
                category = issue.get('category', 'General')
                severity = issue.get('severity', 'Medium')
                urgency = issue.get('urgency', 'Soon')
                problem = issue.get('problem', 'maintenance needed')
                guest_comment = issue.get('guest_comment', '')
                
                severity_emoji = "🚨" if severity == "High" else "⚠️" if severity == "Medium" else "ℹ️"
                urgency_emoji = "⚡" if urgency == "Urgent" else "🔜" if urgency == "Soon" else "📅"
                
                content += f"   {i}. {severity_emoji} {category} Issue - {urgency} {urgency_emoji}\n"
                content += f"      Problem: {problem}\n"
                content += f"      Guest feedback: \"{guest_comment[:120]}{'...' if len(guest_comment) > 120 else ''}\"\n\n"
        
        content += f"""
MAINTENANCE PRIORITIES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ URGENT: Schedule immediately
🔜 SOON: Schedule within 1-2 days  
📅 CAN WAIT: Schedule within a week

Focus on: WiFi, AC, TV, and bed comfort issues first.
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

- Smart Property Management System"""
        
        return self.send_email(subject, content, EMAIL_CONFIG['sender_email'])
    
    def send_smart_pricing_report(self, pricing_changes):
        """Send smart pricing report with AI insights"""
        if not pricing_changes:
            return False
        
        total_impact = sum(change['price_change'] for change in pricing_changes.values())
        
        subject = f"💰 SMART PRICING REPORT - AI-Driven Revenue Optimization ({len(pricing_changes)} Properties)"
        
        content = f"""Hi Ahmed,

Smart Multi-Framework Pricing Analysis Report:

📊 EXECUTIVE SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Properties Adjusted: {len(pricing_changes)}
• Revenue Impact: ${total_impact:+.0f} per night
• Monthly Projection: ${total_impact * 30:+.0f}
• Analysis Method: GPT-4 + Rule-Based Engine + A2A Communication
• Safety Guardrails: Applied automatically

🧠 AI-DRIVEN PRICING DECISIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for property_name, decision in pricing_changes.items():
            gpt_analysis = self.detailed_analyses.get(property_name, {})
            guest_sentiment = gpt_analysis.get('guest_sentiment', 'neutral')
            
            trend = "📈 INCREASE" if decision['price_change'] > 0 else "📉 DECREASE"
            guardrail_note = " (SAFETY CAPPED)" if decision.get('guardrail_applied') else ""
            
            content += f"""🏠 {property_name}:
   💰 ${decision['base_price']} → ${decision['new_price']} ({decision['percentage_change']:+.1f}%) {trend}{guardrail_note}
   
   🤖 AI Analysis:
      • Guest Sentiment: {guest_sentiment.title()}
      • GPT Recommendation: {decision['gpt_recommendation']:+.0f}%
      • Satisfaction Score: {decision['satisfaction_score']:.1f}%
   
   ⚙️ Rule Engine:
      • Rule Adjustment: {decision['rule_adjustment']:+.1f}%
      • Logic: {decision['rule_description']}
      • Confidence: {decision['confidence']:.2f}
   
   🎯 Final Decision Logic:
      • GPT Weight: {decision['decision_logic']['gpt_weight']}
      • Rule Weight: {decision['decision_logic']['rule_weight']}
      • Confidence Applied: {decision['decision_logic']['confidence_applied']}

"""
        
        content += f"""
💡 SMART INSIGHTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Daily Revenue Impact: ${total_impact:+.0f}
• Monthly Projection: ${total_impact * 30:+.0f}
• Annual Potential: ${total_impact * 365:+.0f}

This report combines:
✓ GPT-4 analysis of real guest feedback
✓ Transparent rule-based pricing logic  
✓ Multi-agent coordination and learning
✓ Comprehensive safety guardrails

- Smart Multi-Framework Property Management System"""
        
        return self.send_email(subject, content, EMAIL_CONFIG['sender_email'])

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution - runs smart multi-framework system"""
    manager = SmartPropertyManager()
    result = await manager.run_smart_analysis()
    return result

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🧠 SMART MULTI-FRAMEWORK PROPERTY MANAGEMENT SYSTEM")
    print("=" * 70)
    print("🎯 FINAL CAPSTONE VERSION:")
    print("   ✅ Smart GPT: Analyzes ALL issues automatically (cleaning, AC, TV, bed, etc.)")
    print("   ✅ Rule-Based Engine: Transparent, auditable pricing decisions")
    print("   ✅ A2A Communication: Structured inter-agent messaging")
    print("   ✅ Cross-Agent Learning: Agents rate and adapt to each other")
    print("   ✅ Safety Guardrails: Comprehensive protection systems")
    print("   ✅ Real Reviews: Uses actual guest feedback for analysis")
    print("   ✅ Smart Pricing: Combines GPT insights with business rules")
    print("=" * 70)
    
    print("\n🚀 Running smart multi-framework analysis...")
    result = asyncio.run(main())
    
    print(f"\n🎉 SMART ANALYSIS COMPLETED!")
    print(f"📊 Results: {json.dumps(result, indent=2, default=str)}")

# ============================================================================
# END OF SMART SYSTEM
# ============================================================================