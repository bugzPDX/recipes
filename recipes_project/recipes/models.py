from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# Keep this as category and it only really needs a name
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name


# Call this model Recipe and give it fields for directions, 
# page source, notes, etc..
class Recipe(models.Model):
    category = models.ForeignKey(Category, help_text="Choose a Category")
    title = models.CharField(max_length=128, help_text="Please enter the title of the recipe.")
    url = models.URLField(help_text="Please enter the URL of the recipe.")
    directions = models.TextField(help_text="Please enter the recipe directions.")
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

class Ingredient(models.Model):
    name = models.CharField(max_length=128,unique=True, help_text="Enter an Ingredient")

    def __unicode__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=32, blank=True)

    def __unicode__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients")
    quantity = models.FloatField(default=0.0)
    unit = models.ForeignKey(Unit, blank=True, null=True)
    ingredient = models.ForeignKey(Ingredient)


    def __unicode__(self):
        if not self.unit:
            return "%g %s" % (self.quantity, self.ingredient)
        else:
            return "%g %s %s" % (self.quantity, self.unit, self.ingredient)

# Modify this model to be Ingredients. It should contain,
# fields for quantity, units and name (ex. sugar, salt, water..)
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaninful!
    def __unicode__(self):
        return self.user.username
