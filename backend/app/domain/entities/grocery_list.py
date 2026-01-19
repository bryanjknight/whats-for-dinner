"""Grocery list domain entity.

This module contains the GroceryList and GroceryItem entities.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class GroceryItem:
    """A single item on a grocery list.

    Attributes:
        name: Ingredient name
        quantity: Total quantity needed
        unit: Measurement unit
        category: Grocery store category (e.g., "produce", "meat", "dairy")
        recipe_sources: List of recipe IDs that need this ingredient
        is_purchased: Whether this item has been purchased
        notes: Optional notes
    """

    name: str
    quantity: float
    unit: str
    category: str = "other"
    recipe_sources: list[str] = field(default_factory=list)
    is_purchased: bool = False
    notes: Optional[str] = None

    def add_quantity(self, additional_quantity: float) -> None:
        """Add to the quantity of this item.

        Args:
            additional_quantity: Amount to add
        """
        self.quantity += additional_quantity

    def mark_purchased(self) -> None:
        """Mark this item as purchased."""
        self.is_purchased = True

    def mark_unpurchased(self) -> None:
        """Mark this item as not purchased."""
        self.is_purchased = False


@dataclass
class GroceryList:
    """A consolidated grocery list for a meal plan.

    Attributes:
        id: Unique identifier
        meal_plan_id: ID of the associated meal plan
        items: List of grocery items
        created_at: When this list was created
        week_start_date: Start date of the week this list covers
    """

    id: str
    meal_plan_id: str
    items: list[GroceryItem] = field(default_factory=list)
    created_at: Optional[date] = None
    week_start_date: Optional[date] = None

    def add_item(self, item: GroceryItem) -> None:
        """Add an item to the grocery list.

        Args:
            item: GroceryItem to add
        """
        self.items.append(item)

    def consolidate_item(self, name: str, quantity: float, unit: str, recipe_id: str) -> None:
        """Add or consolidate an ingredient into the grocery list.

        If an item with the same name and unit exists, add to its quantity.
        Otherwise, create a new item.

        Args:
            name: Ingredient name
            quantity: Quantity to add
            unit: Measurement unit
            recipe_id: Source recipe ID
        """
        name_lower = name.lower()

        # Look for existing item with same name and unit
        for item in self.items:
            if item.name.lower() == name_lower and item.unit == unit:
                item.add_quantity(quantity)
                if recipe_id not in item.recipe_sources:
                    item.recipe_sources.append(recipe_id)
                return

        # Create new item if not found
        new_item = GroceryItem(
            name=name, quantity=quantity, unit=unit, recipe_sources=[recipe_id]
        )
        self.add_item(new_item)

    def get_items_by_category(self, category: str) -> list[GroceryItem]:
        """Get all items in a specific category.

        Args:
            category: Category to filter by

        Returns:
            List of items in that category
        """
        return [item for item in self.items if item.category.lower() == category.lower()]

    def get_all_categories(self) -> list[str]:
        """Get all unique categories in this list.

        Returns:
            List of unique category names
        """
        categories = {item.category for item in self.items}
        return sorted(categories)

    def get_unpurchased_items(self) -> list[GroceryItem]:
        """Get all items that haven't been purchased yet.

        Returns:
            List of unpurchased items
        """
        return [item for item in self.items if not item.is_purchased]

    def mark_item_purchased(self, item_name: str) -> bool:
        """Mark an item as purchased by name.

        Args:
            item_name: Name of the item to mark (case-insensitive)

        Returns:
            True if item was found and marked, False otherwise
        """
        item_name_lower = item_name.lower()
        for item in self.items:
            if item.name.lower() == item_name_lower:
                item.mark_purchased()
                return True
        return False

    @property
    def total_items(self) -> int:
        """Get total number of items.

        Returns:
            Total item count
        """
        return len(self.items)

    @property
    def purchased_count(self) -> int:
        """Get count of purchased items.

        Returns:
            Number of items marked as purchased
        """
        return sum(1 for item in self.items if item.is_purchased)

    @property
    def completion_percentage(self) -> float:
        """Calculate shopping completion percentage.

        Returns:
            Percentage of items purchased (0-100)
        """
        if self.total_items == 0:
            return 0.0
        return (self.purchased_count / self.total_items) * 100
