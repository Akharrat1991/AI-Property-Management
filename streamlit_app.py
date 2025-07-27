import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime
from unified_property_management import UnifiedPropertyManager

# 📌 Load API keys and email credentials from Streamlit Secrets
APIFY_API_KEY = st.secrets["APIFY_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]
CLEANING_TEAM_EMAIL = st.secrets["CLEANING_TEAM_EMAIL"]

# Title & Layout
st.set_page_config(page_title="AI Property Management Dashboard", layout="wide")
st.title("🏠 Unified AI Property Management Dashboard")

# Initialize Manager
manager = UnifiedPropertyManager(
    apify_key=APIFY_API_KEY,
    openai_key=OPENAI_API_KEY,
    sender_email=SENDER_EMAIL,
    email_password=GMAIL_APP_PASSWORD,
    cleaning_team_email=CLEANING_TEAM_EMAIL,
)

# Run analysis on button click
if st.button("🚀 Run Full Analysis"):
    with st.spinner("Running full analysis... this may take a few minutes..."):
        result = asyncio.run(manager.run_complete_analysis())

    st.success("✅ Analysis Completed!")

    st.header("📊 Guest Satisfaction Scores")
    satisfaction_df = pd.DataFrame([
        {"Property": prop, "Satisfaction (%)": score}
        for prop, score in manager.satisfaction_scores.items()
    ])
    st.dataframe(satisfaction_df)

    st.header("🧹 Cleaning Issues Detected")
    if manager.cleaning_issues:
        for prop, issues in manager.cleaning_issues.items():
            with st.expander(f"{prop} ({len(issues)})"):
                for idx, comment in enumerate(issues, 1):
                    st.write(f"{idx}. {comment}")
    else:
        st.info("No cleaning issues found.")

    st.header("🔧 Maintenance Issues Detected")
    if manager.maintenance_issues:
        for prop, issues in manager.maintenance_issues.items():
            with st.expander(f"{prop} ({len(issues)})"):
                for idx, comment in enumerate(issues, 1):
                    st.write(f"{idx}. {comment}")
    else:
        st.info("No maintenance issues found.")

    st.header("💰 Dynamic Pricing Adjustments")
    if manager.pricing_adjustments:
        pricing_df = pd.DataFrame([
            {
                "Property": prop,
                "Original Price": data['original_price'],
                "New Price": data['new_price'],
                "Change ($)": data['price_change'],
                "Change (%)": f"{data['percentage_change']:+.1f}%",
                "Reason": data['reason']
            }
            for prop, data in manager.pricing_adjustments.items()
        ])
        st.dataframe(pricing_df)
    else:
        st.info("No pricing changes needed.")

    st.header("📋 Summary")
    st.markdown(f"""
- Properties Analyzed: **{result['properties_analyzed']}**
- Average Satisfaction: **{result['average_satisfaction']:.1f}%**
- Cleaning Issues: **{result['cleaning_issues']}**
- Maintenance Issues: **{result['maintenance_issues']}**
- Pricing Adjustments: **{result['pricing_adjustments']}**
- Revenue Impact: **${result['revenue_impact']:+.0f} per night**
- Emails Sent: **{result['emails_sent']}**
- Last Run: {datetime.now():%Y-%m-%d %H:%M:%S}
""")
else:
    st.info("Click the button above to start the full property analysis.")
