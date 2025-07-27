# ============================================================================
# COMPLETE UNIFIED PROPERTY MANAGEMENT SYSTEM
# Multi-Agent System: Review Analysis + Dynamic Pricing + Email Automation
# ============================================================================

import asyncio
import nest_asyncio
import pandas as pd
from apify_client import ApifyClientAsync
import requests
import json
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from dotenv import load_dotenv
import os

load_dotenv()  # This loads variables from .env into environment
nest_asyncio.apply()

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📧 EMAIL CONFIGURATION
EMAIL_CONFIG = {
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('GMAIL_APP_PASSWORD'),
    'cleaning_team_email': os.getenv('CLEANING_TEAM_EMAIL'),
    'demo_mode': False
}

# 🏠 PROPERTY PORTFOLIO WITH PRICING
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
# UNIFIED PROPERTY MANAGEMENT CLASS
# ============================================================================

class UnifiedPropertyManager:
    """Complete Property Management System combining review analysis and dynamic pricing"""
    
    def __init__(self):
        # Initialize base pricing
        self.base_pricing = {name: price for name, url, price in LISTINGS}
        self.current_pricing = self.base_pricing.copy()
        
        # Storage for analysis results
        self.satisfaction_scores = {}
        self.cleaning_issues = {}
        self.maintenance_issues = {}
        self.pricing_adjustments = {}
        self.review_data = None
        
        print("🚀 Unified Property Management System Initialized")
        print(f"📊 Portfolio: {len(LISTINGS)} properties")
        print(f"💰 Base pricing range: ${min(self.base_pricing.values())} - ${max(self.base_pricing.values())}")

    def test_email_connection(self):
        """Test email connection before starting"""
        print(f"🔧 Testing email connection...")
        print(f"   📧 From: {EMAIL_CONFIG['sender_email']}")
        print(f"   📧 To: {EMAIL_CONFIG['cleaning_team_email']}")
        print(f"   🔑 Password: {'✅ Configured' if EMAIL_CONFIG['sender_password'] != 'PUT_YOUR_APP_PASSWORD_HERE' else '❌ Missing'}")
        
        if EMAIL_CONFIG['demo_mode']:
            print(f"   📱 Mode: DEMO (no emails will be sent)")
            return True
        
        try:
            print(f"   🔗 Connecting to Gmail...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.quit()
            print(f"   ✅ Email connection successful!")
            return True
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            print(f"   💡 Check your Gmail app password")
            return False

    # ========================================================================
    # REVIEW ANALYSIS FUNCTIONS
    # ========================================================================

    def analyze_cleaning_issues(self, negative_comments):
        """Analyze and extract cleaning-related guest comments"""
        if not negative_comments:
            return {"has_cleaning_issues": False, "cleaning_comments": [], "issue_count": 0}
        
        cleaning_keywords = [
            'clean', 'dirty', 'dust', 'hair', 'stain', 'smell', 'odor', 'hygiene',
            'bathroom', 'toilet', 'shower', 'towel', 'bed', 'sheet', 'linen',
            'kitchen', 'dishes', 'garbage', 'trash', 'mess', 'filthy', 'gross'
        ]
        
        potential_cleaning_comments = []
        for comment in negative_comments:
            comment_lower = comment.lower()
            if any(keyword in comment_lower for keyword in cleaning_keywords):
                potential_cleaning_comments.append(comment)
        
        if not potential_cleaning_comments:
            return {"has_cleaning_issues": False, "cleaning_comments": [], "issue_count": 0}
        
        # Use GPT to confirm cleaning issues
        comments_text = "\n".join([f"COMMENT {i+1}: {comment}" for i, comment in enumerate(potential_cleaning_comments)])
        
        prompt = f"""
From these guest comments, extract ONLY the ones that mention cleaning issues and return the EXACT ORIGINAL TEXT:

{comments_text}

Return ONLY the cleaning-related comments in this format:
CLEANING_COMMENT_1: [exact original text]
CLEANING_COMMENT_2: [exact original text]

If no cleaning issues found, return: NO_CLEANING_ISSUES
"""
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"].strip()
                
                cleaning_comments = []
                if "NO_CLEANING_ISSUES" not in analysis:
                    lines = analysis.split('\n')
                    for line in lines:
                        if 'CLEANING_COMMENT_' in line and ':' in line:
                            comment_text = line.split(':', 1)[1].strip()
                            if comment_text and comment_text not in cleaning_comments:
                                cleaning_comments.append(comment_text)
                
                if not cleaning_comments and potential_cleaning_comments:
                    cleaning_comments = potential_cleaning_comments
                
                return {
                    "has_cleaning_issues": len(cleaning_comments) > 0,
                    "cleaning_comments": cleaning_comments,
                    "issue_count": len(cleaning_comments)
                }
            else:
                return {
                    "has_cleaning_issues": len(potential_cleaning_comments) > 0,
                    "cleaning_comments": potential_cleaning_comments,
                    "issue_count": len(potential_cleaning_comments)
                }
                
        except Exception as e:
            print(f"Error analyzing cleaning issues: {e}")
            return {
                "has_cleaning_issues": len(potential_cleaning_comments) > 0,
                "cleaning_comments": potential_cleaning_comments,
                "issue_count": len(potential_cleaning_comments)
            }

    def analyze_maintenance_issues(self, negative_comments):
        """Analyze and extract maintenance-related guest comments"""
        if not negative_comments:
            return {"has_maintenance_issues": False, "maintenance_comments": [], "issue_count": 0}
        
        comments_text = "\n".join([f"COMMENT {i+1}: {comment}" for i, comment in enumerate(negative_comments)])
        
        prompt = f"""
From these guest comments, extract ONLY the ones that mention maintenance or equipment issues:

{comments_text}

Look for: AC, heating, WiFi, TV, beds, appliances, plumbing, electrical, locks, noise, equipment problems

Return format:
MAINTENANCE_COMMENT_1: [exact original text]
MAINTENANCE_COMMENT_2: [exact original text]

If no maintenance issues: NO_MAINTENANCE_ISSUES
"""
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"].strip()
                
                maintenance_comments = []
                if "NO_MAINTENANCE_ISSUES" not in analysis:
                    lines = analysis.split('\n')
                    for line in lines:
                        if 'MAINTENANCE_COMMENT_' in line and ':' in line:
                            comment_text = line.split(':', 1)[1].strip()
                            if comment_text and comment_text not in maintenance_comments:
                                maintenance_comments.append(comment_text)
                
                return {
                    "has_maintenance_issues": len(maintenance_comments) > 0,
                    "maintenance_comments": maintenance_comments,
                    "issue_count": len(maintenance_comments)
                }
            else:
                return {"has_maintenance_issues": False, "maintenance_comments": [], "issue_count": 0}
                
        except Exception as e:
            print(f"Error analyzing maintenance issues: {e}")
            return {"has_maintenance_issues": False, "maintenance_comments": [], "issue_count": 0}

    def is_meaningful_negative(self, comment):
        """Filter out non-issues using GPT"""
        if not comment or len(comment.strip()) < 2:
            return False
        
        prompt = f"""
Analyze this guest comment: "{comment}"

Return "TRUE" for actual complaints/issues.
Return "FALSE" only if clearly saying "no complaints" or "everything perfect".

Response (TRUE or FALSE):"""
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 5
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                gpt_response = result["choices"][0]["message"]["content"].strip().upper()
                return gpt_response == "TRUE"
            else:
                return True
                
        except Exception as e:
            return True

    async def fetch_reviews(self, name, url):
        """Fetch reviews from Booking.com"""
        client = ApifyClientAsync(API_TOKEN)
        actor = client.actor("voyager/booking-reviews-scraper")
        
        try:
            run = await actor.call(
                run_input={
                    "startUrls": [{"url": url}],
                    "maxReviewsPerHotel": 100,
                    "proxyConfiguration": {"useApifyProxy": True}
                },
                wait_secs=300
            )
            print(f"✅ Completed: {name} — Run ID: {run['id']}")
            
            dataset = client.dataset(run["defaultDatasetId"])
            result = await dataset.list_items()
            items = result.items or []
            
            rows = []
            for item in items:
                date = (item.get("reviewDate") or "").split("T")[0]
                
                if item.get("likedText"):
                    rows.append({"listing": name, "date": date, "type": "positive", "comment": item["likedText"]})
                
                if item.get("dislikedText"):
                    if self.is_meaningful_negative(item["dislikedText"]):
                        rows.append({"listing": name, "date": date, "type": "negative", "comment": item["dislikedText"]})
            
            return rows
        except Exception as e:
            print(f"❌ Error fetching {name}: {e}")
            return []

    # ========================================================================
    # DYNAMIC PRICING FUNCTIONS
    # ========================================================================

    def calculate_dynamic_pricing(self, property_name, satisfaction_score):
        """Calculate new pricing based on satisfaction score"""
        current_price = self.base_pricing[property_name]
        
        # Pricing adjustment logic based on satisfaction
        if satisfaction_score >= 95:
            adjustment_factor = 1.15  # 15% increase for excellent performance
            reason = "Excellent guest satisfaction (95%+)"
        elif satisfaction_score >= 90:
            adjustment_factor = 1.08  # 8% increase for great performance
            reason = "Great guest satisfaction (90-94%)"
        elif satisfaction_score >= 85:
            adjustment_factor = 1.03  # 3% increase for good performance
            reason = "Good guest satisfaction (85-89%)"
        elif satisfaction_score >= 80:
            adjustment_factor = 1.0   # No change for average performance
            reason = "Average guest satisfaction (80-84%)"
        elif satisfaction_score >= 75:
            adjustment_factor = 0.95  # 5% decrease for below average
            reason = "Below average satisfaction (75-79%)"
        elif satisfaction_score >= 70:
            adjustment_factor = 0.88  # 12% decrease for poor performance
            reason = "Poor guest satisfaction (70-74%)"
        else:
            adjustment_factor = 0.80  # 20% decrease for very poor performance
            reason = "Very poor guest satisfaction (<70%)"
        
        new_price = int(current_price * adjustment_factor)
        price_change = new_price - current_price
        percentage_change = (price_change / current_price) * 100
        
        return {
            "original_price": current_price,
            "new_price": new_price,
            "price_change": price_change,
            "percentage_change": percentage_change,
            "adjustment_factor": adjustment_factor,
            "reason": reason
        }

    # ========================================================================
    # EMAIL FUNCTIONS
    # ========================================================================

    def send_email(self, subject, content, recipient):
        """Send email with improved error handling"""
        if EMAIL_CONFIG['demo_mode']:
            print(f"📝 DEMO MODE: Email would be sent to {recipient}")
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
            
            print(f"✅ SUCCESS! Email sent to {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False

    def send_consolidated_cleaning_alert(self, all_cleaning_issues):
        """Send consolidated cleaning alert to Mourad"""
        if not all_cleaning_issues:
            return False
        
        total_properties = len(all_cleaning_issues)
        total_issues = sum(len(issues) for issues in all_cleaning_issues.values())
        
        subject = f"🧹 CLEANING ALERT: {total_properties} Properties Need Attention ({total_issues} Issues)"
        
        content = f"""Hi Mourad,

We've detected cleaning-related complaints from guests across {total_properties} properties.

PROPERTIES WITH CLEANING ISSUES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for i, (property_name, issues) in enumerate(all_cleaning_issues.items(), 1):
            content += f"{i}. 🏠 {property_name} ({len(issues)} issue{'s' if len(issues) > 1 else ''})\n"
            for j, issue in enumerate(issues, 1):
                content += f"   Issue {j}: \"{issue}\"\n"
            content += "\n"
        
        content += f"""
SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Properties: {total_properties}
• Total Issues: {total_issues}
• Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please pay extra attention to cleaning these properties on your next visits.

- Automated Review Monitor"""
        
        print(f"\n📧 SENDING CLEANING ALERT TO MOURAD:")
        print(f"   📧 To: {EMAIL_CONFIG['cleaning_team_email']}")
        print(f"   📊 Properties: {total_properties}")
        print(f"   🧹 Issues: {total_issues}")
        
        return self.send_email(subject, content, EMAIL_CONFIG['cleaning_team_email'])

    def send_consolidated_maintenance_alert(self, all_maintenance_issues):
        """Send consolidated maintenance alert to Ahmed"""
        if not all_maintenance_issues:
            return False
        
        total_properties = len(all_maintenance_issues)
        total_issues = sum(len(issues) for issues in all_maintenance_issues.values())
        
        subject = f"🔧 MAINTENANCE ALERT: {total_properties} Properties Need Attention ({total_issues} Issues)"
        
        content = f"""Hi Ahmed,

We've detected maintenance-related complaints from guests across {total_properties} properties.

PROPERTIES WITH MAINTENANCE ISSUES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for i, (property_name, issues) in enumerate(all_maintenance_issues.items(), 1):
            content += f"{i}. 🏠 {property_name} ({len(issues)} issue{'s' if len(issues) > 1 else ''})\n"
            for j, issue in enumerate(issues, 1):
                content += f"   Issue {j}: \"{issue}\"\n"
            content += "\n"
        
        content += f"""
SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Properties: {total_properties}
• Total Issues: {total_issues}
• Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please schedule maintenance visits to address these specific issues.

- Automated Review Monitor"""
        
        print(f"\n📧 SENDING MAINTENANCE ALERT TO AHMED:")
        print(f"   📧 To: {EMAIL_CONFIG['sender_email']}")
        print(f"   📊 Properties: {total_properties}")
        print(f"   🔧 Issues: {total_issues}")
        
        return self.send_email(subject, content, EMAIL_CONFIG['sender_email'])

    def send_pricing_report(self, pricing_changes):
        """Send pricing optimization report to Ahmed"""
        if not pricing_changes:
            return False
        
        total_revenue_change = sum(change['price_change'] for change in pricing_changes.values())
        properties_adjusted = len(pricing_changes)
        
        subject = f"💰 PRICING OPTIMIZATION REPORT - {properties_adjusted} Properties Adjusted"
        
        content = f"""Hi Ahmed,

Here's your Dynamic Pricing Optimization Report:

📊 EXECUTIVE SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Properties Adjusted: {properties_adjusted}
• Net Revenue Impact: ${total_revenue_change:+.0f} per night
• Projected Monthly Impact: ${total_revenue_change * 30:+.0f}
• Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🏠 PRICING ADJUSTMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for property_name, change in pricing_changes.items():
            trend = "INCREASE" if change['price_change'] > 0 else "DECREASE" if change['price_change'] < 0 else "NO CHANGE"
            content += f"""🏠 {property_name}:
   Previous Price: ${change['original_price']}
   New Price: ${change['new_price']}
   Change: ${change['price_change']:+d} ({change['percentage_change']:+.1f}%) - {trend}
   Reason: {change['reason']}
   
"""
        
        content += f"""
💡 REVENUE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Daily Impact: ${total_revenue_change:+.0f}
• Monthly Projection: ${total_revenue_change * 30:+.0f}
• Annual Projection: ${total_revenue_change * 365:+.0f}

All pricing adjustments are based on guest satisfaction scores and market optimization algorithms.

- Automated Pricing System"""
        
        print(f"\n💰 SENDING PRICING REPORT TO AHMED:")
        print(f"   📧 To: {EMAIL_CONFIG['sender_email']}")
        print(f"   📊 Properties: {properties_adjusted}")
        print(f"   💵 Revenue Impact: ${total_revenue_change:+.0f}/night")
        
        return self.send_email(subject, content, EMAIL_CONFIG['sender_email'])

    def send_comprehensive_report(self):
        """Send complete analysis report to Ahmed"""
        if not self.satisfaction_scores:
            return False
        
        avg_satisfaction = sum(self.satisfaction_scores.values()) / len(self.satisfaction_scores)
        cleaning_properties = len(self.cleaning_issues)
        maintenance_properties = len(self.maintenance_issues)
        pricing_adjustments = len(self.pricing_adjustments)
        
        subject = f"🏠 COMPLETE PROPERTY ANALYSIS REPORT - {datetime.now().strftime('%Y-%m-%d')}"
        
        content = f"""Hi Ahmed,

Here's your Complete Property Management Analysis Report:

📊 EXECUTIVE SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Properties Analyzed: {len(self.satisfaction_scores)}
• Average Satisfaction: {avg_satisfaction:.1f}%
• Cleaning Issues: {cleaning_properties} properties
• Maintenance Issues: {maintenance_properties} properties  
• Pricing Adjustments: {pricing_adjustments} properties
• Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 SATISFACTION SCORES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for property_name, score in self.satisfaction_scores.items():
            content += f"🏠 {property_name}: {score:.1f}%\n"
        
        if self.pricing_adjustments:
            total_revenue_change = sum(change['price_change'] for change in self.pricing_adjustments.values())
            content += f"""

💰 PRICING OPTIMIZATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Properties Adjusted: {len(self.pricing_adjustments)}
• Net Revenue Impact: ${total_revenue_change:+.0f} per night
• Monthly Projection: ${total_revenue_change * 30:+.0f}
"""
        
        content += f"""

🚨 OPERATIONAL ALERTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Cleaning Alerts Sent: {'Yes' if cleaning_properties > 0 else 'No'}
• Maintenance Alerts Sent: {'Yes' if maintenance_properties > 0 else 'No'}
• Pricing Updates Applied: {'Yes' if pricing_adjustments > 0 else 'No'}

This report was generated by the Automated Property Management System using AI-powered analysis of guest reviews and dynamic pricing optimization.

- Unified Property Management System"""
        
        print(f"\n📄 SENDING COMPREHENSIVE REPORT TO AHMED:")
        print(f"   📧 To: {EMAIL_CONFIG['sender_email']}")
        print(f"   📊 Properties: {len(self.satisfaction_scores)}")
        print(f"   📈 Avg Satisfaction: {avg_satisfaction:.1f}%")
        
        return self.send_email(subject, content, EMAIL_CONFIG['sender_email'])

    # ========================================================================
    # MAIN EXECUTION FUNCTIONS
    # ========================================================================

    async def run_complete_analysis(self):
        """Run the complete unified property management analysis"""
        print("🚀 UNIFIED PROPERTY MANAGEMENT SYSTEM - COMPLETE ANALYSIS")
        print("=" * 80)
        print(f"🏠 Properties: {len(LISTINGS)}")
        print(f"📧 Email Mode: {'Production' if not EMAIL_CONFIG['demo_mode'] else 'Demo'}")
        print("=" * 80)
        
        # Test email connection
        if not self.test_email_connection():
            print("❌ Email system not working - continuing with analysis only")
        
        # Step 1: Fetch all reviews
        print(f"\n📋 STEP 1: FETCHING REVIEWS")
        print("-" * 40)
        
        all_review_data = []
        for name, url, base_price in LISTINGS:
            print(f"🔄 Processing {name}...")
            rows = await self.fetch_reviews(name, url)
            all_review_data.extend(rows)
        
        if not all_review_data:
            print("⚠️ No reviews retrieved. Stopping analysis.")
            return
        
        self.review_data = pd.DataFrame(all_review_data)
        print(f"✅ Collected {len(all_review_data)} reviews from {self.review_data['listing'].nunique()} properties")
        
        # Step 2: Calculate satisfaction scores and analyze issues
        print(f"\n📊 STEP 2: SATISFACTION ANALYSIS")
        print("-" * 40)
        
        all_cleaning_issues = {}
        all_maintenance_issues = {}
        
        for property_name in self.review_data['listing'].unique():
            property_data = self.review_data[self.review_data['listing'] == property_name]
            positive_count = len(property_data[property_data['type'] == 'positive'])
            negative_count = len(property_data[property_data['type'] == 'negative'])
            total_reviews = positive_count + negative_count
            
            if total_reviews > 0:
                satisfaction_score = (positive_count / total_reviews) * 100
                self.satisfaction_scores[property_name] = round(satisfaction_score, 1)
                
                print(f"🏠 {property_name}: {satisfaction_score:.1f}% satisfaction ({positive_count}+, {negative_count}-)")
                
                # Analyze issues
                negative_comments = property_data[property_data['type'] == 'negative']['comment'].tolist()
                
                # Check for cleaning issues
                cleaning_analysis = self.analyze_cleaning_issues(negative_comments)
                if cleaning_analysis['has_cleaning_issues']:
                    all_cleaning_issues[property_name] = cleaning_analysis['cleaning_comments']
                    self.cleaning_issues[property_name] = cleaning_analysis['cleaning_comments']
                    print(f"   🧹 {len(cleaning_analysis['cleaning_comments'])} cleaning issues detected")
                
                # Check for maintenance issues
                maintenance_analysis = self.analyze_maintenance_issues(negative_comments)
                if maintenance_analysis['has_maintenance_issues']:
                    all_maintenance_issues[property_name] = maintenance_analysis['maintenance_comments']
                    self.maintenance_issues[property_name] = maintenance_analysis['maintenance_comments']
                    print(f"   🔧 {len(maintenance_analysis['maintenance_comments'])} maintenance issues detected")
        
        # Step 3: Dynamic pricing optimization
        print(f"\n💰 STEP 3: DYNAMIC PRICING OPTIMIZATION")
        print("-" * 40)
        
        pricing_changes = {}
        total_revenue_impact = 0
        
        for property_name, satisfaction_score in self.satisfaction_scores.items():
            pricing_result = self.calculate_dynamic_pricing(property_name, satisfaction_score)
            
            if pricing_result['price_change'] != 0:
                pricing_changes[property_name] = pricing_result
                self.pricing_adjustments[property_name] = pricing_result
                self.current_pricing[property_name] = pricing_result['new_price']
                total_revenue_impact += pricing_result['price_change']
                
                trend = "📈" if pricing_result['price_change'] > 0 else "📉"
                print(f"🏠 {property_name}: ${pricing_result['original_price']} → ${pricing_result['new_price']} "
                      f"({pricing_result['percentage_change']:+.1f}%) {trend}")
                print(f"   Reason: {pricing_result['reason']}")
            else:
                print(f"🏠 {property_name}: ${self.base_pricing[property_name]} (no change needed)")
        
        print(f"\n💵 Total Revenue Impact: ${total_revenue_impact:+.0f} per night")
        print(f"📅 Monthly Projection: ${total_revenue_impact * 30:+.0f}")
        
        # Step 4: Send email notifications
        print(f"\n📧 STEP 4: EMAIL NOTIFICATIONS")
        print("-" * 40)
        
        emails_sent = 0
        
        # Send cleaning alerts
        if all_cleaning_issues:
            if self.send_consolidated_cleaning_alert(all_cleaning_issues):
                emails_sent += 1
                print(f"✅ Cleaning alert sent to Mourad ({len(all_cleaning_issues)} properties)")
        else:
            print(f"✅ No cleaning issues detected")
        
        # Send maintenance alerts
        if all_maintenance_issues:
            if self.send_consolidated_maintenance_alert(all_maintenance_issues):
                emails_sent += 1
                print(f"✅ Maintenance alert sent to Ahmed ({len(all_maintenance_issues)} properties)")
        else:
            print(f"✅ No maintenance issues detected")
        
        # Send pricing report
        if pricing_changes:
            if self.send_pricing_report(pricing_changes):
                emails_sent += 1
                print(f"✅ Pricing report sent to Ahmed ({len(pricing_changes)} adjustments)")
        else:
            print(f"✅ No pricing changes needed")
        
        # Send comprehensive report
        if self.send_comprehensive_report():
            emails_sent += 1
            print(f"✅ Comprehensive report sent to Ahmed")
        
        # Step 5: Final summary
        print(f"\n📋 STEP 5: EXECUTION SUMMARY")
        print("=" * 80)
        print(f"📊 Properties Analyzed: {len(self.satisfaction_scores)}")
        print(f"📈 Average Satisfaction: {sum(self.satisfaction_scores.values()) / len(self.satisfaction_scores):.1f}%")
        print(f"🧹 Cleaning Issues: {len(self.cleaning_issues)} properties")
        print(f"🔧 Maintenance Issues: {len(self.maintenance_issues)} properties")
        print(f"💰 Pricing Adjustments: {len(self.pricing_adjustments)} properties")
        print(f"💵 Revenue Impact: ${total_revenue_impact:+.0f} per night")
        print(f"📧 Emails Sent: {emails_sent}")
        print(f"⏱️  Analysis Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Display current pricing matrix
        print(f"\n💰 UPDATED PRICING MATRIX:")
        print("-" * 50)
        for property_name in [name for name, url, price in LISTINGS]:
            original = self.base_pricing[property_name]
            current = self.current_pricing[property_name]
            change = current - original
            if change != 0:
                trend = "📈" if change > 0 else "📉"
                print(f"{property_name}: ${current} (${change:+d}) {trend}")
            else:
                print(f"{property_name}: ${current}")
        
        return {
            "properties_analyzed": len(self.satisfaction_scores),
            "average_satisfaction": sum(self.satisfaction_scores.values()) / len(self.satisfaction_scores),
            "cleaning_issues": len(self.cleaning_issues),
            "maintenance_issues": len(self.maintenance_issues),
            "pricing_adjustments": len(self.pricing_adjustments),
            "revenue_impact": total_revenue_impact,
            "emails_sent": emails_sent
        }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_email_only():
    """Test email functionality without running full analysis"""
    print("🧪 TESTING EMAIL FUNCTIONALITY ONLY")
    print("=" * 50)
    
    manager = UnifiedPropertyManager()
    
    if not manager.test_email_connection():
        print("❌ Email connection failed")
        return
    
    # Test cleaning alert
    print("\n📧 Testing cleaning alert...")
    test_cleaning = {
        "Room N5 Downtown": ["Bathroom needs better cleaning", "Dust on surfaces"],
        "Room 1 Full Luxury": ["Hair in the shower drain"]
    }
    
    if manager.send_consolidated_cleaning_alert(test_cleaning):
        print("✅ Cleaning alert test successful!")
    
    # Test maintenance alert
    print("\n🔧 Testing maintenance alert...")
    test_maintenance = {
        "Room N5 Downtown": ["WiFi connection very slow", "AC unit making noise"],
        "Room 2 Luxury": ["Bed is uncomfortable and squeaky"]
    }
    
    if manager.send_consolidated_maintenance_alert(test_maintenance):
        print("✅ Maintenance alert test successful!")
    
    # Test pricing report
    print("\n💰 Testing pricing report...")
    test_pricing = {
        "Room N5 Downtown": {
            "original_price": 200,
            "new_price": 180,
            "price_change": -20,
            "percentage_change": -10.0,
            "reason": "Below average satisfaction (75%)"
        },
        "Room 1 Full Luxury": {
            "original_price": 300,
            "new_price": 324,
            "price_change": 24,
            "percentage_change": 8.0,
            "reason": "Great guest satisfaction (92%)"
        }
    }
    
    if manager.send_pricing_report(test_pricing):
        print("✅ Pricing report test successful!")
    
    print("\n🎉 EMAIL TESTING COMPLETE!")

def run_review_analysis_only():
    """Run only review analysis without pricing optimization"""
    print("📊 REVIEW ANALYSIS ONLY MODE")
    print("=" * 50)
    
    async def analysis_only():
        manager = UnifiedPropertyManager()
        
        # Fetch reviews
        all_review_data = []
        for name, url, base_price in LISTINGS:
            print(f"🔄 Processing {name}...")
            rows = await manager.fetch_reviews(name, url)
            all_review_data.extend(rows)
        
        if not all_review_data:
            print("⚠️ No reviews retrieved.")
            return
        
        manager.review_data = pd.DataFrame(all_review_data)
        print(f"✅ Collected {len(all_review_data)} reviews")
        
        # Analyze satisfaction and issues
        all_cleaning_issues = {}
        all_maintenance_issues = {}
        
        for property_name in manager.review_data['listing'].unique():
            property_data = manager.review_data[manager.review_data['listing'] == property_name]
            positive_count = len(property_data[property_data['type'] == 'positive'])
            negative_count = len(property_data[property_data['type'] == 'negative'])
            total_reviews = positive_count + negative_count
            
            if total_reviews > 0:
                satisfaction_score = (positive_count / total_reviews) * 100
                manager.satisfaction_scores[property_name] = round(satisfaction_score, 1)
                
                print(f"🏠 {property_name}: {satisfaction_score:.1f}% satisfaction")
                
                # Check for issues
                negative_comments = property_data[property_data['type'] == 'negative']['comment'].tolist()
                
                cleaning_analysis = manager.analyze_cleaning_issues(negative_comments)
                if cleaning_analysis['has_cleaning_issues']:
                    all_cleaning_issues[property_name] = cleaning_analysis['cleaning_comments']
                
                maintenance_analysis = manager.analyze_maintenance_issues(negative_comments)
                if maintenance_analysis['has_maintenance_issues']:
                    all_maintenance_issues[property_name] = maintenance_analysis['maintenance_comments']
        
        # Send alerts only
        if all_cleaning_issues:
            manager.send_consolidated_cleaning_alert(all_cleaning_issues)
        
        if all_maintenance_issues:
            manager.send_consolidated_maintenance_alert(all_maintenance_issues)
    
    asyncio.run(analysis_only())

def run_pricing_optimization_only():
    """Run only pricing optimization with sample data"""
    print("💰 PRICING OPTIMIZATION ONLY MODE")
    print("=" * 50)
    
    manager = UnifiedPropertyManager()
    
    # Sample satisfaction scores for testing
    sample_scores = {
        "Room N5 Downtown": 78,      # Below average - price decrease
        "Room 1 Full Luxury": 93,    # Great - price increase
        "Room 2 Luxury": 87,         # Good - small increase
        "Room N3 Luxury": 82,        # Average - no change
        "Room Shared A": 71,         # Poor - significant decrease
        "Room Shared B": 96,         # Excellent - maximum increase
        "Room N7 Shared": 85         # Good - small increase
    }
    
    print("📊 Sample Satisfaction Scores:")
    for prop, score in sample_scores.items():
        print(f"   🏠 {prop}: {score}%")
    
    print(f"\n💰 Calculating Dynamic Pricing Adjustments:")
    
    pricing_changes = {}
    total_revenue_impact = 0
    
    for property_name, satisfaction_score in sample_scores.items():
        pricing_result = manager.calculate_dynamic_pricing(property_name, satisfaction_score)
        
        if pricing_result['price_change'] != 0:
            pricing_changes[property_name] = pricing_result
            total_revenue_impact += pricing_result['price_change']
            
            trend = "📈" if pricing_result['price_change'] > 0 else "📉"
            print(f"🏠 {property_name}: ${pricing_result['original_price']} → ${pricing_result['new_price']} "
                  f"({pricing_result['percentage_change']:+.1f}%) {trend}")
        else:
            print(f"🏠 {property_name}: ${manager.base_pricing[property_name]} (no change)")
    
    print(f"\n💵 Total Revenue Impact: ${total_revenue_impact:+.0f} per night")
    print(f"📅 Monthly Projection: ${total_revenue_impact * 30:+.0f}")
    
    # Send pricing report
    if pricing_changes:
        manager.send_pricing_report(pricing_changes)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution function - runs complete unified system"""
    manager = UnifiedPropertyManager()
    result = await manager.run_complete_analysis()
    return result

# ============================================================================
# SCRIPT EXECUTION OPTIONS
# ============================================================================

if __name__ == "__main__":
    print("🏠 UNIFIED PROPERTY MANAGEMENT SYSTEM")
    print("=" * 60)
    print("Available execution modes:")
    print("1. main() - Complete unified analysis (review + pricing + emails)")
    print("2. test_email_only() - Test email functionality only") 
    print("3. run_review_analysis_only() - Review analysis + emails only")
    print("4. run_pricing_optimization_only() - Pricing optimization only")
    print("=" * 60)
    
    # Default execution - run complete analysis
    print("🚀 Running complete unified analysis...")
    result = asyncio.run(main())
    
    print(f"\n🎉 SYSTEM EXECUTION COMPLETED!")
    print(f"📊 Final Results: {result}")

# ============================================================================
# END OF UNIFIED SYSTEM
# ============================================================================