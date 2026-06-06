"""Clean a schema-flexible telecom churn CSV for analysis and Power BI."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from utils import ensure_directory, find_column, print_section, safe_numeric, standardize_column_names


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "cleaned_customers.csv"

NUMERIC_CANDIDATES = {
    "tenure": ["tenure", "tenure_months", "tenure_in_months", "months_with_company"],
    "monthly_charge": ["monthly_charges", "monthly_charge", "monthly_fee", "monthly_revenue"],
    "total_charge": ["total_charges", "total_charge", "total_revenue"],
    "cltv": ["cltv", "customer_lifetime_value", "customer_lifetime_value_cltv"],
}


def warn(message: str) -> None:
    print(f"WARNING: {message}")


def select_raw_csv(raw_dir: Path) -> tuple[Path, pd.DataFrame]:
    """Load the only CSV, or choose the CSV with the largest row count."""
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    if len(csv_files) == 1:
        selected = csv_files[0]
        print(f"One CSV found; loading: {selected.name}")
        return selected, pd.read_csv(selected, low_memory=False)

    print("Multiple CSV files found:")
    candidates: list[tuple[Path, pd.DataFrame]] = []
    for path in csv_files:
        try:
            frame = pd.read_csv(path, low_memory=False)
            candidates.append((path, frame))
            print(f"  - {path.name}: {len(frame):,} rows")
        except Exception as exc:
            warn(f"Could not read {path.name}: {exc}")

    if not candidates:
        raise ValueError("CSV files were found, but none could be loaded.")

    selected, frame = max(candidates, key=lambda item: len(item[1]))
    print(f"Choosing {selected.name} because it has the largest row count.")
    return selected, frame


def trim_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].astype("string").str.strip()
        result[column] = result[column].replace({"": pd.NA})
    return result


def convert_likely_numeric_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    result = df.copy()
    found: dict[str, str] = {}
    for role, candidates in NUMERIC_CANDIDATES.items():
        column = find_column(result, candidates)
        if column:
            result[column] = safe_numeric(result[column])
            found[role] = column
        else:
            warn(f"No optional {role.replace('_', ' ')} column found.")
    return result, found


def create_churn_flag(df: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    result = df.copy()
    source = find_column(result, ["churn", "churn_status", "customer_status", "status", "churn_value"])
    if not source:
        warn("No churn or customer status column found; churn_flag was not created.")
        return result, None

    normalized = result[source].astype("string").str.strip().str.lower()
    churned_values = {"yes", "y", "churned", "churn", "1", "true"}
    retained_values = {"no", "n", "stayed", "joined", "retained", "active", "0", "false"}

    result["churn_flag"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    result.loc[normalized.isin(churned_values), "churn_flag"] = 1
    result.loc[normalized.isin(retained_values), "churn_flag"] = 0

    unresolved = int(result["churn_flag"].isna().sum())
    if unresolved:
        warn(f"Could not map {unresolved:,} values from '{source}' to churn_flag.")
    return result, source


def safe_quantile_band(series: pd.Series, labels: list[str]) -> pd.Series:
    """Create quantile bands without failing on small or low-variance datasets."""
    numeric = safe_numeric(series)
    valid = numeric.dropna()
    if valid.empty:
        return pd.Series(pd.NA, index=series.index, dtype="string")
    try:
        ranked = numeric.rank(method="first")
        return pd.qcut(ranked, q=len(labels), labels=labels).astype("string")
    except ValueError:
        return pd.Series("Unclassified", index=series.index, dtype="string")


def create_derived_columns(df: pd.DataFrame, numeric_columns: dict[str, str]) -> pd.DataFrame:
    result = df.copy()
    tenure = numeric_columns.get("tenure")
    monthly = numeric_columns.get("monthly_charge")
    total = numeric_columns.get("total_charge")
    cltv = numeric_columns.get("cltv")

    if tenure:
        result["tenure_group"] = pd.cut(
            result[tenure],
            bins=[-np.inf, 6, 12, 24, 48, 60, np.inf],
            labels=["0-6 months", "7-12 months", "13-24 months", "25-48 months", "49-60 months", "61+ months"],
        ).astype("string")

    if monthly:
        result["monthly_charge_band"] = safe_quantile_band(
            result[monthly], ["Low", "Lower Mid", "Upper Mid", "High"]
        )

    if total:
        result["total_charge_band"] = safe_quantile_band(
            result[total], ["Low", "Lower Mid", "Upper Mid", "High"]
        )

    value_source = cltv or total or monthly
    if value_source:
        result["customer_value_segment"] = safe_quantile_band(
            result[value_source], ["Low Value", "Medium Value", "High Value"]
        )
    else:
        warn("No value column found; customer_value_segment was not created.")

    if monthly and "churn_flag" in result.columns:
        result["revenue_at_risk"] = result[monthly].where(result["churn_flag"].eq(1), 0).fillna(0)
    else:
        warn("Monthly charge and churn_flag are required to create revenue_at_risk.")

    contract = find_column(result, ["contract", "contract_type", "customer_contract"])
    if contract:
        result["contract_group"] = result[contract].astype("string").fillna("Unknown")
    else:
        warn("No contract column found; contract_group was not created.")

    payment = find_column(result, ["payment_method", "payment", "billing_method"])
    if payment:
        result["payment_group"] = result[payment].astype("string").fillna("Unknown")
    else:
        warn("No payment method column found; payment_group was not created.")

    return result


def main() -> int:
    print_section("Telecom Churn Data Cleaning")
    ensure_directory(RAW_DIR)
    ensure_directory(PROCESSED_DIR)

    try:
        source_path, raw_df = select_raw_csv(RAW_DIR)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        print("Add a telecom churn CSV to data/raw/ and run this script again.")
        return 1

    print(f"Loaded file path: {source_path}")
    print(f"Original shape: {raw_df.shape}")

    cleaned = standardize_column_names(raw_df)
    cleaned = trim_string_columns(cleaned)
    cleaned, numeric_columns = convert_likely_numeric_columns(cleaned)
    cleaned, _ = create_churn_flag(cleaned)
    cleaned = create_derived_columns(cleaned, numeric_columns)
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    cleaned.to_csv(OUTPUT_PATH, index=False)

    print_section("Cleaning Summary")
    print(f"Cleaned shape: {cleaned.shape}")
    print(f"Columns ({len(cleaned.columns)}): {', '.join(cleaned.columns)}")
    print("\nMissing value summary:")
    missing = cleaned.isna().sum()
    missing = missing[missing.gt(0)].sort_values(ascending=False)
    print(missing.to_string() if not missing.empty else "No missing values found.")
    print(f"\nOutput path: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
