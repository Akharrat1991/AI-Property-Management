# ============================================================================
# ENHANCED PROPERTY MANAGEMENT SYSTEM - FINAL VERSION
# Superior AI Detection for ALL Cleaning & Maintenance Issues
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
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp

load_dotenv()
nest_asyncio.apply()

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# EMAIL CONFIGURATION
EMAIL_CONFIG = {
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('GMAIL_APP_PASSWORD'),
    'cleaning_team_email': os.getenv('CLEANING_TEAM_EMAIL'),
    'maintenance_team_email': os.getenv('SENDER_EMAIL'),
    'pricing_team_email': os.getenv('SENDER_EMAIL'),
    'demo_mode': False
}

# ALL 7 PROPERTIES
LISTINGS = [
    ("Room N5 Downtown", "https://www.booking.com/hotel/ca/room-n5-in-a-shared-apartment-in-downtown-montreal.fr.html", 200),
    ("Room 1 Full Luxury", "https://www.booking.com/hotel/ca/room-1-full-equipped-in-big-luxury-apartment-in-downtown-montreal.fr.html", 300),
    ("Room 2 Luxury", "https://www.booking.com/hotel/ca/room-2-in-big-luxury-apartment-in-downtown-montreal.fr.html", 280),
    ("Room N3 Luxury", "https://www.booking.com/hotel/ca/room-n3-in-a-big-luxury-apartment-in-downtown-montreal.fr.html", 290),
    ("Room Shared A", "https://www.booking.com/hotel/ca/room-in-a-shared-apartment-in-downtown-montreal.fr.html", 150),
    ("Room Shared B", "https://www.booking.com/hotel/ca/room-in-shared-apartment-in-downtown-montreal.fr.html", 160),
    ("Room N7 Shared", "https://www.booking.com/hotel/ca/room-n7-in-a-shared-apartment-in-downtown-montreal.fr.html", 155),
]

# PARALLEL PROCESSING LIMITS
MAX_CONCURRENT_SCRAPING = 3
MAX_CONCURRENT_GPT = 5
MAX_CONCURRENT_EMAILS = 3

# ============================================================================
# ENHANCED GPT-4 PROCESSOR WITH SUPERIOR CLEANING DETECTION
# ============================================================================

class EnhancedGPTProcessor:
    """Enhanced GPT-4 processor that catches ALL cleaning and maintenance issues"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        
    async def create_session(self):
        """Create reusable HTTP session for speed"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=45)  # Increased timeout for thorough analysis
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Clean up session"""
        if self.session:
            await self.session.close()
    
    async def batch_analyze_properties(self, property_data_list):
        """Analyze multiple properties with ENHANCED cleaning detection"""
        await self.create_session()
        
        # Create concurrent tasks for all properties
        tasks = []
        for property_data in property_data_list:
            task = self.analyze_single_property_enhanced(
                property_data['name'],
                property_data['positive_comments'],
                property_data['negative_comments']
            )
            tasks.append(task)
        
        # Execute all analyses in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        property_analyses = {}
        for i, result in enumerate(results):
            property_name = property_data_list[i]['name']
            if isinstance(result, Exception):
                print(f"❌ Error analyzing {property_name}: {result}")
                property_analyses[property_name] = self._enhanced_fallback_analysis(property_data_list[i]['negative_comments'])
            else:
                property_analyses[property_name] = result
        
        await self.close_session()
        return property_analyses
    
    async def analyze_single_property_enhanced(self, property_name, positive_comments, negative_comments):
        """ENHANCED analysis that catches ALL cleaning issues"""
        if not positive_comments and not negative_comments:
            return self._empty_analysis()
        
        # Combine comments efficiently
        all_comments = []
        for i, comment in enumerate(positive_comments[:20]):  # Increased limit
            all_comments.append(f"POSITIVE {i+1}: {comment}")
        for i, comment in enumerate(negative_comments[:20]):  # Increased limit
            all_comments.append(f"NEGATIVE {i+1}: {comment}")
        
        comments_text = "\n".join(all_comments)
        
        # SUPER ENHANCED GPT prompt for MAXIMUM cleaning detection
        enhanced_prompt = f"""
PROPERTY INSPECTION ANALYSIS - {property_name}

You are a EXPERT PROPERTY INSPECTOR analyzing guest feedback. Your job is to find EVERY SINGLE cleaning and maintenance issue mentioned.

GUEST COMMENTS TO ANALYZE:
{comments_text}

CRITICAL CLEANING DETECTION INSTRUCTIONS:
You MUST detect ANY mention of these cleaning-related words/concepts:

