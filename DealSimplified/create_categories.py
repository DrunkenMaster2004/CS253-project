import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DealSimplified.settings')
django.setup()

from LostNFound.models import LostFoundCategory
from marketplace.models import ItemCategory

# Define category list (common for both Lost & Found and Marketplace)
categories = [
    {"name": "Electronics", "description": "Phones, laptops, headphones, etc."},
    {"name": "Books", "description": "Textbooks, notebooks, etc."},
    {"name": "Clothing", "description": "Jackets, hats, scarves, etc."},
    {"name": "Accessories", "description": "Jewelry, watches, glasses, etc."},
    {"name": "ID/Cards", "description": "ID cards, credit cards, etc."},
    {"name": "Keys", "description": "House keys, car keys, etc."},
    {"name": "Other", "description": "Miscellaneous items"}
]

# Create categories in LostFoundCategory
for category in categories:
    LostFoundCategory.objects.get_or_create(
        name=category["name"],
        defaults={"description": category["description"]}
    )

# Create categories in ItemCategory
for category in categories:
    ItemCategory.objects.get_or_create(
        name=category["name"],
        defaults={"description": category["description"]}
    )

print(f"Created {len(categories)} categories in LostFoundCategory and ItemCategory.")
