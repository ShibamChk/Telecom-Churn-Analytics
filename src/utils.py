"""Shared helpers for schema-flexible telecom churn data preparation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with lowercase snake_case column names."""
    result = df.copy()
    cleaned_columns: list[str] = []
    seen: dict[str, int] = {}

    for column in result.columns:
        name = str(column).strip().lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_") or "unnamed_column"

        count = seen.get(name, 0)
        seen[name] = count + 1
        cleaned_columns.append(name if count == 0 else f"{name}_{count + 1}")

    result.columns = cleaned_columns
    return result


def find_column(df: pd.DataFrame, possible_names: Iterable[str]) -> str | None:
    """Find the first existing column from a list of common name variations."""
    lookup = {str(column).strip().lower(): column for column in df.columns}
    for name in possible_names:
        normalized = str(name).strip().lower()
        if normalized in lookup:
            return str(lookup[normalized])
    return None


def ensure_directory(path: str | Path) -> Path:
    """Create a directory when missing and return it as a Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def print_section(title: str) -> None:
    """Print a clean console section header."""
    border = "=" * max(len(title), 12)
    print(f"\n{border}\n{title}\n{border}")


def safe_numeric(series: pd.Series) -> pd.Series:
    """Convert numeric-like strings, currency values, and blanks to numbers."""
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(r"[$,%]", "", regex=True)
    cleaned = cleaned.str.replace(",", "", regex=False)
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "none": pd.NA, "null": pd.NA})
    return pd.to_numeric(cleaned, errors="coerce")