🧹 CLEANING ISSUES TO DETECT:
- dirty, dirt, dusty, dust, messy, mess, unclean, not clean, needs cleaning
- stained, stains, spots, marks, residue, grime, grimy, filthy
- smells, odor, odour, stinks, stinky, musty, moldy, mold, mildew
- hair, hairs (any type), soap scum, grease, greasy, sticky, crusty
- untidy, unkempt, sloppy, gross, disgusting, nasty, yucky
- "could be cleaner", "not very clean", "poorly cleaned", "needs attention"
- bathroom issues: toilet dirty, shower dirty, sink dirty, mirror spots
- kitchen issues: dishes dirty, counters dirty, appliances dirty
- bedroom issues: sheets dirty, pillows dirty, floor dirty, surfaces dirty
- general: windows dirty, walls dirty, floors dirty, furniture dirty

🔧 MAINTENANCE ISSUES TO DETECT:
- broken, not working, doesn't work, malfunction, out of order
- slow, fast, loud, noisy, quiet, silent, flickering, dim, bright
- hot, cold, warm, cool, uncomfortable, hard, soft, loose, tight
- stuck, jammed, leaking, dripping, cracked, chipped, torn, worn
- WiFi slow, TV problems, AC issues, heating problems, bed uncomfortable
- plumbing issues, electrical problems, appliance failures

ANALYSIS REQUIREMENTS:
1. Read EVERY comment word by word
2. Extract MULTIPLE issues from single comments when present
3. Even minor mentions count (like "a bit dirty" = cleaning issue)
4. Classify location precisely (bathroom/kitchen/bedroom/living room)
5. Rate severity realistically (guest complaints = at least Medium severity)

Return comprehensive JSON:
{{
    "satisfaction_score": 75,
    "cleaning_issues": [
        {{
            "guest_comment": "EXACT quote mentioning cleaning issue",
            "problem": "Detailed description of specific cleaning problem",
            "location": "bathroom/kitchen/bedroom/living room/general",
            "severity": "High/Medium/Low",
            "cleaning_type": "surface/deep/maintenance/odor/stain",
            "keywords_detected": ["list", "of", "cleaning", "keywords", "found"]
        }}
    ],
    "maintenance_issues": [
        {{
            "guest_comment": "EXACT quote mentioning maintenance issue",
            "problem": "Detailed description of specific maintenance problem", 
            "category": "AC/TV/Bed/WiFi/Plumbing/Electrical/Noise/Appliances/Furniture/Other",
            "severity": "High/Medium/Low",
            "urgency": "Urgent/Soon/Can wait",
            "keywords_detected": ["list", "of", "maintenance", "keywords", "found"]
        }}
    ],
    "guest_sentiment": "very satisfied/satisfied/neutral/frustrated/very frustrated",
    "recommended_price_change": -5,
    "confidence": 0.9,
    "analysis_statistics": {{
        "total_comments_analyzed": {len(all_comments)},
        "negative_comments": {len(negative_comments)},
        "positive_comments": {len(positive_comments)},
        "cleaning_mentions_detected": 0,
        "maintenance_mentions_detected": 0,
        "comments_with_issues": 0
    }}
}}

