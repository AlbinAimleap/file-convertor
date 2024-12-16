import streamlit as st
import pandas as pd
import json
import os
from io import StringIO, BytesIO

st.set_page_config(
    page_title="File Format Converter",
    page_icon="🔄",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTitle {
        color: #2c3e50;
        font-size: 3rem !important;
        padding-bottom: 2rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #2ecc71;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stSelectbox {
        margin: 2rem 0;
    }
    .stDownloadButton>button {
        width: 100%;
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("File Format Converter")

# Add description
st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
        Convert your files between different formats easily and quickly.<br>
        Supported formats: CSV, JSON, Excel (XLSX), and TSV
    </div>
""", unsafe_allow_html=True)

def detect_file_type(file):
    extension = os.path.splitext(file.name)[1].lower()
    return extension[1:] if extension else None

def read_file(uploaded_file, file_type):
    if file_type == 'csv':
        return pd.read_csv(uploaded_file)
    elif file_type == 'json':
        return pd.read_json(uploaded_file)
    elif file_type == 'xlsx':
        return pd.read_excel(uploaded_file)
    elif file_type == 'tsv':
        return pd.read_csv(uploaded_file, sep='\t')
    return None

def convert_file(df, output_format, original_filename):
    df.fillna("", inplace=True)
    base_name = os.path.splitext(original_filename)[0]
    output_filename = f"{base_name}.{output_format}"

    if output_format == 'csv':
        output = df.to_csv(index=False)
        mime = 'text/csv'
    elif output_format == 'json':
        output = df.to_dict(orient='records')
        output = json.dumps(output, indent=4)
        mime = 'application/json'
    elif output_format == 'xlsx':
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return output.getvalue(), output_filename, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif output_format == 'tsv':
        output = df.to_csv(sep='\t', index=False)
        mime = 'text/tab-separated-values'

    return output.encode('utf-8'), output_filename, mime

# Create two columns for better layout
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'json', 'xlsx', 'tsv'])

if uploaded_file is not None:
    input_file_type = detect_file_type(uploaded_file)
    st.info(f"📁 Detected file type: {input_file_type.upper()}")

    output_format = st.selectbox(
        "Select output format",
        ['csv', 'json', 'xlsx', 'tsv'],
        index=['csv', 'json', 'xlsx', 'tsv'].index(input_file_type),
        format_func=lambda x: x.upper()
    )

    if st.button("Convert File"):
        with st.spinner('Converting your file...'):
            df = read_file(uploaded_file, input_file_type)
            if df is not None:
                converted_data, output_filename, mime_type = convert_file(df, output_format, uploaded_file.name)
            
                st.success('✅ Conversion completed successfully!')
            
                st.download_button(
                    label="📥 Download Converted File",
                    data=converted_data,
                    file_name=output_filename,
                    mime=mime_type
                )
            
                # Preview the data
                st.markdown("### Data Preview")
                st.dataframe(df.head(5), use_container_width=True)
            else:
                st.error("❌ Error reading the file. Please check if the file is valid.")
