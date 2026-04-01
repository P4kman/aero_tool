import streamlit as st
import pandas as pd

# 1. Dashboard Configuration & McLaren Branding
st.set_page_config(page_title="Aero Analysis - Imaad Akber", layout="wide")

# Custom CSS for that MTC (McLaren Technology Centre) look
st.markdown("""
    <style>
    .stApp { background-color: #0b0b0b; color: #f5f5f5; }
    .stMetric { 
        background-color: #1a1a1a; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #FF8700; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Header Section
st.title("Aero Performance Dashboard")
st.write("### Junior Data Analysis & Visualisation Tool")
st.write("Imaad Akber")
st.divider()

# 3. Live Data Connection
# This is your verified Published CSV link
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSSu46E0kT_l4m3QpITpMDnLOoVDWt-8nyx0G7-8RjqzpgpyyGGAydV7Uf9XiDHTl_QtUvmzZYnaydL/pub?gid=0&single=true&output=csv"

try:
    # 4. Data Processing
    df = pd.read_csv(CSV_URL)
    
    # Cleaning headers to ensure no hidden spaces cause errors
    df.columns = df.columns.str.strip()
    
    # Basic Aerospace Math: Lift-to-Drag Ratio (Aerodynamic Efficiency)
    if 'Cl' in df.columns and 'Cd' in df.columns:
        df['L_D_Ratio'] = df['Cl'] / df['Cd']

        # 5. Top-Level Telemetry Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Max Cl (Downforce)", f"{df['Cl'].max():.3f}")
        m2.metric("Min Cd (Drag)", f"{df['Cd'].min():.3f}")
        m3.metric("Avg L/D Ratio", f"{df['L_D_Ratio'].mean():.2f}")
        m4.metric("Test Runs", len(df))

        st.divider()

        # 6. Performance Visualisation
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Performance Curve: Lift Coefficient ($C_l$) vs. Alpha ($\\alpha$)")
            # Using a line chart to show the trend across the angle of attack
            st.line_chart(data=df, x='Alpha', y='Cl')
            st.caption("Standard aerodynamic lift curve used for wing stall and sensitivity analysis.")
            
        with col_right:
            st.subheader("Real-Time Data Feed")
            # Formatting the table for high readability
            st.dataframe(df[['Run_ID', 'Alpha', 'Cl', 'Cd', 'L_D_Ratio']], hide_index=True, use_container_width=True)

        # 7. Download Action
        st.sidebar.header("Data Actions")
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="💾 Export Analysis to CSV",
            data=csv_data,
            file_name="mclaren_aero_report.csv",
            mime="text/csv",
        )

    else:
        st.error("Error: Data structure mismatch. Ensure 'Cl' and 'Cd' headers exist in the sheet.")

except Exception as e:
    st.error(f"⚠️ Telemetry Offline: {e}")
    st.info("Check the Google Sheets publishing settings or the CSV URL.")