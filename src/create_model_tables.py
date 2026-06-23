"""Create dashboard-ready model and summary tables from cleaned customer data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from utils import ensure_directory, find_column, print_section, safe_numeric


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
INPUT_PATH = PROCESSED_DIR / "cleaned_customers.csv"


def warn(message: str) -> None:
    print(f"WARNING: {message}")


def save_table(df: pd.DataFrame, filename: str) -> None:
    path = PROCESSED_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved {filename}: {df.shape[0]:,} rows")


def create_churn_summary(df: pd.DataFrame, segment_column: str) -> pd.DataFrame:
    grouped = df.groupby(segment_column, dropna=False).agg(total_customers=(segment_column, "size")).reset_index()
    if "churn_flag" in df.columns:
        churn = df.groupby(segment_column, dropna=False)["churn_flag"].agg(
            churned_customers="sum", churn_rate="mean"
        ).reset_index()
        grouped = grouped.merge(churn, on=segment_column, how="left")
    if "revenue_at_risk" in df.columns:
        risk = df.groupby(segment_column, dropna=False)["revenue_at_risk"].sum().reset_index()
        grouped = grouped.merge(risk, on=segment_column, how="left")
    return grouped


def create_service_summary(df: pd.DataFrame) -> pd.DataFrame | None:
    service_columns = [
        column
        for column in df.columns
        if any(token in column for token in ["internet_service", "phone_service", "streaming", "security", "backup", "support"])
    ]
    if not service_columns:
        return None

    frames: list[pd.DataFrame] = []
    for column in service_columns:
        summary = create_churn_summary(df, column).rename(columns={column: "service_value"})
        summary.insert(0, "service_type", column)
        frames.append(summary)
    return pd.concat(frames, ignore_index=True)


def create_revenue_risk_summary(df: pd.DataFrame) -> pd.DataFrame:
    preferred_segments = [
        "customer_value_segment",
        "contract_group",
        "tenure_group",
        "monthly_charge_band",
        "payment_group",
    ]
    segment_columns = [column for column in preferred_segments if column in df.columns]
    if not segment_columns:
        return pd.DataFrame(
            {"segment_type": ["all_customers"], "segment": ["All Customers"], "revenue_at_risk": [df["revenue_at_risk"].sum()]}
        )

    frames: list[pd.DataFrame] = []
    for column in segment_columns:
        summary = df.groupby(column, dropna=False)["revenue_at_risk"].sum().reset_index()
        summary = summary.rename(columns={column: "segment"})
        summary.insert(0, "segment_type", column)
        frames.append(summary)
    return pd.concat(frames, ignore_index=True)


def create_retention_curve(df: pd.DataFrame) -> pd.DataFrame | None:
    """Approximate survival retention curve from tenure and churn status."""
    tenure_column = "tenure_in_months"
    if tenure_column not in df.columns or "churn_flag" not in df.columns:
        return None

    working = df.copy()
    working[tenure_column] = safe_numeric(working[tenure_column])
    working["churn_flag"] = safe_numeric(working["churn_flag"])
    working = working.dropna(subset=[tenure_column, "churn_flag"])
    if working.empty:
        return None

    if "contract_group" in working.columns:
        segment_column = "contract_group"
    elif "contract" in working.columns:
        segment_column = "contract"
    else:
        segment_column = None

    if segment_column is not None:
        working["_segment"] = working[segment_column].astype("string").fillna("Unknown")
    else:
        working["_segment"] = "All Customers"

    # This is an approximate survival curve because the source data is a
    # customer snapshot, not true longitudinal event-history data.
    # The hazard at month m is estimated from customers whose observed tenure is
    # at least m and whose churn flag is set at exactly month m.
    records: list[dict[str, object]] = []
    for segment, segment_df in working.groupby("_segment", dropna=False):
        max_tenure = int(segment_df[tenure_column].max())
        survival_rate = 1.0
        for month in range(0, max_tenure + 1):
            customers_at_risk = int(segment_df[tenure_column].ge(month).sum())
            churn_events = int(segment_df["churn_flag"].eq(1).where(segment_df[tenure_column].eq(month), False).sum())
            monthly_churn_hazard = churn_events / customers_at_risk if customers_at_risk > 0 else 0
            survival_rate *= 1 - monthly_churn_hazard
            records.append(
                {
                    "segment": segment,
                    "tenure_month": month,
                    "customers_at_risk": customers_at_risk,
                    "churn_events": churn_events,
                    "monthly_churn_hazard": monthly_churn_hazard,
                    "survival_rate": survival_rate,
                }
            )
    return pd.DataFrame(records)


def main() -> int:
    print_section("Create Dashboard Model Tables")
    ensure_directory(PROCESSED_DIR)
    if not INPUT_PATH.exists():
        print(f"ERROR: {INPUT_PATH} does not exist. Run python src/clean_data.py first.")
        return 1

    df = pd.read_csv(INPUT_PATH, low_memory=False)
    save_table(df, "fact_customers.csv")

    summary_specs = [
        ("churn_summary_by_contract.csv", ["contract_group", "contract", "contract_type"]),
        ("churn_summary_by_tenure.csv", ["tenure_group"]),
        ("churn_summary_by_payment.csv", ["payment_group", "payment_method", "payment"]),
    ]
    for filename, candidates in summary_specs:
        column = find_column(df, candidates)
        if column:
            save_table(create_churn_summary(df, column), filename)
        else:
            warn(f"Skipped {filename}; no suitable segment column was found.")

    service_summary = create_service_summary(df)
    if service_summary is not None:
        save_table(service_summary, "churn_summary_by_service.csv")
    else:
        warn("Skipped churn_summary_by_service.csv; no service-related columns were found.")

    if "revenue_at_risk" in df.columns:
        save_table(create_revenue_risk_summary(df), "revenue_risk_summary.csv")
    else:
        warn("Skipped revenue_risk_summary.csv; revenue_at_risk was not found.")

    retention_curve = create_retention_curve(df)
    if retention_curve is not None:
        save_table(retention_curve, "retention_curve_table.csv")
    else:
        warn("Skipped retention_curve_table.csv; tenure and churn_flag are required.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
