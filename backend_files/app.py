# Importing necessary libraries
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialising the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Loading the trained pipeline (preprocessing + regressor)
model = joblib.load("superkart_model.joblib")

# Features expected by the model
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]


# Home endpoint
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API!"


# Online (single record) prediction
@superkart_api.post("/v1/predict")
def predict_sales():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Send the input features as a JSON body."}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    try:
        input_df = pd.DataFrame([{f: data[f] for f in FEATURES}])
        prediction = float(model.predict(input_df)[0])
        return jsonify({"Predicted_Sales": round(prediction, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Batch prediction from an uploaded CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file with the key 'file'."}), 400

    try:
        input_df = pd.read_csv(request.files["file"])
        missing = [f for f in FEATURES if f not in input_df.columns]
        if missing:
            return jsonify({"error": f"Missing columns: {missing}"}), 400

        predictions = model.predict(input_df[FEATURES])
        # keys = row index of the uploaded file, values = predicted sales
        return jsonify({str(i): round(float(p), 2) for i, p in zip(input_df.index, predictions)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
