import os
import requests
import pandas as pd
import streamlit as st

# URL of the Flask backend. Inside the Docker network the backend is reachable by its container name.
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecaster", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecaster")
st.write("Predict the sales revenue of a product in a given store - for a single record or for a whole CSV file.")

tab_single, tab_batch = st.tabs(["Single prediction", "Batch prediction"])

# ------------------------------------------------------------------ single prediction
with tab_single:
    st.subheader("Enter product and store details")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Product**")
        product_weight = st.number_input("Product weight", min_value=0.0, value=12.66, step=0.1)
        sugar = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        allocated_area = st.number_input("Allocated display area (ratio)", min_value=0.0, max_value=1.0,
                                         value=0.027, step=0.001, format="%.3f")
        mrp = st.number_input("Product MRP", min_value=0.0, value=117.08, step=1.0)
        product_char = st.selectbox("Product family code (Product_Id prefix)", ["FD", "DR", "NC"])
        category = st.selectbox("Product category", ["Perishables", "Non Perishables"], index=1)

    with col2:
        st.markdown("**Store**")
        store_size = st.selectbox("Store size", ["Small", "Medium", "High"], index=1)
        city_type = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"], index=1)
        store_type = st.selectbox("Store type", ["Departmental Store", "Food Mart",
                                                 "Supermarket Type1", "Supermarket Type2"], index=3)
        store_age = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

    if st.button("Predict sales", type="primary"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": sugar,
            "Product_Allocated_Area": allocated_area,
            "Product_MRP": mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_char,
            "Store_Age_Years": store_age,
            "Product_Type_Category": category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                st.success(f"Predicted sales: {response.json()['Predicted_Sales']:,.2f}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend: {e}")

# ------------------------------------------------------------------ batch prediction
with tab_batch:
    st.subheader("Upload a CSV file")
    st.caption("Required columns: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, Product_MRP, "
               "Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, Store_Age_Years, "
               "Product_Type_Category")
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded is not None:
        batch_df = pd.read_csv(uploaded)
        st.write("Preview of the uploaded data")
        st.dataframe(batch_df.head())

        if st.button("Predict sales for the file"):
            try:
                files = {"file": ("batch.csv", batch_df.to_csv(index=False).encode("utf-8"), "text/csv")}
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=120)
                if response.status_code == 200:
                    preds = response.json()
                    result = batch_df.copy()
                    result["Predicted_Sales"] = [preds.get(str(i)) for i in result.index]
                    st.success(f"Generated {len(result)} predictions")
                    st.dataframe(result)
                    st.download_button("Download predictions as CSV",
                                       result.to_csv(index=False).encode("utf-8"),
                                       file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend: {e}")
