import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Branding & Styling
st.set_page_config(page_title="McLaren Aero Analysis", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0b0b; color: #f5f5f5; }
   .stMetric { 
        background-color: #1a1a1a !important; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #FF8700;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    /* This forces the metric labels and values to be white */
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ Aero Performance Dashboard")
st.subheader("Engineer: Imaad Akber | Aerospace Engineer")

# 2. Sidebar Settings
st.sidebar.header("🛠️ Tool Settings")
user_link = st.sidebar.text_input(
    "Analyze Custom Dataset (Paste Link):", 
    placeholder="https://docs.google.com/spreadsheets/d/..."
)

DEFAULT_LINK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSSu46E0kT_l4m3QpITpMDnLOoVDWt-8nyx0G7-8RjqzpgpyyGGAydV7Uf9XiDHTl_QtUvmzZYnaydL/pub?gid=0&single=true&output=csv"

if user_link:
    if "pub?" in user_link:
        CSV_URL = user_link
    elif "/edit" in user_link:
        base = user_link.split('/edit')[0]
        CSV_URL = f"{base}/export?format=csv"
    else:
        CSV_URL = user_link
else:
    CSV_URL = DEFAULT_LINK

# 3. Main Logic
try:
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    
    if all(col in df.columns for col in ['Cl (Total)', 'FRH', 'RRH']):
        
        # --- TOP LEVEL METRICS ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Max Downforce", f"{df['Cl (Total)'].max():.3f}")
        m2.metric("Optimal Run ID", df.loc[df['Cl (Total)'].idxmax(), 'Run_ID'])
        m3.metric("Total Test Runs", len(df))

        st.divider()

        # --- AERO BALANCE GAUGE ---
        if 'Cl_front' in df.columns:
            df['Aero_Balance'] = (df['Cl_front'] / df['Cl (Total)']) * 100
            
            st.subheader("⚖️ Aero Balance & Center of Pressure ($C_{oP}$)")
            selected_run = st.selectbox("Select Run for Balance Analysis", df['Run_ID'])
            current_bal = df.loc[df['Run_ID'] == selected_run, 'Aero_Balance'].values[0]
            
            c1, c2 = st.columns([2, 1])
            with c1:
                fig_bal = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = current_bal,
                    number = {'suffix': "% Front"},
                    gauge = {
                        'axis': {'range': [35, 55]},
                        'bar': {'color': "#FF8700"},
                        'steps': [
                            {'range': [35, 42], 'color': "#333333"},
                            {'range': [42, 48], 'color': "#444444"},
                            {'range': [48, 55], 'color': "#333333"}
                        ],
                        'threshold': {'line': {'color': "white", 'width': 4}, 'value': 45}
                    }
                ))
                fig_bal.update_layout(paper_bgcolor='#0b0b0b', font_color='white', height=250, margin=dict(t=0, b=0))
                st.plotly_chart(fig_bal, use_container_width=True)
            
            with c2:
                st.write("#### Engineering Insight")
                if current_bal > 48:
                    st.error("⚠️ OVERSTEER RISK: High Front Bias.")
                elif current_bal < 41:
                    st.warning("⚠️ UNDERSTEER RISK: High Rear Bias.")
                else:
                    st.success("✅ OPTIMAL SETUP: Balance within window.")

        # --- 2D AERO CONTOUR MAP ---
        st.divider()
        st.subheader("🗺️ 2D Setup Window (Contour Map)")
        
        fig_contour = go.Figure(data=go.Contour(
            x=df['FRH'], y=df['RRH'], z=df['Cl (Total)'],
            colorscale='Turbo', connectgaps=True,
            contours=dict(showlabels=True, labelfont=dict(color='white')),
            hoverinfo='skip'
        ))
        
        fig_contour.add_trace(go.Scatter(
            x=df['FRH'], y=df['RRH'], mode='markers',
            customdata=df[['Run_ID', 'Cl (Total)']],
            hovertemplate="<b>%{customdata[0]}</b><br>FRH: %{x}mm<br>RRH: %{y}mm<br>Cl: %{customdata[1]:.3f}<extra></extra>",
            marker=dict(size=12, color='white', line=dict(width=2, color='black')),
            showlegend=False
        ))

        fig_contour.update_layout(
            plot_bgcolor='#0b0b0b', paper_bgcolor='#0b0b0b', font_color='white',
            xaxis=dict(title='Front Ride Height (mm)', gridcolor='#333333'),
            yaxis=dict(title='Rear Ride Height (mm)', gridcolor='#333333'),
            margin=dict(l=0, r=0, b=0, t=30)
        )
        st.plotly_chart(fig_contour, use_container_width=True)

        # --- 3D AERO MAP ---
        st.divider()
        st.subheader("🏎️ 3D Aerodynamic Ride Height Map")
        fig_3d = px.scatter_3d(
            df, x='FRH', y='RRH', z='Cl (Total)', color='Cl (Total)',
            hover_name='Run_ID', color_continuous_scale='Turbo'
        )
        fig_3d.update_traces(
            marker=dict(size=12, line=dict(width=2, color='white')),
            hovertemplate="<b>%{hovertext}</b><br>FRH: %{x}<br>RRH: %{y}<br>Cl: %{z}<extra></extra>"
        )
        fig_3d.update_layout(scene=dict(bgcolor='#0b0b0b'), paper_bgcolor='#0b0b0b', font_color='white')
        st.plotly_chart(fig_3d, use_container_width=True)

        # --- RAW DATA TABLE (VITAL FOR VERIFICATION) ---
        st.divider()
        st.subheader("📊 Raw Telemetry Data")
        st.write("Full dataset used for the visualizations above.")
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        # --- TECHNICAL GLOSSARY ---
        with st.expander("📖 Technical Glossary & Definitions"):
            st.write("""
            - **$C_l$ (Total):** The overall Coefficient of Lift (Downforce). Higher is better for grip.
            - **FRH / RRH:** Front and Rear Ride Heights in millimeters.
            - **Aero Balance:** The percentage of total downforce acting on the front axle. 
            - **Contour Map:** A 2D visualization using mathematical interpolation to predict performance between test points.
            """)

    else:
        st.warning(f"Header Mismatch. Need: 'Cl (Total)', 'FRH', 'RRH'")

except Exception as e:
    st.error(f"⚠️ Telemetry Error: {e}")