CRITICAL: Do NOT miss cleaning issues. Every guest complaint about cleanliness costs revenue and reputation. Be thorough and comprehensive.
"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert property inspector and hospitality consultant. Your expertise is finding EVERY cleaning and maintenance issue in guest feedback. Missing issues costs money and guest satisfaction. Be extremely thorough - err on the side of detecting MORE issues rather than fewer."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                "temperature": 0.05,  # Very low for consistency
                "max_tokens": 4000    # Increased for detailed analysis
            }
            
            async with self.session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    gpt_response = result["choices"][0]["message"]["content"].strip()
                    
                    try:
                        analysis = json.loads(gpt_response)
                        
                        # Validate detection quality
                        cleaning_count = len(analysis.get("cleaning_issues", []))
                        maintenance_count = len(analysis.get("maintenance_issues", []))
                        negative_count = len(negative_comments)
                        
                        print(f"✅ Enhanced analysis complete: {property_name}")
                        print(f"   📝 Total comments: {len(all_comments)} (Positive: {len(positive_comments)}, Negative: {negative_count})")
                        print(f"   🧹 Cleaning issues detected: {cleaning_count}")
                        print(f"   🔧 Maintenance issues detected: {maintenance_count}")
                        print(f"   📊 Detection rate: {(cleaning_count + maintenance_count) / max(negative_count, 1):.1f} issues per negative comment")
                        
                        # Quality check warnings
                        if negative_count > 2 and cleaning_count == 0:
                            print(f"   ⚠️ WARNING: {negative_count} negative comments but NO cleaning issues detected!")
                        
                        if negative_count > 5 and (cleaning_count + maintenance_count) < 2:
                            print(f"   ⚠️ WARNING: Low detection rate - only {cleaning_count + maintenance_count} issues from {negative_count} negative comments!")
                        
                        return analysis
                        
                    except json.JSONDecodeError:
                        print(f"⚠️ JSON decode error for {property_name}, using enhanced fallback")
                        return self._enhanced_fallback_analysis(negative_comments)
                else:
                    print(f"❌ GPT API error for {property_name}: {response.status}")
                    return self._enhanced_fallback_analysis(negative_comments)
                    
        except Exception as e:
            print(f"❌ Error in enhanced analysis for {property_name}: {e}")
            return self._enhanced_fallback_analysis(negative_comments)
    
    def _enhanced_fallback_analysis(self, negative_comments):
        """Enhanced fallback with aggressive keyword detection"""
        
        # Comprehensive keyword lists
        cleaning_keywords = {
            'dirty': ['dirty', 'dirt', 'unclean', 'not clean', 'filthy', 'grimy', 'messy', 'mess'],
            'stains': ['stained', 'stains', 'spots', 'marks', 'residue'],
            'odors': ['smell', 'smells', 'odor', 'odour', 'stink', 'musty', 'moldy'],
            'dust': ['dust', 'dusty', 'hair', 'hairs'],
            'general': ['gross', 'disgusting', 'nasty', 'needs cleaning', 'could be cleaner', 'poorly cleaned']
        }
        
        maintenance_keywords = {
            'broken': ['broken', 'not working', "doesn't work", 'malfunction', 'out of order'],
            'comfort': ['uncomfortable', 'hard', 'soft', 'loud', 'noisy'],
            'temperature': ['hot', 'cold', 'warm', 'cool'],
            'electrical': ['flickering', 'dim', 'bright', 'slow wifi', 'wifi slow'],
            'plumbing': ['leaking', 'dripping', 'stuck', 'jammed']
        }
        
        cleaning_issues = []
        maintenance_issues = []
        
        for comment in negative_comments:
            comment_lower = comment.lower()
            
            # Check for cleaning issues (multiple per comment)
            for category, keywords in cleaning_keywords.items():
                for keyword in keywords:
                    if keyword in comment_lower:
                        cleaning_issues.append({
                            "guest_comment": comment,
                            "problem": f"Guest mentioned {category}: '{keyword}'",
                            "location": "general",
                            "severity": "Medium",
                            "cleaning_type": category,
                            "keywords_detected": [keyword]
                        })
                        break  # One per category per comment
            
            # Check for maintenance issues (multiple per comment)
            for category, keywords in maintenance_keywords.items():
                for keyword in keywords:
                    if keyword in comment_lower:
                        maintenance_issues.append({
                            "guest_comment": comment,
                            "problem": f"Guest mentioned {category}: '{keyword}'",
                            "category": "Other",
                            "severity": "Medium",
                            "urgency": "Soon",
                            "keywords_detected": [keyword]
                        })
                        break  # One per category per comment
        
        # Calculate satisfaction based on issues found
        total_issues = len(cleaning_issues) + len(maintenance_issues)
        satisfaction = max(50, 90 - (total_issues * 8))
        
        print(f"   🔄 FALLBACK ANALYSIS:")
        print(f"   📝 Negative comments: {len(negative_comments)}")
        print(f"   🧹 Cleaning issues found: {len(cleaning_issues)}")
        print(f"   🔧 Maintenance issues found: {len(maintenance_issues)}")
        
        return {
            "satisfaction_score": satisfaction,
            "cleaning_issues": cleaning_issues,
            "maintenance_issues": maintenance_issues,
            "guest_sentiment": "frustrated" if total_issues > 3 else "neutral",
            "recommended_price_change": -min(total_issues * 3, 15),
            "confidence": 0.7,
            "analysis_statistics": {
                "total_comments_analyzed": len(negative_comments),
                "negative_comments": len(negative_comments),
                "positive_comments": 0,
                "cleaning_mentions_detected": len(cleaning_issues),
                "maintenance_mentions_detected": len(maintenance_issues),
                "comments_with_issues": len(set([issue["guest_comment"] for issue in cleaning_issues + maintenance_issues]))
            }
        }
    
    def _empty_analysis(self):
        """Empty analysis for properties with no comments"""
        return {
            "satisfaction_score": 80,
            "cleaning_issues": [],
            "maintenance_issues": [],
            "guest_sentiment": "neutral",
            "recommended_price_change": 0,
            "confidence": 0.3,
            "analysis_statistics": {
                "total_comments_analyzed": 0,
                "negative_comments": 0,
                "positive_comments": 0,
                "cleaning_mentions_detected": 0,
                "maintenance_mentions_detected": 0,
                "comments_with_issues": 0
            }
        }

