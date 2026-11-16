import streamlit as st
import pandas as pd
from PIL import Image
import time

# Simulated AI model for ingredient detection (replace with actual model/API in production)
def detect_ingredients(image):
    # Placeholder: Simulate ingredient detection from image
    # In a real app, use a computer vision model (e.g., YOLO, Google Vision API)
    return [
        {"name": "Tomato", "quantity": 3, "unit": "pieces", "priority": "High (use soon)"},
        {"name": "Lettuce", "quantity": 1, "unit": "head", "priority": "Medium"},
        {"name": "Chicken Breast", "quantity": 2, "unit": "pieces", "priority": "High (use soon)"},
        {"name": "Onion", "quantity": 1, "unit": "piece", "priority": "Low"},
        {"name": "Cheese", "quantity": 200, "unit": "grams", "priority": "Medium"}
    ]

# Recipe database (simplified, can be replaced with an API like Edamam or Spoonacular)
recipe_db = {
    "Caprese Salad": {
        "ingredients": ["Tomato", "Cheese"],
        "recipe": "Slice tomatoes and cheese. Arrange on a plate, drizzle with olive oil, and sprinkle with salt and pepper.",
        "waste_reduction_tip": "Use tomatoes that are soft or slightly overripe for best flavor."
    },
    "Chicken Lettuce Wraps": {
        "ingredients": ["Chicken Breast", "Lettuce", "Onion"],
        "recipe": "Cook diced chicken breast with chopped onion. Serve in lettuce leaves as wraps.",
        "waste_reduction_tip": "Use wilting lettuce leaves; they’re still great for wraps."
    },
    "Chicken Salad": {
        "ingredients": ["Chicken Breast", "Lettuce", "Tomato"],
        "recipe": "Shred cooked chicken, chop lettuce and tomato, mix with dressing, and serve.",
        "waste_reduction_tip": "Use leftover chicken to avoid waste."
    }
}

# Function to suggest recipes based on detected ingredients
def suggest_recipes(ingredients):
    ingredient_names = [item["name"] for item in ingredients]
    suggestions = []
    
    for recipe_name, recipe_data in recipe_db.items():
        required_ingredients = recipe_data["ingredients"]
        if all(ing in ingredient_names for ing in required_ingredients):
            suggestions.append({
                "name": recipe_name,
                "ingredients": required_ingredients,
                "recipe": recipe_data["recipe"],
                "waste_reduction_tip": recipe_data["waste_reduction_tip"]
            })
    
    return suggestions

# Streamlit app layout
st.title("Fridge Scanner: AI Recipe Suggester")
st.write("Upload an image of your fridge, and get recipe suggestions to reduce food waste!")

# Image upload
uploaded_image = st.file_uploader("Choose an image of your fridge", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    # Display uploaded image
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Fridge Image", use_column_width=True)
    
    # Simulate AI processing
    with st.spinner("Scanning fridge contents..."):
        time.sleep(2)  # Simulate processing delay
        ingredients = detect_ingredients(image)
    
    # Display detected ingredients
    st.subheader("Detected Ingredients")
    ingredients_df = pd.DataFrame(ingredients)
    st.table(ingredients_df)
    
    # Suggest recipes
    st.subheader("Recipe Suggestions to Reduce Food Waste")
    recipes = suggest_recipes(ingredients)
    
    if recipes:
        for recipe in recipes:
            with st.expander(f"Recipe: {recipe['name']}"):
                st.write(f"*Required Ingredients*: {', '.join(recipe['ingredients'])}")
                st.write(f"*Instructions*: {recipe['recipe']}")
                st.write(f"*Waste Reduction Tip*: {recipe['waste_reduction_tip']}")
    else:
        st.warning("No recipes found with the detected ingredients. Try adding more items or check the image quality.")

# Footer
st.markdown("---")
st.write("Built with Streamlit. For a real app, integrate with a computer vision API and recipe database.")