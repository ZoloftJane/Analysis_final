import matplotlib.pyplot as plt
import pandas as pd

def plot_top_items(df: pd.DataFrame):
    top_items = df.groupby("item_name", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_items["item_name"].astype(str)[::-1], top_items["revenue"][::-1])
    ax.set_title("Топ-10 товаров по выручке")
    ax.set_xlabel("Выручка")
    return fig

def plot_category_revenue(df: pd.DataFrame):
    cat_rev = df.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(cat_rev["revenue"].head(8), labels=cat_rev["category"].head(8), autopct="%1.1f%%")
    ax.set_title("Выручка по категориям товаров")
    return fig

def plot_weekday_orders(df: pd.DataFrame):
    tmp = df.copy()
    tmp["weekday"] = tmp["order_date"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wd = tmp.groupby("weekday").size().reindex(order).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(wd.index, wd.values, marker="o")
    ax.set_title("Количество заказов по дням недели")
    ax.set_ylabel("Заказы")
    ax.tick_params(axis="x", rotation=30)
    return fig