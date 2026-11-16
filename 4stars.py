import streamlit as st
from PIL import Image
import requests
from ultralytics import YOLO
import io
import re

model = YOLO("yolov8n.pt")  


API_KEY = "33647b5804764c36b1634eb78a49e4f5"


FOOD_LABELS = {
    "banana", "apple", "orange", "broccoli", "carrot", "cake", "sandwich", "pizza",
    "hot dog", "donut", "cup", "bowl", "wine glass", "fork", "spoon", "knife", "carrot"
}


def detect_food_items(image):
    results = model(image)
    labels = results[0].names
    detected_items = set()

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = labels[cls_id]
        
        if any(food in label.lower() for food in FOOD_LABELS):
            detected_items.add(label.lower())

    return list(detected_items)


def clean_html(raw_html):
    return re.sub('<.*?>', '', raw_html)


def get_recipes(food_items):
    if not API_KEY:
        return [f"Mock recipe for {item}" for item in food_items]

    all_recipes = []
    seen_ids = set()

    for item in food_items:
        search_url = f"https://api.spoonacular.com/recipes/complexSearch?query={item}&number=2&apiKey={API_KEY}"
        search_response = requests.get(search_url)

        if search_response.status_code == 200:
            results = search_response.json().get("results", [])
            for result in results:
                recipe_id = result["id"]
                if recipe_id in seen_ids:
                    continue
                seen_ids.add(recipe_id)

                detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
                detail_response = requests.get(detail_url)

                if detail_response.status_code == 200:
                    detail = detail_response.json()
                    all_recipes.append({
                        "title": detail.get("title"),
                        "url": detail.get("sourceUrl"),
                        "summary": clean_html(detail.get("summary", "")),
                        "instructions": detail.get("instructions", "No instructions available.")
                    })

    return all_recipes

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

        with st.spinner("Fetching full recipe suggestions..."):
            recipes = get_recipes(detected_items)

        st.subheader("🍽 Suggested Recipes:")
        if recipes:
            for recipe in recipes:
                st.markdown(f"### [{recipe['title']}]({recipe['url']})")
                st.markdown(f"*Summary:* {recipe['summary']}")
                st.markdown(f"*Instructions:*\n\n{recipe['instructions']}")
                st.markdown("---")
        else:
            st.warning("No recipes found for detected items.")
    else:
        st.warning("No recognizable food items detected. Try another image.")
else:
    st.info("Upload a food or fridge image to get started.")