# ============================================================================
# PARALLEL SCRAPING ENGINE (UNCHANGED)
# ============================================================================

class ParallelScrapingEngine:
    """High-speed parallel scraping for all 7 properties"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        
    async def scrape_all_properties_parallel(self):
        """Scrape all 7 properties in parallel batches for maximum speed"""
        print(f"🚀 PARALLEL SCRAPING: Starting {len(LISTINGS)} properties in batches of {MAX_CONCURRENT_SCRAPING}")
        
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_SCRAPING)
        
        async def scrape_with_semaphore(property_data):
            async with semaphore:
                return await self.scrape_single_property(property_data)
        
        scraping_tasks = []
        for name, url, price in LISTINGS:
            task = scrape_with_semaphore((name, url, price))
            scraping_tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
        end_time = time.time()
        
        all_reviews = []
        successful_scrapes = 0
        
        for i, result in enumerate(results):
            property_name = LISTINGS[i][0]
            if isinstance(result, Exception):
                print(f"❌ Scraping failed for {property_name}: {result}")
            else:
                all_reviews.extend(result)
                successful_scrapes += 1
                print(f"✅ Scraped {len(result)} reviews from {property_name}")
        
        print(f"🏁 PARALLEL SCRAPING COMPLETE: {successful_scrapes}/{len(LISTINGS)} properties in {end_time - start_time:.1f}s")
        return all_reviews
    
    async def scrape_single_property(self, property_data):
        """Optimized single property scraping"""
        name, url, price = property_data
        
        client = ApifyClientAsync(self.api_key)
        actor = client.actor("voyager/booking-reviews-scraper")
        
        try:
            print(f"🔄 Scraping: {name}")
            
            run = await actor.call(
                run_input={
                    "startUrls": [{"url": url}],
                    "maxReviewsPerHotel": 40,  # Increased for better analysis
                    "proxyConfiguration": {"useApifyProxy": True},
                    "timeout": 120
                },
                wait_secs=120
            )
            
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
            
            print(f"✅ {name}: {len(reviews)} reviews collected")
            return reviews
            
        except Exception as e:
            print(f"❌ Error scraping {name}: {e}")
            return []

# ============================================================================
# FAST PARALLEL EMAIL SYSTEM (UNCHANGED)
# ============================================================================

class FastEmailSystem:
    """Parallel email sending system for speed"""
    
    def __init__(self, config):
        self.config = config
        
    async def send_all_emails_parallel(self, cleaning_properties, maintenance_properties, pricing_changes):
        """Send all emails in parallel for maximum speed"""
        print(f"📧 PARALLEL EMAIL SENDING: Starting batch email dispatch")
        
        email_tasks = []
        
        if cleaning_properties:
            task = self.send_cleaning_email_async(cleaning_properties)
            email_tasks.append(("cleaning", task))
        
        if maintenance_properties:
            task = self.send_maintenance_email_async(maintenance_properties)
            email_tasks.append(("maintenance", task))
        
        if pricing_changes:
            task = self.send_pricing_email_async(pricing_changes)
            email_tasks.append(("pricing", task))
        
        if not email_tasks:
            print("📧 No emails to send")
            return 0
        
        start_time = time.time()
        results = await asyncio.gather(*[task for _, task in email_tasks], return_exceptions=True)
        end_time = time.time()
        
        emails_sent = 0
        for i, result in enumerate(results):
            email_type = email_tasks[i][0]
            if isinstance(result, Exception):
                print(f"❌ {email_type} email failed: {result}")
            elif result:
                emails_sent += 1
                print(f"✅ {email_type} email sent successfully")
            else:
                print(f"❌ {email_type} email failed")
        
        print(f"📧 PARALLEL EMAIL COMPLETE: {emails_sent}/{len(email_tasks)} emails sent in {end_time - start_time:.1f}s")
        return emails_sent
    
    async def send_cleaning_email_async(self, cleaning_properties):
        """Send cleaning email to MOURAD"""
        def send_email_sync():
            subject = f"🧹 ENHANCED CLEANING ALERT - {len(cleaning_properties)} Properties Need Attention"
            content = self._generate_enhanced_cleaning_content(cleaning_properties)
            return self._send_email_sync(subject, content, self.config['cleaning_team_email'])
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await loop.run_in_executor(executor, send_email_sync)
    
    async def send_maintenance_email_async(self, maintenance_properties):
        """Send maintenance email to AHMED"""
        def send_email_sync():
            subject = f"🔧 ENHANCED MAINTENANCE ALERT - {len(maintenance_properties)} Properties Need Attention"
            content = self._generate_enhanced_maintenance_content(maintenance_properties)
            return self._send_email_sync(subject, content, self.config['maintenance_team_email'])
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await loop.run_in_executor(executor, send_email_sync)
    
    async def send_pricing_email_async(self, pricing_changes):
        """Send pricing email to AHMED"""
        def send_email_sync():
            subject = f"💰 PRICING OPTIMIZATION REPORT - {len(pricing_changes)} Properties Adjusted"
            content = self._generate_pricing_content(pricing_changes)
            return self._send_email_sync(subject, content, self.config['pricing_team_email'])
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await loop.run_in_executor(executor, send_email_sync)
    
    def _generate_enhanced_cleaning_content(self, cleaning_properties):
        """Enhanced cleaning email with detailed issue breakdown"""
        total_issues = sum(len(issues) for issues in cleaning_properties.values())
        
        content = f"""Hi Mourad,

