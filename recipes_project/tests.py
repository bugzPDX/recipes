from django.test import TestCase
from recipes.models import RecipeIngredient
from recipes.models import Unit
from recipes.models import Ingredient

class RecipeIngredientTestCase(TestCase):
    def setUp(self):
        self.unit = Unit.objects.create(name="cups")
        self.ingredient = Ingredient.objects.create(name="bananas")

    def test_unicode_no_units(self):
        """Tests how recipe ingredients stringify without units"""
        ri = RecipeIngredient.objects.create(recipe_id=1, quantity=3, ingredient=self.ingredient)
        self.assertEqual("%s" % ri, "3 bananas")

    def test_unicode_with_units(self):
        """Tests how recipe ingredients stringify with units"""
        ri = RecipeIngredient.objects.create(recipe_id=1, unit=self.unit, quantity=19, ingredient=self.ingredient)
        self.assertEqual("%s" % ri, "19 cups bananas")
