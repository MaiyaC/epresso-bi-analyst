
import streamlit as st
import pandas as pd
import altair as alt
from analytics import (
    get_revenue_by_channel,
    get_category_performance,
    get_monthly_revenue_share,
    get_store_trend,
    get_data_quality_report,
)

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

    original_sales_rows = len(sales)
    original_sales_revenue = pd.to_numeric(
        sales["Revenue"], errors="coerce"
    ).sum()
            
    # Connect the sales data to lookup tables
    data = sales.merge(
        products, on="Product ID", how="left",
        validate="many_to_one"
    )
    
    products_merge_rows = len(data)
    products_merge_revenue = pd.to_numeric(
        data["Revenue"], errors="coerce"
    ).sum()
            
    data = data.merge(
        categories, on="Category ID", how="left",
        validate="many_to_one"
    )
    categories_merge_rows = len(data)
    categories_merge_revenue = pd.to_numeric(
        data["Revenue"], errors="coerce"
    ).sum()

    data = data.merge(
        stores[["ID", "City", "StoreType"]],
        left_on="Store ID", right_on="ID",
        how="left", validate="many_to_one"
    )
    merged_sales_rows = len(data)
    merged_sales_revenue = pd.to_numeric(
        data["Revenue"], errors="coerce"
    ).sum()

    if (original_sales_rows != merged_sales_rows
            or abs(original_sales_revenue - merged_sales_revenue) > 0.01):
        st.error("Data merge changed the sales row count or total revenue.")
        st.stop()
                
    unmatched_products = (~sales["Product ID"].isin(products["Product ID"])).sum()
    unmatched_categories = (~sales["Category ID"].isin(categories["Category ID"])).sum()
    unmatched_stores = (~sales["Store ID"].isin(stores["ID"])).sum()

    if unmatched_products or unmatched_categories or unmatched_stores:
        st.error("Some sales records have unmatched lookup IDs.")
        st.stop()            
    data["Date"] = pd.to_datetime(data["Date"])
    data["Revenue"] = pd.to_numeric(
        data["Revenue"], errors="coerce"
    )
    if data["Revenue"].isna().any():
        st.error("Some sales records have missing or invalid revenue values.")
        st.stop()
    
    st.success("All five datasets uploaded successfully!")

    
    survey_duplicate_count = survey.duplicated(
        subset=["Store ID", "Year"]
    ).sum()

    
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
   # Monthly revenue as a percentage of selected revenue
    st.subheader("Percent of Revenue by Month")

    monthly_data = data.copy()
    monthly_data["Month"] = monthly_data["Date"].dt.month

    monthly_revenue = (
        monthly_data.groupby("Month")["Revenue"]
        .sum()
        .reindex(range(1, 13), fill_value=0)
        .reset_index()
    )

    month_names = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    monthly_revenue["Month Name"] = month_names

    if total_revenue != 0:
        monthly_revenue["Percentage"] = (
            monthly_revenue["Revenue"] / total_revenue * 100
        )
    else:
        monthly_revenue["Percentage"] = 0.0

    monthly_bars = alt.Chart(monthly_revenue).mark_bar(
        color="#60A5FA"
    ).encode(
        x=alt.X(
            "Month Name:N",
            sort=month_names,
            title="Month"
        ),
        y=alt.Y(
            "Percentage:Q",
            title="Percentage of Selected Revenue (%)"
        ),
        tooltip=[
            alt.Tooltip("Month Name:N", title="Month"),
            alt.Tooltip("Revenue:Q", format="$,.2f"),
            alt.Tooltip("Percentage:Q", format=".2f")
        ]
    )

    monthly_labels = alt.Chart(monthly_revenue).mark_text(
        dy=-8,
        color="#60A5FA",
        fontSize=12
    ).encode(
        x=alt.X("Month Name:N", sort=month_names),
        y="Percentage:Q",
        text=alt.Text("Percentage:Q", format=".2f")
    )

    st.altair_chart(
        (monthly_bars + monthly_labels).properties(height=350),
        use_container_width=True
    )

    st.caption(
        "Each month is calculated as a percentage of total "
        "revenue for the currently selected filters."
    )
   # Revenue by sales channel
    st.subheader("Revenue by Sales Channel")

    channel_revenue = (
        data.groupby("StoreType")["Revenue"]
        .sum()
        .reset_index()
    )

    channel_revenue = channel_revenue.sort_values(
        "Revenue", ascending=False
    )

    bars = alt.Chart(channel_revenue).mark_bar(
        color="#60A5FA"
    ).encode(
        x=alt.X(
            "Revenue:Q",
            title="Total Revenue",
            scale=alt.Scale(zero=True)
        ),
        y=alt.Y(
            "StoreType:N",
            title="Sales Channel",
            sort="-x"
        ),
        tooltip=[
            alt.Tooltip("StoreType:N", title="Sales Channel"),
            alt.Tooltip("Revenue:Q", format="$,.2f")
        ]
    )

    labels = alt.Chart(channel_revenue).mark_text(
        align="left",
        baseline="middle",
        dx=6,
        color="#60A5FA",
        fontSize=13
    ).encode(
        x="Revenue:Q",
        y=alt.Y("StoreType:N", sort="-x"),
        text=alt.Text("Revenue:Q", format="$,.2f")
    )

    channel_chart = (bars + labels).properties(
        height=220
    )

    st.altair_chart(channel_chart, use_container_width=True)

    # Preview combined data
    st.header("3. Combined Dataset")
    st.dataframe(data.head(20))

    # Data quality checks
    st.header("4. Data Quality")

    st.write("Missing values by column:")
    st.dataframe(
        data.isna().sum().rename("Missing Values")
    )
    missing_city = data[data["City"].isna()]

    if len(missing_city) > 0:
        website_missing = (
            missing_city["StoreType"] == "Website"
        ).sum()

        if website_missing == len(missing_city):
            st.info(
                "All missing City values belong to website sales. "
                "These transactions do not have a physical store city."
            )
        else:
            st.warning(
                "Some missing City values are associated with "
                "non-website transactions and should be investigated."
            )

    st.write(
        "Duplicate Sales IDs:",
        sales["Sales ID"].duplicated().sum()
    )

    st.write("Survey records:", len(survey))

else:
    st.info("Upload all five E-Presso files to begin.")

