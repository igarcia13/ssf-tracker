import streamlit as st
import pandas as pd
import plotly.express as px
import io
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np

# Set the title of the dashboard
st.title("📊 Student Support Services Dashboard")

# File uploader for Excel files
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    # Read the "Student Supports" sheet
    sheet_name = "Student Supports"
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

    # Display dataset preview
    st.subheader(f"Dataset Preview - {sheet_name}")
    st.write(df.head())

    # Convert date column
    df["Entry Date"] = pd.to_datetime(df["Entry Date"], errors="coerce")

    # **FILTER OPTIONS**
    filters = {
        "Home School": "Filter by School",
        "Grade Level": "Filter by Grade",
        "Case Manager": "Filter by Case Manager",
        "Student Support Name": "Filter by Support Type"
    }

    for col, label in filters.items():
        if col in df.columns:
            unique_values = df[col].dropna().unique()
            selected_value = st.selectbox(f"{label} (optional)", ["All"] + list(unique_values))
            if selected_value != "All":
                df = df[df[col] == selected_value]

    # **Summarize Services Provided**
    st.subheader("📊 Summary of Services Provided")

    if "Student Support Name" in df.columns and "Hours" in df.columns:
        summary = df.groupby("Student Support Name")["Hours"].sum().reset_index()
        summary.columns = ["Support Type", "Total Hours Provided"]
        st.write(summary)

        # Bar Chart of Services
        fig_service = px.bar(summary, x="Support Type", y="Total Hours Provided",
                             title="Total Hours of Support by Type", labels={"Total Hours Provided": "Hours"})
        st.plotly_chart(fig_service)

    # **Trends Over Time**
    if "Entry Date" in df.columns:
        df["Month"] = df["Entry Date"].dt.to_period("M").astype(str)
        trend_summary = df.groupby("Month")["Hours"].sum().reset_index()
        trend_summary.columns = ["Month", "Total Hours Provided"]

        st.subheader("📈 Service Hours Over Time")
        fig_trend = px.line(trend_summary, x="Month", y="Total Hours Provided",
                            title="Service Hours Trends Over Time")
        st.plotly_chart(fig_trend)

    # **Predict Future Service Needs**
    st.subheader("🔮 Predict Future Service Needs")
    
    if "Entry Date" in df.columns and len(trend_summary) > 2:
        trend_summary["Numeric Month"] = range(len(trend_summary))

        # Prepare ML Model
        X = trend_summary[["Numeric Month"]]
        y = trend_summary["Total Hours Provided"]

        # Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Show Model Accuracy
        accuracy = model.score(X_test, y_test)
        st.write(f"Model Accuracy: **{accuracy:.2f}**")

        # Predict Future Hours
        future_months = st.number_input("Predict support hours for how many future months?", min_value=1, max_value=12, step=1)
        future_numeric = np.array([len(trend_summary) + future_months]).reshape(-1, 1)
        future_prediction = model.predict(future_numeric)[0]

        st.write(f"Predicted Total Service Hours in {future_months} months: **{int(future_prediction)}**")

        # Show Predicted Trend Line
        trend_summary["Predicted"] = model.predict(X)
        fig_pred = px.line(trend_summary, x="Month", y=["Total Hours Provided", "Predicted"],
                           title="Actual vs Predicted Service Hours")
        st.plotly_chart(fig_pred)

    else:
        st.warning("Not enough data to make predictions. Upload a file with at least 3 months of data.")

    # **Download Custom Reports**
    st.subheader("💾 Download Filtered Data")
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    st.download_button("Download CSV", buffer.getvalue(), "filtered_student_services.csv", "text/csv")


