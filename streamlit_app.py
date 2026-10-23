
import streamlit as st
import pandas as pd
import altair as alt

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
  # Interactive dashboard filters
    st.header("Dashboard Filters")

    available_years = sorted(
        data["Date"].dt.year.dropna().unique().tolist()
    )

    selected_years = st.multiselect(
        "Select Year(s)",
        options=available_years,
        default=available_years
    )

    selected_categories = st.multiselect(
        "Select Product Category",
        options=sorted(data["Category"].dropna().unique()),
        default=sorted(data["Category"].dropna().unique())
    )

    selected_channels = st.multiselect(
        "Select Sales Channel",
        options=sorted(data["StoreType"].dropna().unique()),
        default=sorted(data["StoreType"].dropna().unique())
    )

    # Apply the selected filters
    data = data[
        data["Date"].dt.year.isin(selected_years)
        & data["Category"].isin(selected_categories)
        & data["StoreType"].isin(selected_channels)
    ].copy()
    # Show revenue calculations
    st.header("2. Business Performance")

    total_revenue = data["Revenue"].sum()
    transaction_count = len(data)

    website_revenue = data.loc[
        data["StoreType"] == "Website", "Revenue"
    ].sum()

    physical_revenue = data.loc[
        data["StoreType"] == "Brick & Mortar", "Revenue"
    ].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Website Revenue", f"${website_revenue:,.2f}")
    col3.metric("Brick & Mortar Revenue", f"${physical_revenue:,.2f}")
    col4.metric("Sales Records", f"{transaction_count:,}")

   # Revenue by year
    st.subheader("Revenue by Year")

    annual_revenue = (
        data.groupby(data["Date"].dt.year)["Revenue"]
        .sum()
        .reset_index()
    )

    annual_revenue.columns = ["Year", "Revenue"]
    annual_revenue["Year"] = annual_revenue["Year"].astype(str)

    # Create the line chart
    line = alt.Chart(annual_revenue).mark_line(
        point=True,
        color="#60A5FA",
        strokeWidth=3
    ).encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("Revenue:Q", title="Total Revenue"),
        tooltip=[
            "Year:N",
            alt.Tooltip("Revenue:Q", format="$,.2f")
        ]
    )

    # Display exact revenue above each year
    labels = alt.Chart(annual_revenue).mark_text(
        align="center",
        baseline="bottom",
        dy=-12,
        color="#60A5FA",
        fontSize=13
    ).encode(
        x="Year:N",
        y="Revenue:Q",
        text=alt.Text("Revenue:Q", format="$,.2f")
    )

    chart = (line + labels).properties(
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

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

