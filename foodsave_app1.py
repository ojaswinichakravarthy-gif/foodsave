import streamlit as st
from PIL import Image
import requests
from ultralytics import YOLO
import io

# Load YOLOv8 model trained on food (or general object detection)
model = YOLO("yolov8n.pt")  # Replace with food-specific model if available

# Spoonacular API setup (optional for real recipe suggestions)
API_KEY = "your_spoonacular_api_key"

def detect_food_items(image):
    results = model(image)
    labels = results[0].names
    detected_items = set()

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = labels[cls_id]
        detected_items.add(label)

    return list(detected_items)

def get_recipes(food_items):
    if not API_KEY:
        return [f"Mock recipe for {item}" for item in food_items]

    all_recipes = []
    for item in food_items:
        url = f"https://api.spoonacular.com/recipes/complexSearch?query={item}&number=2&apiKey={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for recipe in data.get("results", []):
                all_recipes.append({
                    "title": recipe["title"],
                    "url": f'https://spoonacular.com/recipes/{recipe["title"].replace(" ", "-")}-{recipe["id"]}'
                })
    return all_recipes

# Streamlit UI
st.set_page_config(page_title="FoodSave AI", layout="centered")
st.title("🥦 FoodSave AI - Reduce Food Waste with Smart Recipes")

uploaded_file = st.file_uploader("Upload a photo of your food/fridge", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Detecting food items..."):
        detected_items = detect_food_items(image)

    if detected_items:
        st.success(f"Detected Food Items: {', '.join(detected_items)}")

        with st.spinner("Fetching recipe suggestions..."):
            recipes = get_recipes(detected_items)

        st.subheader("🍽️ Suggested Recipes:")
        for recipe in recipes:
            if isinstance(recipe, dict):
                st.markdown(f"[{recipe['title']}]({recipe['url']})")
            else:
                st.write(recipe)
    else:
        st.warning("No recognizable food items detected. Try another image.")
else:
    st.info("Upload a food or fridge image to get started.")