ENHANCED AI ANALYSIS has detected {total_issues} cleaning issues across {len(cleaning_properties)} properties that require immediate attention.

🧹 DETAILED CLEANING ISSUES DETECTED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for property_name, issues in cleaning_properties.items():
            content += f"🏠 {property_name} ({len(issues)} issues detected):\n\n"
            
            for i, issue in enumerate(issues, 1):
                severity = issue.get('severity', 'Medium')
                location = issue.get('location', 'general')
                problem = issue.get('problem', 'cleaning issue')
                guest_comment = issue.get('guest_comment', '')[:100]
                keywords = issue.get('keywords_detected', [])
                
                severity_emoji = "🚨" if severity == "High" else "⚠️" if severity == "Medium" else "ℹ️"
                
                content += f"   {i}. {severity_emoji} {severity} Priority - {location.title()}\n"
                content += f"      Issue: {problem}\n"
                content += f"      Guest Said: \"{guest_comment}{'...' if len(guest_comment) == 100 else ''}\"\n"
                if keywords:
                    content += f"      Keywords: {', '.join(keywords)}\n"
                content += "\n"
            
            content += "─" * 80 + "\n\n"
        
        content += f"""
🎯 PRIORITY ACTION REQUIRED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Properties Affected: {len(cleaning_properties)}
• Total Issues to Address: {total_issues}
• High Priority Issues: {sum(1 for issues in cleaning_properties.values() for issue in issues if issue.get('severity') == 'High')}
• Guest Complaints Analyzed: Multiple per property

Focus on HIGH priority issues first (🚨), then medium (⚠️), then low (ℹ️).
All issues detected are based on real guest complaints and affect our reputation.

Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Generated by Enhanced AI Property Management System

Best regards,
Enhanced Property Management System
Powered by Advanced AI Detection"""
        
        return content
    
    def _generate_enhanced_maintenance_content(self, maintenance_properties):
        """Enhanced maintenance email with detailed issue breakdown"""
        total_issues = sum(len(issues) for issues in maintenance_properties.values())
        
        content = f"""Hi Ahmed,

ENHANCED AI ANALYSIS has detected {total_issues} maintenance issues across {len(maintenance_properties)} properties requiring your attention.

🔧 DETAILED MAINTENANCE ISSUES DETECTED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for property_name, issues in maintenance_properties.items():
            content += f"🏠 {property_name} ({len(issues)} issues detected):\n\n"
            
            for i, issue in enumerate(issues, 1):
                category = issue.get('category', 'General')
                severity = issue.get('severity', 'Medium')
                urgency = issue.get('urgency', 'Soon')
                problem = issue.get('problem', 'maintenance needed')
                guest_comment = issue.get('guest_comment', '')[:100]
                keywords = issue.get('keywords_detected', [])
                
                severity_emoji = "🚨" if severity == "High" else "⚠️" if severity == "Medium" else "ℹ️"
                urgency_emoji = "⚡" if urgency == "Urgent" else "🔜" if urgency == "Soon" else "📅"
                
                content += f"   {i}. {severity_emoji} {category} Issue - {urgency} {urgency_emoji}\n"
                content += f"      Problem: {problem}\n"
                content += f"      Guest Said: \"{guest_comment}{'...' if len(guest_comment) == 100 else ''}\"\n"
                if keywords:
                    content += f"      Keywords: {', '.join(keywords)}\n"
                content += "\n"
            
            content += "─" * 80 + "\n\n"
        
        content += f"""
