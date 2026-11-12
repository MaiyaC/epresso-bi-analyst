
import pandas as pd


def get_revenue_by_channel(data, year=None, channel=None, store=None):
    """Calculate total revenue by sales channel."""

    data = data.copy()

    if year is not None:
        dates = pd.to_datetime(data["Date"], errors="coerce")
        available_years = dates.dt.year.dropna().unique()
        if year not in available_years:
            return {"status": "invalid_parameter", "message": "Year is not available in the data."}
        data = data[dates.dt.year == year]

    if channel is not None:
        if channel not in data["StoreType"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Channel is not available in the data."}
        data = data[data["StoreType"] == channel]

    if store is not None:
        if store not in data["Store ID"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Store is not available in the data."}
        data = data[data["Store ID"] == store]
    
    revenue_by_channel = (
        data.groupby("StoreType", dropna=False)["Revenue"]
        .sum()
        .reset_index()
    )

    total_revenue = float(data["Revenue"].sum())

    results = {
        "total_revenue": total_revenue,
        "channels": {}
    }

    for _, row in revenue_by_channel.iterrows():
        channel = str(row["StoreType"])
        revenue = float(row["Revenue"])

        results["channels"][channel] = {
            "revenue": revenue,
            "percentage": (
                round(revenue / total_revenue * 100, 2)
                if total_revenue != 0 else 0
            )
        }

    return results


def get_category_performance(data, year=None, channel=None, store=None):
    """Analyze revenue performance by product category."""

    data = data.copy()

    if year is not None:
        dates = pd.to_datetime(data["Date"], errors="coerce")
        available_years = dates.dt.year.dropna().unique()
        if year not in available_years:
            return {"status": "invalid_parameter", "message": "Year is not available in the data."}
        data = data[dates.dt.year == year]

    if channel is not None:
        if channel not in data["StoreType"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Channel is not available in the data."}
        data = data[data["StoreType"] == channel]

    if store is not None:
        if store not in data["Store ID"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Store is not available in the data."}
        data = data[data["Store ID"] == store]
    
    category_revenue = (
        data.groupby("Category", dropna=False)["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    total_revenue = float(data["Revenue"].sum())

    categories = []

    for category, revenue in category_revenue.items():
        revenue = float(revenue)

        categories.append({
            "category": str(category),
            "revenue": revenue,
            "percentage": (
                round(revenue / total_revenue * 100, 2)
                if total_revenue != 0 else 0
            )
        })

    return {
        "total_revenue": total_revenue,
        "categories": categories,
        "highest_revenue_category": (
            categories[0] if categories else None
        ),
        "lowest_revenue_category": (
            categories[-1] if categories else None
        )
    }


def get_monthly_revenue_share(data, year=None, channel=None, store=None):
    """Calculate each month's share of annual revenue."""
    df = data.copy()

    if year is not None:
        dates = pd.to_datetime(df["Date"], errors="coerce")
        if year not in dates.dt.year.dropna().unique():
            return {"status": "invalid_parameter", "message": "Year is not available in the data."}
        df = df[dates.dt.year == year].copy()

    if channel is not None:
        if channel not in df["StoreType"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Channel is not available in the data."}
        df = df[df["StoreType"] == channel].copy()

    if store is not None:
        if store not in df["Store ID"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Store is not available in the data."}
        df = df[df["Store ID"] == store].copy()
    
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    valid = df.dropna(subset=["Date", "Revenue"]).copy()

    if valid.empty:
        return {"status": "insufficient_data", "message": "No valid dated revenue records."}

    valid["Year"] = valid["Date"].dt.year
    valid["Month"] = valid["Date"].dt.month

    annual = valid.groupby("Year")["Revenue"].sum()
    monthly = valid.groupby(["Year", "Month"])["Revenue"].sum()

    results = []
    for (year, month), revenue in monthly.items():
        annual_total = float(annual.loc[year])
        results.append({
            "year": int(year),
            "month": int(month),
            "month_name": pd.Timestamp(2000, int(month), 1).strftime("%B"),
            "revenue": float(revenue),
            "annual_revenue": annual_total,
            "share_percent": (
                round(float(revenue) / annual_total * 100, 2)
                if annual_total != 0 else None
            )
        })

    return {
        "status": "success",
        "scope": "supplied_data",
        "monthly_results": results
    }


def get_store_trend(data, year=None, channel=None, store=None):
    """Compare annual revenue trends for physical stores."""
    df = data.copy()

    
    if year is not None:
        dates = pd.to_datetime(df["Date"], errors="coerce")
        if year not in dates.dt.year.dropna().unique():
            return {"status": "invalid_parameter", "message": "Year is not available in the data."}
        df = df[dates.dt.year.isin([year - 1, year])].copy()

    if channel is not None:
        if channel not in df["StoreType"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Channel is not available in the data."}
        df = df[df["StoreType"] == channel].copy()

    if store is not None:
        if store not in df["Store ID"].dropna().unique():
            return {"status": "invalid_parameter", "message": "Store is not available in the data."}
        df = df[df["Store ID"] == store].copy()
    
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    required = ["Store ID", "StoreType", "Date", "Revenue"]
    if any(col not in df.columns for col in required):
        return {"status": "insufficient_data", "message": "Required store fields are missing."}

    physical = df[
        df["StoreType"].astype(str).str.strip().eq("Brick & Mortar")
    ].dropna(subset=["Date", "Revenue"]).copy()

    if physical.empty:
        return {"status": "insufficient_data", "message": "No physical-store sales are available."}

    physical["Year"] = physical["Date"].dt.year

    grouped = (
        physical.groupby(["Store ID", "Year"])["Revenue"]
        .sum()
        .reset_index()
        .sort_values(["Store ID", "Year"])
    )

    results = []
    for store_id, rows in grouped.groupby("Store ID"):
        previous_revenue = None
        for _, row in rows.iterrows():
            revenue = float(row["Revenue"])
            growth = None
            if previous_revenue is not None and previous_revenue != 0:
                growth = round(
                    (revenue - previous_revenue) / previous_revenue * 100, 2
                )

            results.append({
                "store_id": str(store_id),
                "year": int(row["Year"]),
                "revenue": revenue,
                "growth_percent_vs_previous_available_year": growth
            })
            previous_revenue = revenue

    if year is not None:
        results = [row for row in results if row["year"] == year]
    
    return {
        "status": "success",
        "scope": "physical_stores_in_supplied_data",
        "store_trends": results
    }


def get_data_quality_report(data):
    """Summarize missing values and duplicate sales records."""
    if data.empty:
        return {"status": "insufficient_data", "message": "No sales records available."}

    missing = {
        str(column): int(count)
        for column, count in data.isna().sum().items()
        if count > 0
    }

    duplicate_ids = (
        int(data["Sales ID"].duplicated().sum())
        if "Sales ID" in data.columns else None
    )

    return {
        "status": "success",
        "total_records": int(len(data)),
        "missing_values_by_column": missing,
        "duplicate_sales_ids": duplicate_ids,
        "note": (
            "Missing City values may be expected for website transactions. "
            "Review missing values in context before treating them as errors."
        )
    }



def get_customer_satisfaction_analysis(data, survey, year=None, channel=None, store=None):
    """Compare store-year satisfaction scores with annual store revenue."""

    required_survey = ["Store ID", "Year", "Satisfaction"]
    required_sales = ["Store ID", "Date", "Revenue", "StoreType"]

    if any(col not in survey.columns for col in required_survey):
        return {
            "status": "insufficient_data",
            "message": "Required survey fields are missing."
        }

    if any(col not in data.columns for col in required_sales):
        return {
            "status": "insufficient_data",
            "message": "Required sales fields are missing."
        }

    surveys = survey.copy()
    sales = data.copy()

    if year is not None:
        dates = pd.to_datetime(sales["Date"], errors="coerce")
        if year not in dates.dt.year.dropna().unique():
            return {"status": "invalid_parameter", "message": "Year is not available in the data."}
        sales = sales[dates.dt.year == year].copy()
        survey_years = pd.to_numeric(
            surveys["Year"].astype(str).str.extract(r"(\d{4})")[0],
            errors="coerce"
        )
        surveys = surveys[survey_years == year].copy()

    if channel is not None:
        if channel != "Brick & Mortar":
            return {
                "status": "invalid_parameter",
                "message": "Customer satisfaction analysis supports physical stores only."
            }

    if store is not None:
        if store not in sales["Store ID"].dropna().astype(str).unique():
            return {"status": "invalid_parameter", "message": "Store is not available in the data."}
        sales = sales[sales["Store ID"].astype(str) == str(store)].copy()
        surveys = surveys[surveys["Store ID"].astype(str) == str(store)].copy()

    surveys["Year"] = pd.to_numeric(
        surveys["Year"].astype(str).str.extract(r"(\d{4})")[0],
        errors="coerce"
    )
    surveys["Satisfaction"] = pd.to_numeric(
        surveys["Satisfaction"], errors="coerce"
    )
    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
    sales["Year"] = sales["Date"].dt.year

    surveys["Store ID"] = surveys["Store ID"].astype(str).str.strip()
    sales["Store ID"] = sales["Store ID"].astype(str).str.strip()

    surveys = surveys.dropna(
        subset=["Store ID", "Year", "Satisfaction"]
    )
    sales = sales[
        sales["StoreType"].astype(str).str.strip().eq("Brick & Mortar")
    ].dropna(subset=["Date", "Revenue"])

    if surveys.empty or sales.empty:
        return {
            "status": "insufficient_data",
            "message": "No matching valid survey and store sales data."
        }

    if surveys.duplicated(["Store ID", "Year"]).any():
        return {
            "status": "invalid_data",
            "message": "Duplicate store-year survey records were found."
        }

    annual_revenue = (
        sales.groupby(["Store ID", "Year"], as_index=False)["Revenue"]
        .sum()
    )

    comparison = surveys.merge(
        annual_revenue,
        on=["Store ID", "Year"],
        how="inner",
        validate="one_to_one"
    )

    if comparison.empty:
        return {
            "status": "insufficient_data",
            "message": "No matching store-year records were found."
        }

    results = [
        {
            "store_id": str(row["Store ID"]),
            "year": int(row["Year"]),
            "satisfaction": float(row["Satisfaction"]),
            "annual_revenue": float(row["Revenue"])
        }
        for _, row in comparison.iterrows()
    ]

    return {
        "status": "success",
        "scope": "physical_store_years_with_valid_survey_data",
        "average_satisfaction": round(
            float(comparison["Satisfaction"].mean()), 2
        ),
        "store_year_results": results,
        "note": (
            "Satisfaction and revenue can be compared, but their "
            "relationship does not establish causation. "
            "Survey records without valid satisfaction scores are excluded."
        )
    }

