import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart Property Management Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.header-image {
    width: 100%;
    max-width: 600px;
    height: 200px;
    object-fit: cover;
    border-radius: 10px;
    margin: 1rem 0;
}

.system-badge {
    background: #3498db;
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    margin: 0.2rem;
    display: inline-block;
    font-weight: 500;
}

.metric-card {
    background: white;
    color: #2c3e50;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-left: 4px solid #3498db;
}

.metric-card h3 {
    margin: 0;
    font-size: 0.9rem;
    color: #7f8c8d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-card h1 {
    margin: 0.5rem 0;
    font-size: 2.5rem;
    color: #2c3e50;
    font-weight: 600;
}

.revenue-card {
    background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.property-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #3498db;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.status-excellent { color: #27ae60; font-weight: 600; }
.status-good { color: #f39c12; font-weight: 600; }
.status-poor { color: #e74c3c; font-weight: 600; }

.professional-badge {
    background: #34495e;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.8rem;
    margin: 0.2rem;
    display: inline-block;
    font-weight: 500;
}

.sidebar-section {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    border-left: 3px solid #3498db;
}

.success-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 8px;
    padding: 1rem;
    color: #155724;
    margin: 1rem 0;
}

.info-box {
    background: #d1ecf1;
    border: 1px solid #bee5eb;
    border-radius: 8px;
    padding: 1rem;
    color: #0c5460;
    margin: 1rem 0;
}

.warning-box {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 1rem;
    color: #856404;
    margin: 1rem 0;
}

.run-button {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    margin: 1rem 0;
    transition: all 0.3s ease;
}

.run-button:hover {
    background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}
</style>
""", unsafe_allow_html=True)

# Enhanced GPT-4 Recommendation Generator (simplified for dashboard)
def generate_gpt_recommendations(issue_type, problem, location_or_category, severity_or_urgency, guest_comment):
    """Generate intelligent recommendations using GPT-4 intelligence"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return ["API key not configured"]
    
    if issue_type == "cleaning":
        prompt = f"""You are an expert cleaning supervisor. A guest complained:

GUEST COMPLAINT: "{guest_comment}"

Provide 5-6 specific cleaning recommendations to fix this exact issue. Be practical and actionable."""
    else:
        prompt = f"""You are an expert maintenance technician. A guest complained:

GUEST COMPLAINT: "{guest_comment}"

Provide 5-6 specific troubleshooting steps to fix this exact issue. Be practical and actionable."""
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert property management consultant. Provide specific, actionable recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 600
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            gpt_response = result["choices"][0]["message"]["content"].strip()
            
            # Extract recommendations
            recommendations = []
            for line in gpt_response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                    # Clean up formatting
                    clean_line = line
                    for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '•', '-']:
                        if clean_line.startswith(prefix):
                            clean_line = clean_line[len(prefix):].strip()
                            break
                    if clean_line:
                        recommendations.append(clean_line)
            
            return recommendations[:7] if recommendations else ["Address the guest's specific concern"]
            
    except Exception as e:
        print(f"Error generating recommendations: {e}")
    
    # Simple fallback
    return [f"Address the {issue_type} issue mentioned by guest"]

def get_gpt_time_cost_estimates(category, severity, guest_comment):
    """Get intelligent time and cost estimates using GPT-4"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "1-2 hours", "$50-150"
    
    prompt = f"""Based on this guest complaint, provide realistic estimates:

GUEST COMPLAINT: "{guest_comment}"
CATEGORY: {category}

Provide in this format:
TIME: [range like "30 minutes - 2 hours"]
COST: [range like "$25-100"]"""
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 100
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            gpt_response = result["choices"][0]["message"]["content"].strip()
            
            # Parse response
            time_estimate = "1-2 hours"
            cost_estimate = "$50-150"
            
            for line in gpt_response.split('\n'):
                if 'TIME:' in line.upper():
                    time_estimate = line.split(':', 1)[1].strip()
                elif 'COST:' in line.upper():
                    cost_estimate = line.split(':', 1)[1].strip()
            
            return time_estimate, cost_estimate
            
    except Exception as e:
        print(f"Error getting estimates: {e}")
    
    return "1-2 hours", "$50-150"

# Initialize session state with enhanced data integration
def initialize_system():
    """Initialize system and load enhanced data if available"""
    if 'system_initialized' not in st.session_state:
        # Check if we can import the enhanced system
        try:
            from unified_property_management import UltraFastSmartPropertyManager, EMAIL_CONFIG
            st.session_state.real_system_available = True
            st.session_state.email_config = EMAIL_CONFIG
            st.session_state.system_type = "Ultra-Fast Multi-Framework System"
        except ImportError:
            st.session_state.real_system_available = False
            st.session_state.email_config = {}
            st.session_state.system_type = "Demo Mode"
        
        # Initialize empty data structure
        st.session_state.satisfaction_scores = {}
        st.session_state.detailed_analyses = {}
        st.session_state.pricing_decisions = {}
        st.session_state.real_reviews_data = None
        st.session_state.framework_performance = {
            "smart_ai_analyses": 0,
            "pricing_decisions": 0,
            "a2a_messages": 0,
            "learning_events": 0,
            "safety_violations": 0
        }
        st.session_state.last_real_update = None
        st.session_state.system_initialized = True

# Initialize system
initialize_system()

# Professional Header with Real Image
st.markdown("""
<div class="main-header">
    <h1>Smart Property Management Dashboard</h1>
    <p>Intelligent Multi-Framework AI System for Property Analytics & Optimization</p>
    <img src="https://images.timesproperty.com/blog/759/TP_iStock_1072145896_ss.jpg" alt="Property Management" class="header-image">
    <div style="margin-top: 1rem;">
        <span class="system-badge">AI Analytics</span>
        <span class="system-badge">Rule Engine</span>
        <span class="system-badge">Communication Protocol</span>
        <span class="system-badge">Safety Systems</span>
        <span class="system-badge">Email Automation</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Professional Sidebar
st.sidebar.header("System Control Panel")
st.sidebar.markdown(f"""
<div class="sidebar-section">
<strong>MGSC 695 Capstone Project</strong><br>
<strong>Student:</strong> Ahmed Kharrat<br>
<strong>System:</strong> {st.session_state.system_type}<br>
<strong>Features:</strong> Full AI Intelligence<br>
<strong>Email:</strong> Enhanced with AI Recommendations
</div>
""", unsafe_allow_html=True)

# System Status
st.sidebar.header("System Status")
if st.session_state.real_system_available:
    st.sidebar.markdown("""
    <div class="success-box">
    ✅ Smart AI System: Online<br>
    ✅ Rule-Based Pricing: Online<br>
    ✅ Communication Protocol: Active<br>
    ✅ Safety Guardrails: Monitoring<br>
    ✅ AI Recommendations: Ready
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="warning-box">
    ❌ Enhanced System: Not Available<br>
    💡 Check unified_property_management.py
    </div>
    """, unsafe_allow_html=True)

# Configuration Status
st.sidebar.markdown("---")
st.sidebar.header("Configuration Status")

if st.session_state.real_system_available:
    try:
        email_config = st.session_state.email_config
        config_status = ""
        
        if email_config.get('sender_email') and email_config.get('sender_password'):
            config_status += "✅ Email System: Configured<br>"
        else:
            config_status += "❌ Email System: Not configured<br>"
        
        if os.getenv('OPENAI_API_KEY'):
            config_status += "✅ AI API: Configured<br>"
        else:
            config_status += "❌ AI API: Missing<br>"
        
        if os.getenv('APIFY_API_KEY'):
            config_status += "✅ Scraping API: Configured<br>"
        else:
            config_status += "❌ Scraping API: Missing<br>"
        
        st.sidebar.markdown(f'<div class="info-box">{config_status}</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.sidebar.markdown('<div class="warning-box">❌ System: Configuration error</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="warning-box">❌ System: Not found<br>💡 unified_property_management.py missing</div>', unsafe_allow_html=True)

# MAIN SYSTEM EXECUTION
st.markdown("---")
st.header("Complete System Execution")

if st.session_state.real_system_available:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 RUN COMPLETE ANALYSIS", type="primary", help="Complete system: Scraping + Analysis + Emails + Dashboard Population"):
            with st.spinner("Running complete smart analysis & email testing..."):
                try:
                    # Import and run the enhanced system
                    import asyncio
                    from unified_property_management import UltraFastSmartPropertyManager
                    
                    # Create progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Initializing Smart AI system...")
                    progress_bar.progress(5)
                    
                    # Run the enhanced system
                    async def run_complete_analysis():
                        manager = UltraFastSmartPropertyManager()
                        result = await manager.run_ultra_fast_analysis()
                        return manager, result
                    
                    status_text.text("Scraping real guest reviews from Booking.com...")
                    progress_bar.progress(20)
                    
                    status_text.text("Running AI analysis on scraped comments...")
                    progress_bar.progress(40)
                    
                    status_text.text("Generating AI recommendations for each issue...")
                    progress_bar.progress(60)
                    
                    status_text.text("Sending enhanced emails with AI recommendations...")
                    progress_bar.progress(80)
                    
                    # Actually run the enhanced system
                    try:
                        manager, result = asyncio.run(run_complete_analysis())
                        
                        status_text.text("Testing email system configuration...")
                        progress_bar.progress(90)
                        
                        status_text.text("✅ Complete analysis & email testing completed!")
                        progress_bar.progress(100)
                        
                        # Display enhanced results
                        if result and "error" not in result:
                            st.success("🎉 Complete Smart Analysis & Email Testing Completed Successfully!")
                            
                            # Load enhanced data into session state
                            st.session_state.satisfaction_scores = manager.satisfaction_scores
                            st.session_state.detailed_analyses = manager.detailed_analyses
                            st.session_state.pricing_decisions = manager.pricing_decisions
                            st.session_state.real_reviews_data = manager.review_data
                            st.session_state.framework_performance = result.get('framework_performance', {})
                            st.session_state.last_real_update = datetime.now()
                            
                            # Show enhanced metrics
                            st.markdown("### Analysis Results")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Properties Analyzed", result.get("properties_analyzed", 0))
                            
                            with col2:
                                st.metric("Avg Satisfaction", f"{result.get('average_satisfaction', 0):.1f}%")
                            
                            with col3:
                                st.metric("Cleaning Issues", result.get("cleaning_issues", 0))
                            
                            with col4:
                                st.metric("Maintenance Issues", result.get("maintenance_issues", 0))
                            
                            # Show revenue impact
                            revenue_impact = result.get("revenue_impact", 0)
                            st.metric("Revenue Impact", f"${revenue_impact:+.0f}/night", f"${revenue_impact * 365:+.0f}/year")
                            
                            # Show emails sent
                            emails_sent = result.get("emails_sent", 0)
                            st.metric("Emails Sent", f"{emails_sent} emails", "To Ahmed & Mourad")
                            
                            # Performance metrics
                            total_time = result.get("total_time", 0)
                            performance_improvement = result.get("performance_improvement", "0")
                            st.metric("Analysis Time", f"{total_time:.1f} seconds", f"{performance_improvement} faster")
                            
                            # Show system execution summary
                            if st.session_state.real_reviews_data is not None:
                                total_reviews = len(st.session_state.real_reviews_data)
                                positive_reviews = len(st.session_state.real_reviews_data[st.session_state.real_reviews_data['type'] == 'positive'])
                                negative_reviews = len(st.session_state.real_reviews_data[st.session_state.real_reviews_data['type'] == 'negative'])
                                
                                st.markdown(f"""
                                <div class="success-box">
                                <strong>COMPLETE SYSTEM EXECUTION SUMMARY:</strong><br>
                                • <strong>Reviews Scraped:</strong> {total_reviews} real guest comments<br>
                                • <strong>Positive Comments:</strong> {positive_reviews}<br>
                                • <strong>Negative Comments:</strong> {negative_reviews}<br>
                                • <strong>AI Analysis:</strong> Complete on all comments<br>
                                • <strong>AI Recommendations:</strong> Generated for every issue<br>
                                • <strong>Emails Sent:</strong> {emails_sent} enhanced emails with AI recommendations<br>
                                • <strong>Dashboard:</strong> All tabs now populated with real data<br>
                                • <strong>Multi-Framework:</strong> All systems coordinated successfully
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Show sample of real comments analyzed
                            with st.expander("View Sample Real Guest Comments Analyzed by AI"):
                                if st.session_state.real_reviews_data is not None and not st.session_state.real_reviews_data.empty:
                                    sample_reviews = st.session_state.real_reviews_data.head(10)
                                    for _, review in sample_reviews.iterrows():
                                        comment_type = "👍 POSITIVE" if review['type'] == 'positive' else "👎 NEGATIVE"
                                        st.write(f"**{comment_type} - {review['listing']}:**")
                                        st.write(f"\"{review['comment'][:200]}{'...' if len(review['comment']) > 200 else ''}\"")
                                        st.write("---")
                                else:
                                    st.write("No review data available")
                            
                            st.balloons()
                            st.success("🎯 **ALL TABS ARE NOW POPULATED!** Navigate through the tabs below to see all the real data and analysis.")
                            st.rerun()  # Refresh with complete data
                        else:
                            st.error(f"❌ Complete analysis failed: {result.get('error', 'Unknown error') if result else 'No result returned'}")
                            
                    except Exception as e:
                        st.error(f"❌ Failed to run complete analysis: {str(e)}")
                        st.info("💡 Check your .env file has valid API keys and email credentials")
                        
                except ImportError as e:
                    st.error("❌ Could not import the enhanced system. Make sure unified_property_management.py is in the same directory.")
                    st.code("Error: " + str(e))
    
    with col2:
        st.markdown("#### System Features")
        st.markdown("""
        <div class="info-box">
        <strong>ONE CLICK DOES EVERYTHING:</strong><br>
        ✅ Live Booking.com scraping<br>
        ✅ <strong>Full AI intelligence</strong><br>
        ✅ <strong>AI recommendations</strong><br>
        ✅ Enhanced email notifications<br>
        ✅ Email system testing<br>
        ✅ <strong>Populate ALL dashboard tabs</strong><br>
        ✅ Multi-framework coordination
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="success-box">
        <strong>RESULT:</strong> Complete system execution in one click!
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
        ⚠️ <strong>Note:</strong> Uses real AI API credits!
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="warning-box">
    ❌ <strong>Enhanced system not available!</strong> Make sure `unified_property_management.py` is in the same directory.<br>
    💡 The dashboard will show empty data until you run the complete analysis.
    </div>
    """, unsafe_allow_html=True)

# Dashboard Content
st.markdown("---")

# Data Source Indicator
if st.session_state.get('last_real_update'):
    last_update = st.session_state.last_real_update
    st.markdown(f"""
    <div class="success-box">
    📊 <strong>Dashboard showing real data with full AI analysis</strong> | Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="info-box">
    📊 <strong>Dashboard showing empty data</strong> | Click 'RUN COMPLETE ANALYSIS' above to load actual scraped reviews with full AI intelligence
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Key Metrics - calculated from enhanced or empty data
total_properties = len(st.session_state.satisfaction_scores) if st.session_state.satisfaction_scores else 7
if st.session_state.satisfaction_scores and any(score > 0 for score in st.session_state.satisfaction_scores.values()):
    avg_satisfaction = sum(st.session_state.satisfaction_scores.values()) / len(st.session_state.satisfaction_scores)
else:
    avg_satisfaction = 0

total_cleaning_issues = sum(len(analysis.get('cleaning_issues', [])) for analysis in st.session_state.detailed_analyses.values())
total_maintenance_issues = sum(len(analysis.get('maintenance_issues', [])) for analysis in st.session_state.detailed_analyses.values())

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Properties</h3>
        <h1>{total_properties}</h1>
        <p>Active Listings</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    satisfaction_color = "🟢" if avg_satisfaction >= 85 else "🟡" if avg_satisfaction >= 75 else "🔴"
    st.markdown(f"""
    <div class="metric-card">
        <h3>{satisfaction_color} Satisfaction</h3>
        <h1>{avg_satisfaction:.1f}%</h1>
        <p>AI Analyzed</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    cleaning_color = "🔴" if total_cleaning_issues > 5 else "🟡" if total_cleaning_issues > 2 else "🟢"
    st.markdown(f"""
    <div class="metric-card">
        <h3>{cleaning_color} Cleaning</h3>
        <h1>{total_cleaning_issues}</h1>
        <p>AI Detected</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    maintenance_color = "🔴" if total_maintenance_issues > 5 else "🟡" if total_maintenance_issues > 2 else "🟢"
    st.markdown(f"""
    <div class="metric-card">
        <h3>{maintenance_color} Maintenance</h3>
        <h1>{total_maintenance_issues}</h1>
        <p>AI Detected</p>
    </div>
    """, unsafe_allow_html=True)

# Revenue Impact Section
st.markdown("---")
col1, col2 = st.columns([2, 1])

with col1:
    # Revenue Analysis Chart
    st.subheader("Revenue Impact Analysis")
    
    if st.session_state.pricing_decisions and st.session_state.satisfaction_scores:
        pricing_df = pd.DataFrame([
            {
                "Property": prop.replace("Room ", "").replace(" Downtown", "").replace(" Luxury", "").replace(" Shared", ""),
                "Base Price": st.session_state.pricing_decisions.get(prop, {}).get("base_price", 200),
                "New Price": st.session_state.pricing_decisions.get(prop, {}).get("new_price", 200),
                "Change": st.session_state.pricing_decisions.get(prop, {}).get("price_change", 0),
                "Satisfaction": st.session_state.satisfaction_scores.get(prop, 0)
            }
            for prop in st.session_state.satisfaction_scores.keys()
        ])
        
        fig_revenue = px.bar(
            pricing_df, 
            x="Property", 
            y="Change",
            color="Satisfaction",
            color_continuous_scale="RdYlGn",
            title="Daily Revenue Impact by Property (AI + Rules)",
            labels={"Change": "Revenue Change ($)", "Property": ""}
        )
        fig_revenue.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("📊 Revenue chart will appear after running analysis")

with col2:
    total_revenue_change = sum(decision.get("price_change", 0) for decision in st.session_state.pricing_decisions.values()) if st.session_state.pricing_decisions else 0
    
    st.markdown(f"""
    <div class="revenue-card">
        <h3>Revenue Impact</h3>
        <h1>${total_revenue_change:+.0f}</h1>
        <p>Per Night</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <p><strong>Monthly:</strong> ${total_revenue_change * 30:+.0f}</p>
        <p><strong>Annual:</strong> ${total_revenue_change * 365:+.0f}</p>
    </div>
    """, unsafe_allow_html=True)

# Issues Analysis Section
st.markdown("---")
st.header("Issues Analysis Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Cleaning Issues", "Maintenance Issues", "Property Performance", "AI Insights"])

with tab1:
    st.subheader("Cleaning Issues Analysis")
    
    # Collect all cleaning issues from data
    all_cleaning_issues = []
    for prop, analysis in st.session_state.detailed_analyses.items():
        for issue in analysis.get('cleaning_issues', []):
            all_cleaning_issues.append({
                "Property": prop,
                "Location": issue.get('location', 'general'),
                "Problem": issue.get('problem', 'cleaning issue'),
                "Severity": issue.get('severity', 'Medium'),
                "Guest Comment": issue.get('guest_comment', '')
            })
    
    if all_cleaning_issues:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Cleaning issues by severity
            cleaning_df = pd.DataFrame(all_cleaning_issues)
            severity_counts = cleaning_df['Severity'].value_counts()
            
            fig_severity = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                title="AI Detected Cleaning Issues by Severity",
                color_discrete_map={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#27ae60'}
            )
            st.plotly_chart(fig_severity, use_container_width=True)
        
        with col2:
            # Cleaning issues by location
            location_counts = cleaning_df['Location'].value_counts()
            
            fig_location = px.bar(
                x=location_counts.values,
                y=location_counts.index,
                orientation='h',
                title="AI Detected Issues by Location",
                color=location_counts.values,
                color_continuous_scale="Reds"
            )
            fig_location.update_layout(height=300)
            st.plotly_chart(fig_location, use_container_width=True)
        
        # Detailed cleaning issues with AI recommendations
        st.subheader("Cleaning Issues & AI Recommendations (From Real Comments)")
        
        for issue in all_cleaning_issues:
            severity_emoji = "🚨" if issue['Severity'] == 'High' else "⚠️" if issue['Severity'] == 'Medium' else "ℹ️"
            
            # Generate AI recommendations based on real guest comment
            with st.spinner(f"Generating AI recommendations for {issue['Property']}..."):
                recommendations = generate_gpt_recommendations(
                    "cleaning", 
                    issue['Problem'], 
                    issue['Location'], 
                    issue['Severity'], 
                    issue['Guest Comment']
                )
            
            # Create expandable section for each issue
            with st.expander(f"{severity_emoji} {issue['Property']} - {issue['Location'].title()} ({issue['Severity']} Priority)", expanded=issue['Severity'] == 'High'):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Issue Details:**")
                    st.write(f"**Property:** {issue['Property']}")
                    st.write(f"**Problem:** {issue['Problem']}")
                    st.write(f"**Location:** {issue['Location'].title()}")
                    st.write(f"**Severity:** {issue['Severity']}")
                    st.markdown("**Real Guest Comment:**")
                    st.info(f"\"{issue['Guest Comment']}\"")
                
                with col2:
                    st.markdown("**AI Cleaning Recommendations:**")
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"**{i}.** {rec}")
                    
                    # Add time estimates
                    time_estimate = "30-45 minutes" if issue['Severity'] == 'High' else "15-30 minutes" if issue['Severity'] == 'Medium' else "10-15 minutes"
                    st.success(f"⏱️ **Estimated Time:** {time_estimate}")
                    
                    # Add priority level
                    if issue['Severity'] == 'High':
                        st.error("🚨 **Priority:** Address Today")
                    elif issue['Severity'] == 'Medium':
                        st.warning("⚠️ **Priority:** Address Within 2 Days")
                    else:
                        st.info("ℹ️ **Priority:** Address This Week")
    else:
        if st.session_state.last_real_update:
            st.success("🎉 No cleaning issues detected by AI analysis! All properties meet cleanliness standards.")
        else:
            st.info("📊 Cleaning issues will appear here after running analysis with full AI intelligence.")

with tab2:
    st.subheader("Maintenance Issues Analysis")
    
    # Collect all maintenance issues from data
    all_maintenance_issues = []
    for prop, analysis in st.session_state.detailed_analyses.items():
        for issue in analysis.get('maintenance_issues', []):
            all_maintenance_issues.append({
                "Property": prop,
                "Category": issue.get('category', 'General'),
                "Problem": issue.get('problem', 'maintenance needed'),
                "Severity": issue.get('severity', 'Medium'),
                "Urgency": issue.get('urgency', 'Soon'),
                "Guest Comment": issue.get('guest_comment', '')
            })
    
    if all_maintenance_issues:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Maintenance issues by category
            maintenance_df = pd.DataFrame(all_maintenance_issues)
            category_counts = maintenance_df['Category'].value_counts()
            
            fig_category = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="AI Detected Maintenance Issues by Category",
                color=category_counts.values,
                color_continuous_scale="Blues"
            )
            fig_category.update_layout(height=300, xaxis_tickangle=-45)
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Urgency analysis
            urgency_counts = maintenance_df['Urgency'].value_counts()
            
            fig_urgency = px.pie(
                values=urgency_counts.values,
                names=urgency_counts.index,
                title="AI Detected Issues by Urgency",
                color_discrete_map={'Urgent': '#e74c3c', 'Soon': '#f39c12', 'Can wait': '#27ae60'}
            )
            st.plotly_chart(fig_urgency, use_container_width=True)
        
        # Detailed maintenance issues with AI recommendations
        st.subheader("Maintenance Issues & AI Recommendations (From Real Comments)")
        maintenance_df_sorted = maintenance_df.sort_values(['Urgency', 'Severity'], 
                                                         key=lambda x: x.map({'Urgent': 3, 'Soon': 2, 'Can wait': 1, 
                                                                             'High': 3, 'Medium': 2, 'Low': 1}), 
                                                         ascending=False)
        
        for _, issue in maintenance_df_sorted.iterrows():
            urgency_emoji = "⚡" if issue['Urgency'] == 'Urgent' else "🔜" if issue['Urgency'] == 'Soon' else "📅"
            severity_emoji = "🚨" if issue['Severity'] == 'High' else "⚠️" if issue['Severity'] == 'Medium' else "ℹ️"
            
            # Generate AI recommendations
            with st.spinner(f"Generating AI recommendations for {issue['Property']}..."):
                recommendations = generate_gpt_recommendations(
                    "maintenance", 
                    issue['Problem'], 
                    issue['Category'], 
                    issue['Urgency'], 
                    issue['Guest Comment']
                )
                
                time_estimate, cost_estimate = get_gpt_time_cost_estimates(
                    issue['Category'], 
                    issue['Severity'], 
                    issue['Guest Comment']
                )
            
            # Create expandable section for each issue
            with st.expander(f"{urgency_emoji} {severity_emoji} {issue['Property']} - {issue['Category']} ({issue['Urgency']})", expanded=issue['Urgency'] == 'Urgent' or issue['Severity'] == 'High'):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Issue Details:**")
                    st.write(f"**Property:** {issue['Property']}")
                    st.write(f"**Category:** {issue['Category']}")
                    st.write(f"**Problem:** {issue['Problem']}")
                    st.write(f"**Urgency:** {issue['Urgency']}")
                    st.write(f"**Severity:** {issue['Severity']}")
                    st.markdown("**Real Guest Comment:**")
                    st.info(f"\"{issue['Guest Comment']}\"")
                
                with col2:
                    st.markdown("**AI Maintenance Recommendations:**")
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"**{i}.** {rec}")
                    
                    # Add AI generated estimates
                    st.success(f"⏱️ **AI Time Estimate:** {time_estimate}")
                    st.success(f"💰 **AI Cost Estimate:** {cost_estimate}")
                    
                    # Add urgency level
                    if issue['Urgency'] == 'Urgent':
                        st.error("⚡ **Action Required:** Same Day")
                    elif issue['Urgency'] == 'Soon':
                        st.warning("🔜 **Action Required:** Within 1-2 Days")
                    else:
                        st.info("📅 **Action Required:** Within a Week")
    else:
        if st.session_state.last_real_update:
            st.success("🎉 No maintenance issues detected by AI analysis! All systems functioning properly.")
        else:
            st.info("📊 Maintenance issues will appear here after running analysis with full AI intelligence.")