🎯 MAINTENANCE PRIORITIES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ URGENT: Schedule immediately (same day)
🔜 SOON: Schedule within 1-2 days  
📅 CAN WAIT: Schedule within a week

• Total Properties Affected: {len(maintenance_properties)}
• Total Issues to Address: {total_issues}
• Urgent Issues: {sum(1 for issues in maintenance_properties.values() for issue in issues if issue.get('urgency') == 'Urgent')}
• Guest Complaints Analyzed: Multiple per property

All issues detected are based on real guest feedback and impact guest satisfaction.

Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Generated by Enhanced AI Property Management System

Best regards,
Enhanced Property Management System
Powered by Advanced AI Detection"""
        
        return content
    
    def _generate_pricing_content(self, pricing_changes):
        """Pricing email content"""
        total_impact = sum(change['price_change'] for change in pricing_changes.values())
        
        content = f"""Hi Ahmed,

PRICING OPTIMIZATION REPORT - AI Analysis Complete

💰 PRICING ADJUSTMENTS ({len(pricing_changes)} properties):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for property_name, decision in pricing_changes.items():
            trend = "📈" if decision['price_change'] > 0 else "📉"
            content += f"🏠 {property_name}: ${decision['base_price']} → ${decision['new_price']} ({decision['percentage_change']:+.1f}%) {trend}\n"
        
        content += f"""

📊 FINANCIAL IMPACT:
• Revenue Impact: ${total_impact:+.0f} per night
• Monthly Impact: ${total_impact * 30:+.0f}
• Annual Projection: ${total_impact * 365:+.0f}
• Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Generated by Enhanced AI Property Management System
"""
        return content
    
    def _send_email_sync(self, subject, content, recipient):
        """Synchronous email sending"""
        if self.config['demo_mode']:
            print(f"📝 DEMO: Email would be sent to {recipient}")
            return True
        
        if not self.config['sender_email'] or not self.config['sender_password']:
            print(f"❌ Email credentials missing")
            return False
        
        try:
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = self.config['sender_email']
            msg['To'] = recipient
            
            context = ssl.create_default_context()
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls(context=context)
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

# ============================================================================
# ENHANCED SMART PROPERTY MANAGER - FINAL VERSION
# ============================================================================

