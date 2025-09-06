import streamlit as st
import pandas as pd
from data_reader.xpr_reader import XPRReader
from data_reader.xpn_reader import XPNReader
import os

st.title("Turbine Data Visualizer")

# Initialize session state
if 'xpr_df' not in st.session_state:
    st.session_state.xpr_df = None
if 'xpn_df' not in st.session_state:
    st.session_state.xpn_df = None

def save_uploaded_file(uploaded_file):
    """Saves the uploaded file to the data directory and returns the path."""
    if not os.path.exists("data"):
        os.makedirs("data")
    filepath = os.path.join("data", uploaded_file.name)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getvalue())
    return filepath

with st.form("my_form"):
    xpr_file = st.file_uploader("Choose a .xpr file", type=["xpr"])
    xpn_file = st.file_uploader("Choose a .xpn file", type=["xpn"])

    # Create a submit button
    submitted = st.form_submit_button("Submit")

if submitted:
    if xpr_file is not None:
        filepath = save_uploaded_file(xpr_file)
        reader = XPRReader(filepath)
        xpr_data_df = reader.read()
        st.dataframe(xpr_data_df)
        if not xpr_data_df.empty:
            st.session_state.xpr_df = xpr_data_df

    if xpn_file is not None:
        filepath = save_uploaded_file(xpn_file)
        reader = XPNReader(filepath)
        xpn_data_df = reader.read()
        st.dataframe(xpn_data_df)
        if not xpn_data_df.empty:
            st.session_state.xpn_df = xpn_data_df

if st.session_state.xpr_df is not None:
    st.write("### Actual XPR Data  ")
    st.dataframe(st.session_state.xpr_df)
    st.write("### Actual XPR Scatter Plot")
    if len(st.session_state.xpr_df.columns) >= 2:
        x_axis = st.selectbox("Select X-axis for Actual XPR", st.session_state.xpr_df.columns, key='xpr_x')
        y_axis = st.selectbox("Select Y-axis for Actual XPR", st.session_state.xpr_df.columns, key='xpr_y')
        st.scatter_chart(st.session_state.xpr_df, x=x_axis, y=y_axis)
    else:
        st.warning("XPR data does not have enough columns for a scatter plot.")

if st.session_state.xpn_df is not None:
    st.write("### Original XPN Data")
    st.dataframe(st.session_state.xpn_df)
    st.write("### Original XPN Scatter Plot")
    if len(st.session_state.xpn_df.columns) >= 2:
        x_axis = st.selectbox("Select X-axis for Original XPN", st.session_state.xpn_df.columns, key='xpn_x')
        y_axis = st.selectbox("Select Y-axis for Original XPN", st.session_state.xpn_df.columns, key='xpn_y')
        st.scatter_chart(st.session_state.xpn_df, x=x_axis, y=y_axis)
    else:
        st.warning("XPN data does not have enough columns for a scatter plot.")

if st.session_state.xpr_df is not None and st.session_state.xpn_df is not None:
    st.write("### Combined Scatter Plot")

    # Add a source column
    xpr_df_copy = st.session_state.xpr_df.copy()
    xpr_df_copy['source'] = 'Actual'
    xpn_df_copy = st.session_state.xpn_df.copy()
    xpn_df_copy['source'] = 'Orignal'

    # Concatenate the dataframes
    combined_df = pd.concat([xpr_df_copy, xpn_df_copy], ignore_index=True)

    # Select axes
    x_axis_combined = st.selectbox("Select X-axis for Combined Plot", combined_df.columns, key='combined_x')
    y_axis_combined = st.selectbox("Select Y-axis for Combined Plot", combined_df.columns, key='combined_y')

    # Plot
    st.scatter_chart(combined_df, x=x_axis_combined, y=y_axis_combined, color='source')
       