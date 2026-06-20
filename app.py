import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date

# ---------------- DATABASE ----------------

conn = sqlite3.connect("expense_tracker.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    exp_date TEXT,
    category TEXT,
    amount REAL,
    description TEXT
)
""")

conn.commit()

# ---------------- FUNCTIONS ----------------

def create_user(username, password):
    try:
        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return c.fetchone()

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Expense Tracker Pro",
    page_icon="💰",
    layout="wide"
)

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN / SIGNUP ----------------

if not st.session_state.logged_in:

    st.title("💰 Expense Tracker Pro")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    with tab2:
        st.subheader("Create Account")

        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if create_user(new_user, new_pass):
                st.success("Account Created Successfully")
            else:
                st.error("Username already exists")

    st.stop()

# ---------------- SIDEBAR ----------------

st.sidebar.title("💰 Expense Tracker")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Expense",
        "Reports",
        "Video Tutorial"
    ]
)

st.sidebar.success(
    f"Logged in as {st.session_state.username}"
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- ADD EXPENSE ----------------

if menu == "Add Expense":

    st.header("➕ Add Expense")

    with st.form("expense_form"):

        exp_date = st.date_input(
            "Date",
            date.today()
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Shopping",
                "Bills",
                "Entertainment",
                "Education",
                "Health",
                "Other"
            ]
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0
        )

        description = st.text_input(
            "Description"
        )

        submit = st.form_submit_button(
            "Save Expense"
        )

        if submit:

            c.execute("""
            INSERT INTO expenses
            (username,exp_date,category,amount,description)
            VALUES(?,?,?,?,?)
            """,
            (
                st.session_state.username,
                str(exp_date),
                category,
                amount,
                description
            ))

            conn.commit()

            st.success("Expense Added Successfully!")

# ---------------- DASHBOARD ----------------

elif menu == "Dashboard":

    st.header("📊 Dashboard")

    df = pd.read_sql_query(
        """
        SELECT * FROM expenses
        WHERE username=?
        """,
        conn,
        params=(st.session_state.username,)
    )

    if df.empty:
        st.info("No expenses added yet.")
    else:

        total_expense = df["amount"].sum()
        average_expense = df["amount"].mean()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Expense",
                f"₹{total_expense:.2f}"
            )

        with col2:
            st.metric(
                "Average Expense",
                f"₹{average_expense:.2f}"
            )

        st.subheader("💵 Monthly Budget")

        budget = st.number_input(
            "Enter Monthly Budget",
            value=10000.0
        )

        remaining = budget - total_expense

        st.metric(
            "Remaining Budget",
            f"₹{remaining:.2f}"
        )

        if remaining < 0:
            st.error("⚠ Budget Exceeded")
        else:
            st.success("✅ Within Budget")

        st.subheader("Expense Records")
        st.dataframe(df, use_container_width=True)

        st.subheader("Category Wise Expenses")

        category_df = (
            df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            category_df,
            names="category",
            values="amount",
            title="Expense Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Bar Chart")

        st.bar_chart(
            category_df.set_index("category")
        )

        st.subheader("Expense Trend")

        trend = (
            df.groupby("exp_date")["amount"]
            .sum()
        )

        st.line_chart(trend)

# ---------------- REPORTS ----------------

elif menu == "Reports":

    st.header("📑 Reports")

    df = pd.read_sql_query(
        """
        SELECT * FROM expenses
        WHERE username=?
        """,
        conn,
        params=(st.session_state.username,)
    )

    st.dataframe(df, use_container_width=True)

    if not df.empty:

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            csv,
            "expenses.csv",
            "text/csv"
        )

# ---------------- VIDEO ----------------

elif menu == "Video Tutorial":

    st.header("🎥 Financial Education")

    st.video(
        "https://www.youtube.com/watch?v=VqgUkExPvLY"
    )

    st.info(
        "Watch this video to learn money management and budgeting."
    )