class UltraFastSmartPropertyManager:
    """Enhanced property manager with SUPERIOR cleaning detection"""
    
    def __init__(self):
        # Core data for all 7 properties
        self.base_pricing = {name: price for name, url, price in LISTINGS}
        self.satisfaction_scores = {}
        self.detailed_analyses = {}
        self.pricing_decisions = {}
        self.review_data = None
        
        # Enhanced processing components
        self.scraper = ParallelScrapingEngine(APIFY_API_KEY)
        self.gpt_processor = EnhancedGPTProcessor(OPENAI_API_KEY)  # ENHANCED!
        self.email_system = FastEmailSystem(EMAIL_CONFIG)
        
        print("🚀 ENHANCED SMART PROPERTY MANAGEMENT SYSTEM - FINAL VERSION")
        print(f"🏠 Portfolio: {len(LISTINGS)} properties (ALL 7 PROPERTIES)")
        print(f"🧹 ENHANCED CLEANING DETECTION: Catches ALL cleaning issues")
        print(f"🔧 COMPREHENSIVE MAINTENANCE DETECTION: Nothing gets missed")
        print(f"⚡ Parallel Processing: Maximum speed with maximum accuracy")
        print("🎯 OPTIMIZED FOR COMPLETE ISSUE DETECTION!")
    
    async def run_ultra_fast_analysis(self):
        """Enhanced complete analysis with SUPERIOR issue detection"""
        total_start_time = time.time()
        cycle_id = f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("\n🚀 ENHANCED SMART ANALYSIS STARTING")
        print("=" * 80)
        print(f"🆔 Cycle: {cycle_id}")
        print(f"🏠 Properties: {len(LISTINGS)} (ALL 7 PROPERTIES)")
        print(f"🧹 Enhanced Cleaning Detection: MAXIMUM SENSITIVITY")
        
        # STEP 1: PARALLEL SCRAPING
        print(f"\n⚡ STEP 1: PARALLEL SCRAPING")
        print("-" * 50)
        
        scraping_start = time.time()
        all_reviews = await self.scraper.scrape_all_properties_parallel()
        scraping_time = time.time() - scraping_start
        
        if not all_reviews:
            print("⚠️ No reviews collected")
            return {"error": "No reviews", "cycle_id": cycle_id}
        
        self.review_data = pd.DataFrame(all_reviews)
        unique_properties = self.review_data['listing'].nunique()
        
        print(f"✅ SCRAPING COMPLETE: {len(all_reviews)} reviews from {unique_properties} properties in {scraping_time:.1f}s")
        
        # STEP 2: ENHANCED AI ANALYSIS
        print(f"\n🧠 STEP 2: ENHANCED AI ANALYSIS WITH SUPERIOR DETECTION")
        print("-" * 50)
        
        gpt_start = time.time()
        
        # Prepare data for enhanced GPT processing
        property_data_list = []
        for property_name in self.review_data['listing'].unique():
            property_data = self.review_data[self.review_data['listing'] == property_name]
            positive_comments = property_data[property_data['type'] == 'positive']['comment'].tolist()
            negative_comments = property_data[property_data['type'] == 'negative']['comment'].tolist()
            
            property_data_list.append({
                'name': property_name,
                'positive_comments': positive_comments,
                'negative_comments': negative_comments
            })
            
            print(f"   🏠 {property_name}: {len(positive_comments)} positive, {len(negative_comments)} negative comments")
        
        # Execute ENHANCED parallel analysis
        self.detailed_analyses = await self.gpt_processor.batch_analyze_properties(property_data_list)
        
        # Extract satisfaction scores and display enhanced results
        total_cleaning_issues = 0
        total_maintenance_issues = 0
        
        for property_name, analysis in self.detailed_analyses.items():
            self.satisfaction_scores[property_name] = analysis.get('satisfaction_score', 80)
            cleaning_count = len(analysis.get('cleaning_issues', []))
            maintenance_count = len(analysis.get('maintenance_issues', []))
            total_cleaning_issues += cleaning_count
            total_maintenance_issues += maintenance_count
            
            print(f"   ✅ {property_name}: {cleaning_count} cleaning + {maintenance_count} maintenance issues")
        
        gpt_time = time.time() - gpt_start
        print(f"✅ ENHANCED ANALYSIS COMPLETE: {len(self.detailed_analyses)} properties analyzed in {gpt_time:.1f}s")
        print(f"🧹 TOTAL CLEANING ISSUES DETECTED: {total_cleaning_issues}")
        print(f"🔧 TOTAL MAINTENANCE ISSUES DETECTED: {total_maintenance_issues}")
        
        # STEP 3: FAST PRICING DECISIONS
        print(f"\n💰 STEP 3: SMART PRICING CALCULATIONS")
        print("-" * 50)
        
        pricing_start = time.time()
        total_revenue_impact = 0
        
        for property_name, analysis in self.detailed_analyses.items():
            base_price = self.base_pricing.get(property_name, 200)
            satisfaction = analysis.get('satisfaction_score', 80)
            gpt_recommendation = analysis.get('recommended_price_change', 0)
            
            # Enhanced pricing calculation based on issues
            cleaning_issues = len(analysis.get('cleaning_issues', []))
            maintenance_issues = len(analysis.get('maintenance_issues', []))
            total_issues = cleaning_issues + maintenance_issues
            
            # Base pricing adjustment
            if satisfaction >= 90:
                price_change_pct = 0.10
            elif satisfaction >= 85:
                price_change_pct = 0.05
            elif satisfaction >= 75:
                price_change_pct = 0.0
            elif satisfaction >= 65:
                price_change_pct = -0.05
            else:
                price_change_pct = -0.10
            
            # Issue penalty
            issue_penalty = -(total_issues * 0.02)  # 2% per issue
            
            # Combine factors
            final_change = price_change_pct + issue_penalty + (gpt_recommendation / 100 * 0.2)
            final_change = max(-0.25, min(0.25, final_change))
            
            new_price = int(base_price * (1 + final_change))
            price_change = new_price - base_price
            
            self.pricing_decisions[property_name] = {
                'base_price': base_price,
                'new_price': new_price,
                'price_change': price_change,
                'percentage_change': final_change * 100,
                'satisfaction_score': satisfaction,
                'cleaning_issues': cleaning_issues,
                'maintenance_issues': maintenance_issues
            }
            
            if abs(price_change) >= 5:
                total_revenue_impact += price_change
        
        pricing_time = time.time() - pricing_start
        print(f"✅ PRICING COMPLETE: {len(self.pricing_decisions)} decisions in {pricing_time:.1f}s")
        
        # STEP 4: ENHANCED EMAIL DISPATCH
        print(f"\n📧 STEP 4: ENHANCED EMAIL DISPATCH")
        print("-" * 50)
        
        email_start = time.time()
        
        # Collect issues for emails
        cleaning_properties = {name: analysis.get("cleaning_issues", []) 
                             for name, analysis in self.detailed_analyses.items() 
                             if analysis.get("cleaning_issues")}
        
        maintenance_properties = {name: analysis.get("maintenance_issues", []) 
                                for name, analysis in self.detailed_analyses.items() 
                                if analysis.get("maintenance_issues")}
        
        significant_pricing = {name: decision 
                             for name, decision in self.pricing_decisions.items() 
                             if abs(decision.get("price_change", 0)) >= 5}
        
        print(f"   📧 Cleaning email to Mourad: {len(cleaning_properties)} properties with {sum(len(issues) for issues in cleaning_properties.values())} issues")
        print(f"   📧 Maintenance email to Ahmed: {len(maintenance_properties)} properties with {sum(len(issues) for issues in maintenance_properties.values())} issues")
        print(f"   📧 Pricing email to Ahmed: {len(significant_pricing)} pricing adjustments")
        
        # Send emails in parallel
        emails_sent = await self.email_system.send_all_emails_parallel(
            cleaning_properties, maintenance_properties, significant_pricing
        )
        
        email_time = time.time() - email_start
        total_time = time.time() - total_start_time
        
        # ENHANCED FINAL SUMMARY
        print(f"\n🏁 ENHANCED ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"⚡ TOTAL TIME: {total_time:.1f} seconds")
        print(f"🔄 Scraping Time: {scraping_time:.1f}s")
        print(f"🧠 Enhanced Analysis Time: {gpt_time:.1f}s")
        print(f"💰 Pricing Time: {pricing_time:.1f}s")
        print(f"📧 Email Time: {email_time:.1f}s")
        print("")
        print(f"🏠 Properties Processed: {len(self.satisfaction_scores)}/7 (ALL PROPERTIES)")
        print(f"📊 Average Satisfaction: {sum(self.satisfaction_scores.values()) / len(self.satisfaction_scores):.1f}%" if self.satisfaction_scores else "N/A")
        print(f"🧹 CLEANING ISSUES DETECTED: {total_cleaning_issues} (Enhanced Detection)")
        print(f"🔧 MAINTENANCE ISSUES DETECTED: {total_maintenance_issues} (Enhanced Detection)")
        print(f"💰 Pricing Adjustments: {len(significant_pricing)} properties")
        print(f"💵 Revenue Impact: ${total_revenue_impact:+.0f} per night")
        print(f"📧 Emails Sent: {emails_sent}")
        print("")
        print(f"🎯 DETECTION IMPROVEMENT: Enhanced AI catches {total_cleaning_issues + total_maintenance_issues} total issues")
        print(f"📧 EMAIL ROUTING: Cleaning→Mourad, Maintenance→Ahmed, Pricing→Ahmed")
        print("=" * 80)
        
        return {
            "cycle_id": cycle_id,
            "total_time": total_time,
            "scraping_time": scraping_time,
            "gpt_time": gpt_time,
            "pricing_time": pricing_time,
            "email_time": email_time,
            "properties_analyzed": len(self.satisfaction_scores),
            "average_satisfaction": sum(self.satisfaction_scores.values()) / len(self.satisfaction_scores) if self.satisfaction_scores else 0,
            "cleaning_issues": total_cleaning_issues,
            "maintenance_issues": total_maintenance_issues,
            "pricing_adjustments": len(significant_pricing),
            "revenue_impact": total_revenue_impact,
            "emails_sent": emails_sent,
            "enhancement_note": f"Enhanced detection found {total_cleaning_issues + total_maintenance_issues} total issues",
            "email_routing": "Cleaning→Mourad, Maintenance→Ahmed, Pricing→Ahmed"
        }

# ============================================================================
# USAGE
# ============================================================================

async def main():
    """Run the enhanced system"""
    manager = UltraFastSmartPropertyManager()
    result = await manager.run_ultra_fast_analysis()
    return result

if __name__ == "__main__":
    asyncio.run(main())