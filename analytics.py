
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
