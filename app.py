from flask import Flask, request, jsonify
import joblib
import pandas as pd
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# Load only the Neural Network model
model = joblib.load("model/NeuralNet_pipeline.pkl")

tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype=torch.float32)
model.eval()
print("Phi-2 model loaded.")

@app.route("/api/ask", methods=["POST"])
def ask_ai():
    data = request.get_json()
    prompt = data.get("prompt", "")

    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=True,
            top_p=0.9,
            temperature=0.7
        )

    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return jsonify({"response": response}) 

# @app.route("/api/ask", methods=["POST"])
# def ask_ai():
#     data = request.get_json()
#     prompt = data.get("prompt", "")

#     inputs = tokenizer(prompt, return_tensors="pt")
#     outputs = model.generate(**inputs, max_new_tokens=200)
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     return jsonify({"response": response.strip()})

@app.route("/api/nutrition", methods=["POST"])
def get_nutrition():
    data = request.get_json()

    # Validate input
    required_fields = ["age", "height", "weight", "sex", "activity_level"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields in input"}), 400

    # Create input DataFrame for prediction
    input_df = pd.DataFrame([{
        "age": data["age"],
        "height": data["height"],
        "weight": data["weight"],
        "sex": data["sex"],
        "activity_level": data["activity_level"]
    }])

    # Predict using the Random Forest pipeline
    preds = model.predict(input_df)[0]  # Single prediction

    # Create a response dict
    response = {
        "calories": round(preds[0], 2),
        "protein": round(preds[1], 2),
        "fat": round(preds[2], 2),
        "carbs": round(preds[3], 2)
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