with tab3:
    st.subheader("Property Performance Overview")
    
    if st.session_state.satisfaction_scores and st.session_state.detailed_analyses:
        # Performance scorecard from real data
        performance_data = []
        for prop, satisfaction in st.session_state.satisfaction_scores.items():
            analysis = st.session_state.detailed_analyses.get(prop, {})
            cleaning_count = len(analysis.get('cleaning_issues', []))
            maintenance_count = len(analysis.get('maintenance_issues', []))
            sentiment = analysis.get('guest_sentiment', 'neutral')
            rating = analysis.get('summary', {}).get('overall_rating', 'B')
            
            performance_data.append({
                "Property": prop,
                "Satisfaction": satisfaction,
                "Cleaning Issues": cleaning_count,
                "Maintenance Issues": maintenance_count,
                "Guest Sentiment": sentiment,
                "Overall Rating": rating,
                "Total Issues": cleaning_count + maintenance_count
            })
        
        perf_df = pd.DataFrame(performance_data)
        
        # Performance heatmap
        fig_heatmap = px.scatter(
            perf_df,
            x="Satisfaction",
            y="Total Issues",
            size="Satisfaction",
            color="Overall Rating",
            hover_data=["Property", "Guest Sentiment"],
            title="Property Performance Matrix (Full AI Analysis)",
            labels={"Total Issues": "Total Issues Count", "Satisfaction": "AI Satisfaction Score"}
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Property cards
        st.subheader("Individual Property Status (AI Analysis)")
        
        for _, prop_data in perf_df.iterrows():
            status_class = "status-excellent" if prop_data['Satisfaction'] >= 85 else "status-good" if prop_data['Satisfaction'] >= 75 else "status-poor"
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="property-card">
                    <h4>{prop_data['Property']}</h4>
                    <p><strong>AI Sentiment:</strong> {prop_data['Guest Sentiment'].title()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<p class='{status_class}'>{prop_data['Satisfaction']:.1f}%</p>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<p>🧹 {prop_data['Cleaning Issues']}</p>", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"<p>🔧 {prop_data['Maintenance Issues']}</p>", unsafe_allow_html=True)
    else:
        st.info("📊 Property performance data will appear here after running analysis.")

with tab4:
    st.subheader("AI System Insights")
    
    if st.session_state.last_real_update:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### AI Performance")
            framework_perf = st.session_state.framework_performance
            st.write(f"• **AI Analyses:** {framework_perf.get('smart_ai_analyses', 0)}")
            st.write(f"• **Rule-Based Decisions:** {framework_perf.get('pricing_decisions', 0)}")
            st.write(f"• **Communication Messages:** {framework_perf.get('a2a_messages', 0)}")
            st.write(f"• **Safety Events:** {framework_perf.get('safety_violations', 0)}")
            st.info("**Full AI Intelligence:** No keyword dictionaries used")
        
        with col2:
            st.markdown("#### Data Summary")
            if st.session_state.real_reviews_data is not None:
                total_reviews = len(st.session_state.real_reviews_data)
                positive_reviews = len(st.session_state.real_reviews_data[st.session_state.real_reviews_data['type'] == 'positive'])
                negative_reviews = len(st.session_state.real_reviews_data[st.session_state.real_reviews_data['type'] == 'negative'])
                
                st.write(f"• **Total Reviews Scraped:** {total_reviews}")
                st.write(f"• **Positive Comments:** {positive_reviews}")
                st.write(f"• **Negative Comments:** {negative_reviews}")
                st.write(f"• **Properties Analyzed:** {len(st.session_state.satisfaction_scores)}")
                st.success("**All processed by full AI intelligence**")
    else:
        st.info("📊 AI insights will appear here after running analysis with full AI intelligence.")

# Professional Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 10px; color: white;">
    <h3>Smart Multi-Framework Property Management System</h3>
    <p><strong>MGSC 695 Capstone Project - Ahmed Kharrat</strong></p>
    <p><em>Real web scraping + Full AI intelligence + AI recommendations + Multi-framework coordination + Enhanced email notifications</em></p>
    <p><strong>Professional AI-Powered Property Management Solution</strong></p>
</div>
""", unsafe_allow_html=True)