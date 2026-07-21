import streamlit as st
import pandas as pd

from src.data_loader import load_data
from src.data_processing import merge_data, prepare_data, calculate_kpis
from src.visualizations import plot_top_items, plot_category_revenue, plot_weekday_orders
from src.eda import (
    basic_info,
    numeric_summary,
    categorical_summary,
    plot_missing_values,
    plot_numeric_distributions,
    plot_correlation,
    )

st.set_page_config(page_title="Аналитический дашборд", layout="wide")
st.title("Аналитический дашборд интернет-магазина")
st.write("Интерактивное приложение для анализа заказов, пользователей и товаров")

orders, users, items = load_data()
df_raw = merge_data(orders, users, items)

tab_eda, tab_raw, tab_kpi, tab_viz, tab_conc = st.tabs([
    "EDA",
    "Сырые данные",
    "Ключевые показатели",
    "Визуализация",
    "Аналитические выводы"
])

with tab_eda:
    st.subheader("Общая информация")
    info = basic_info(df_raw)
    col1, col2, col3 = st.columns(3)
    col1.metric("Строки", info["shape"][0])
    col2.metric("Столбцы", info["shape"][1])
    col3.metric("Дубликаты", info["duplicates"])

    st.write("### Типы данных")
    st.dataframe(info["dtypes"].to_frame("dtype"), use_container_width=True)

    st.write("### Пропуски")
    st.dataframe(info["missing"].to_frame("missing"), use_container_width=True)
    st.pyplot(plot_missing_values(df_raw))

    st.write("### Числовые признаки")
    num_sum = numeric_summary(df_raw)
    if not num_sum.empty:
        st.dataframe(num_sum, use_container_width=True)
        for col_name, fig in plot_numeric_distributions(df_raw):
            st.pyplot(fig)
    else:
        st.write("Числовых столбцов нет.")

    st.write("### Категориальные признаки")
    cat_sum = categorical_summary(df_raw)
    if cat_sum:
        for col_name, series in cat_sum.items():
            st.write(f"**{col_name}**")
            st.dataframe(series.to_frame("count"), use_container_width=True)
    else:
        st.write("Категориальных столбцов нет.")

    st.write("### Корреляция")
    corr_fig = plot_correlation(df_raw)
    if corr_fig is not None:
        st.pyplot(corr_fig)
    else:
        st.write("Недостаточно числовых столбцов для корреляции.")

df = prepare_data(df_raw)

with tab_raw:
    st.header("Сырые данные")

    cols = st.columns(2)
    selected_category = None

    if "category" in df.columns:
        cats = ["All"] + sorted(df["category"].dropna().astype(str).unique().tolist())
        selected_category = cols[0].selectbox("Категория", cats)

    if "order_date" in df.columns and df["order_date"].notna().any():
        min_date = df["order_date"].min().date()
        max_date = df["order_date"].max().date()
        date_range = cols[1].date_input("Период", value=(min_date, max_date))
    else:
        date_range = None

    df_copy = df.copy()

    if selected_category and selected_category != "All":
        df_copy = df_copy[df_copy["category"].astype(str) == selected_category]

    if date_range and isinstance(date_range, tuple) and len(date_range) == 2 and "order_date" in df_copy.columns:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_copy = df_copy[(df_copy["order_date"] >= start) & (df_copy["order_date"] <= end)]

    st.dataframe(df_copy, use_container_width=True)

with tab_kpi:
    st.header("Ключевые показатели")
    kpis = calculate_kpis(df_copy)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Общее количество заказов", f"{kpis['orders_count']}")
    m2.metric("Общая выручка", f"{kpis['revenue']:,.2f}")
    m3.metric("Уникальные пользователи", f"{kpis['unique_users']}")
    m4.metric("Средний чек", f"{kpis['avg_check']:,.2f}")

with tab_viz:
    st.header("Визуализация")
    if "item_name" in df_copy.columns and "revenue" in df_copy.columns:
        st.pyplot(plot_top_items(df_copy))

    if "category" in df_copy.columns and "revenue" in df_copy.columns:
        st.pyplot(plot_category_revenue(df_copy))

    if "order_date" in df_copy.columns:
        st.pyplot(plot_weekday_orders(df_copy))

with tab_conc:
    st.header("Аналитические выводы")
    conclusions = []

    if "category" in df_copy.columns and not df_copy.empty and "revenue" in df_copy.columns:
        top_cat = df_copy.groupby("category")["revenue"].sum().sort_values(ascending=False).index[0]
        conclusions.append(f"Основная выручка приходится на категорию {top_cat}.")

    if "item_name" in df_copy.columns and not df_copy.empty and "revenue" in df_copy.columns:
        top_item = df_copy.groupby("item_name")["revenue"].sum().sort_values(ascending=False).index[0]
        conclusions.append(f"Товар {top_item} является лидером продаж.")

    if "order_date" in df_copy.columns and not df_copy.empty:
        peak_day = (
            df_copy.assign(weekday=df_copy["order_date"].dt.day_name())
            .groupby("weekday")
            .size()
            .sort_values(ascending=False)
            .index[0]
        )
        conclusions.append(f"Пик заказов наблюдается в день недели {peak_day}.")

    if conclusions:
        st.markdown("\n".join([f"- {x}" for x in conclusions]))
    else:
        st.write("Недостаточно данных для автоматических выводов.")