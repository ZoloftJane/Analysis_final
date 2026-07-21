import pandas as pd


def merge_data(orders: pd.DataFrame, users: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    
    df_raw = orders.merge(users, on="user_id", how="left")
    df_raw = df_raw.merge(items, on="item_id", how="left")

    return df_raw

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:

    for col in ["order_date", "registration_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["quantity", "price_per_unit", "base_price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["revenue"] = df["quantity"].fillna(0) * df["price_per_unit"].fillna(0)
    
    return df


def calculate_kpis(df: pd.DataFrame) -> dict:
    orders_count = df["order_id"].nunique()
    revenue = float(df["revenue"].fillna(0).sum())
    unique_users = df["user_id"].nunique()
    avg_check = revenue / orders_count

    return {
        "orders_count": orders_count,
        "revenue": revenue,
        "unique_users": unique_users,
        "avg_check": avg_check,
    }