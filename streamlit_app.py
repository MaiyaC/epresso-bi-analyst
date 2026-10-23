
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="E-Presso Business Intelligence",
    layout="wide"
)

st.title("E-Presso Business Intelligence Dashboard")
st.write("Explore E-Presso sales and business performance.")

# Upload the original datasets
st.header("1. Upload E-Presso Data")

sales_file = st.file_uploader(
    "Upload Sales.xlsx", type=["xlsx"], key="sales"
)
products_file = st.file_uploader(
    "Upload Products.xlsx", type=["xlsx"], key="products"
)
categories_file = st.file_uploader(
    "Upload Categories.xlsx", type=["xlsx"], key="categories"
)
stores_file = st.file_uploader(
    "Upload the Stores CSV file", type=["csv"], key="stores"
)
survey_file = st.file_uploader(
    "Upload the Survey Excel file", type=["xlsx"], key="survey"
)

if all([sales_file, products_file, categories_file,
        stores_file, survey_file]):

    # Read the uploaded data
    sales = pd.read_excel(sales_file)
    products = pd.read_excel(products_file)
    categories = pd.read_excel(categories_file)
    stores = pd.read_csv(stores_file, sep="\t")
    survey = pd.read_excel(
        survey_file, sheet_name="Survey Results", header=2
    )

    # Check important relationships
    if (products["Product ID"].duplicated().any()
            or categories["Category ID"].duplicated().any()
            or stores["ID"].duplicated().any()):
        st.error("Duplicate IDs found in a lookup table.")
        st.stop()

    # Connect the sales data to lookup tables
    data = sales.merge(
        products, on="Product ID", how="left",
        validate="many_to_one"
    )
    data = data.merge(
        categories, on="Category ID", how="left",
        validate="many_to_one"
    )
    data = data.merge(
        stores[["ID", "City", "StoreType"]],
        left_on="Store ID", right_on="ID",
        how="left", validate="many_to_one"
    )

    data["Date"] = pd.to_datetime(data["Date"])
    data["Revenue"] = pd.to_numeric(
        data["Revenue"], errors="coerce"
    )

    st.success("All five datasets uploaded successfully!")

    # Show revenue calculations
    st.header("2. Business Performance")

    total_revenue = data["Revenue"].sum()
    transaction_count = len(data)

    col1, col2 = st.columns(2)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Sales Records", f"{transaction_count:,}")

    # Revenue by year
    st.subheader("Revenue by Year")

    annual_revenue = (
        data.groupby(data["Date"].dt.year)["Revenue"]
        .sum()
        .sort_index()
    )
    st.bar_chart(annual_revenue)

    # Revenue by sales channel
    st.subheader("Revenue by Sales Channel")

    channel_revenue = (
        data.groupby("StoreType")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(channel_revenue)

    # Preview combined data
    st.header("3. Combined Dataset")
    st.dataframe(data.head(20))

    # Data quality checks
    st.header("4. Data Quality")

    st.write("Missing values by column:")
    st.dataframe(
        data.isna().sum().rename("Missing Values")
    )

    st.write(
        "Duplicate Sales IDs:",
        sales["Sales ID"].duplicated().sum()
    )

    st.write("Survey records:", len(survey))

else:
    st.info("Upload all five E-Presso files to begin.")

