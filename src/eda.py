import pandas as pd
import matplotlib.pyplot as plt


def basic_info(df_raw: pd.DataFrame) -> dict:
    return {
        "shape": df_raw.shape,
        "columns": df_raw.columns.tolist(),
        "missing": df_raw.isna().sum().sort_values(ascending=False),
        "dtypes": df_raw.dtypes.astype(str),
        "duplicates": int(df_raw.duplicated().sum()),
    }


def numeric_summary(df_raw: pd.DataFrame) -> pd.DataFrame:
    num_df_raw = df_raw[["quantity", "price_per_unit", "base_price"]]
    if num_df_raw.empty:
        return pd.DataFrame()
    return num_df_raw.describe().T


def categorical_summary(df_raw: pd.DataFrame, top_n: int = 10) -> dict:
    result = {}
    cat_cols = df_raw.select_dtypes(include="object").columns
    for col in cat_cols:
        vc = df_raw[col].value_counts(dropna=False).head(top_n)
        result[col] = vc
    return result


def plot_missing_values(df_raw: pd.DataFrame):
    missing = df_raw.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]

    fig, ax = plt.subplots(figsize=(4, 0.6))
    if missing.empty:
        ax.text(0.5, 0.5, "Нет пропусков", ha="center", va="center", fontsize=8)
        ax.axis("off")
        fig.tight_layout(pad=0)
    else:
        ax.bar(missing.index.astype(str), missing.values)
        ax.set_title("Количество пропусков по столбцам")
        ax.set_ylabel("Пропуски")
        ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def plot_numeric_distributions(df_raw: pd.DataFrame, max_cols: int = 4):
    num_cols =  ["quantity", "price_per_unit", "base_price"]
    figs = []

    for col in num_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(df_raw[col].dropna(), bins=20)
        ax.set_title(f"Распределение: {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Частота")
        fig.tight_layout()
        figs.append((col, fig))

    return figs


def plot_correlation(df_raw: pd.DataFrame):
    num_df_raw = df_raw[["quantity", "price_per_unit", "base_price"]]
    if num_df_raw.shape[1] < 2:
        return None

    corr = num_df_raw.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.imshow(corr, aspect="auto")
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    fig.colorbar(cax, ax=ax)
    ax.set_title("Корреляция числовых признаков")
    fig.tight_layout()
    return fig


def top_categories(df_raw: pd.DataFrame, col: str, top_n: int = 10) -> pd.Series:
    if col not in df_raw.columns:
        return pd.Series(dtype="int64")
    return df_raw[col].value_counts(dropna=False).head(top_n)
