import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
import asyncio
from datetime import datetime
from unified_property_management import UnifiedPropertyManager

# Title
st.set_page_config(page_title="AI Property Management Dashboard", layout="wide")
st.title("🏠 Unified AI Property Management Dashboard")

# Initialize Manager
manager = UnifiedPropertyManager()

# Run analysis on button click
if st.button("🚀 Run Full Analysis"):
    with st.spinner("Running full analysis... this may take a few minutes..."):
        result = asyncio.run(manager.run_complete_analysis())

    st.success("Analysis Completed!")

    # Satisfaction Scores
    st.header("📊 Guest Satisfaction Scores")
    satisfaction_df = pd.DataFrame([
        {"Property": k, "Satisfaction (%)": v} for k, v in manager.satisfaction_scores.items()
    ])
    st.dataframe(satisfaction_df)

    # Cleaning Issues
    st.header("🧹 Cleaning Issues Detected")
    if manager.cleaning_issues:
        for prop, issues in manager.cleaning_issues.items():
            with st.expander(f"{prop} ({len(issues)} issues)"):
                for i, comment in enumerate(issues, 1):
                    st.write(f"{i}. {comment}")
    else:
        st.info("No cleaning issues found.")

    # Maintenance Issues
    st.header("🔧 Maintenance Issues Detected")
    if manager.maintenance_issues:
        for prop, issues in manager.maintenance_issues.items():
            with st.expander(f"{prop} ({len(issues)} issues)"):
                for i, comment in enumerate(issues, 1):
                    st.write(f"{i}. {comment}")
    else:
        st.info("No maintenance issues found.")

    # Pricing Adjustments
    st.header("💰 Dynamic Pricing Adjustments")
    if manager.pricing_adjustments:
        pricing_df = pd.DataFrame([
            {
                "Property": k,
                "Original Price": v['original_price'],
                "New Price": v['new_price'],
                "Change ($)": v['price_change'],
                "Change (%)": f"{v['percentage_change']:+.1f}%",
                "Reason": v['reason']
            }
            for k, v in manager.pricing_adjustments.items()
        ])
        st.dataframe(pricing_df)
    else:
        st.info("No pricing changes needed.")

    # Summary
    st.header("📋 Summary")
    st.markdown(f"""
    - Properties Analyzed: **{result['properties_analyzed']}**
    - Average Satisfaction: **{result['average_satisfaction']:.1f}%**
    - Cleaning Issues: **{result['cleaning_issues']}**
    - Maintenance Issues: **{result['maintenance_issues']}**
    - Pricing Adjustments: **{result['pricing_adjustments']}**
    - Revenue Impact: **${result['revenue_impact']:+.0f}** per night
    - Emails Sent: **{result['emails_sent']}**
    - Last Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)
else:
    st.info("Click the button above to start the full property analysis.")
