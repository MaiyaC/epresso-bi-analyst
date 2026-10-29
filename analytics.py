
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
