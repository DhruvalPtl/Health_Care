import tensorflow as tf
from tensorflow.keras.models import load_model, Model, model_from_json
import json

# Paths
model_path = "F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\model\\chest_xray\\chest_xray_model.h5"
fixed_model_path = "F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\model\\chest_xray\\fixed_chest_xray_model.h5"

# ✅ Load the model without compiling
try:
    model = load_model(model_path, compile=False)
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# ✅ Convert the model to JSON
model_json = model.to_json()

# ✅ Fix layer names in JSON
model_config = json.loads(model_json)
for layer in model_config["config"]["layers"]:
    if "/" in layer["config"]["name"]:
        old_name = layer["config"]["name"]
        new_name = old_name.replace("/", "_")
        layer["config"]["name"] = new_name
        print(f"🔄 Renamed layer: {old_name} -> {new_name}")

# ✅ Recreate model from modified JSON
new_model_json = json.dumps(model_config)
fixed_model = model_from_json(new_model_json)

# ✅ Transfer weights from old model
fixed_model.set_weights(model.get_weights())

# ✅ Save the fixed model
try:
    fixed_model.save(fixed_model_path)
    print(f"✅ Fixed model saved at: {fixed_model_path}")
except Exception as e:
    print(f"❌ Error saving fixed model: {e}")
