
import streamlit as st
import pandas as pd

st.set_page_config(page_title="E-Presso Business Intelligence", layout="wide")

st.title("E-Presso Business Intelligence Dashboard")
st.write("Welcome to the E-Presso Sales Analytics Application!")

st.header("Upload Your Data")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("File uploaded successfully!")
