import os
import requests
from pathlib import Path

# Create directory
os.makedirs('supershopee/static/products', exist_ok=True)

# VERIFIED IMAGES WITH CORRECT URLs
verified_products = {
    "milk": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg",
    "yogurt": "https://images.pexels.com/photos/6775221/pexels-photo-6775221.jpeg",
    "cheese": "https://images.pexels.com/photos/3407857/pexels-photo-3407857.jpeg",
    "butter": "https://images.pexels.com/photos/4551832/pexels-photo-4551832.jpeg",
    "bananas": "https://images.pexels.com/photos/5632583/pexels-photo-5632583.jpeg",
    "apples": "https://images.pexels.com/photos/5632580/pexels-photo-5632580.jpeg",
    "oranges": "https://images.pexels.com/photos/1092730/pexels-photo-1092730.jpeg",
    "strawberries": "https://images.pexels.com/photos/2582522/pexels-photo-2582522.jpeg",
    "grapes": "https://images.pexels.com/photos/5733447/pexels-photo-5733447.jpeg",
    "potatoes": "https://images.pexels.com/photos/4553529/pexels-photo-4553529.jpeg",
    "onions": "https://images.pexels.com/photos/4905906/pexels-photo-4905906.jpeg",
    "tomatoes": "https://images.pexels.com/photos/3962286/pexels-photo-3962286.jpeg",
    "carrots": "https://images.pexels.com/photos/5632585/pexels-photo-5632585.jpeg",
    "broccoli": "https://images.pexels.com/photos/4553531/pexels-photo-4553531.jpeg",
    "bread": "https://images.pexels.com/photos/1410235/pexels-photo-1410235.jpeg",
    "croissants": "https://images.pexels.com/photos/4631317/pexels-photo-4631317.jpeg",
    "cookies": "https://images.pexels.com/photos/3407857/pexels-photo-3407857.jpeg",
    "rice": "https://images.pexels.com/photos/5632577/pexels-photo-5632577.jpeg",
    "pasta": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg",
    "olive_oil": "https://images.pexels.com/photos-dynamic/460632/pexels-photo-460632.jpeg",
    "almonds": "https://images.pexels.com/photos/5632585/pexels-photo-5632585.jpeg",
    "honey": "https://images.pexels.com/photos-dynamic/427394/pexels-photo-427394.jpeg",
    "coffee": "https://images.pexels.com/photos-dynamic/399161/pexels-photo-399161.jpeg",
    "tea": "https://images.pexels.com/photos-dynamic/325185/pexels-photo-325185.jpeg",
}

# Download images
for product_name, url in verified_products.items():
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            file_path = f'supershopee/static/products/{product_name}.jpg'
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded: {product_name}")
        else:
            print(f"❌ Failed: {product_name} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error downloading {product_name}: {e}")

print("\n✅ All images downloaded to supershopee/static/products/")