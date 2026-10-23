
import streamlit as st
import pandas as pd

# Set up the application
st.set_page_config(
    page_title="E-Presso Business Intelligence",
    layout="wide"
)

# Dashboard title
st.title("E-Presso Business Intelligence Dashboard")
st.write("Welcome to the E-Presso Sales Analytics Application!")

# Data upload section
st.header("Upload Your Data")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

# Display uploaded data
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("File uploaded successfully!")

    # Preview the dataset
    st.subheader("Dataset Preview")
    st.dataframe(df)

    # Display dataset information
    st.subheader("Dataset Information")
    st.write("Number of rows:", df.shape[0])
    st.write("Number of columns:", df.shape[1])

else:
    st.info("Please upload a CSV file to begin.")

