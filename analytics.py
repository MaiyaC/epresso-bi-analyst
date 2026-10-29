
import pandas as pd


def get_revenue_by_channel(data):
    """Calculate total revenue by sales channel."""

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


def get_category_performance(data):
    """Analyze revenue performance by product category."""

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


def get_monthly_revenue_share(data):
    """Calculate each month's share of annual revenue."""
    df = data.copy()
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


def get_store_trend(data):
    """Compare annual revenue trends for physical stores."""
    df = data.copy()
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

