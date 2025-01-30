from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories'
    )

    def __str__(self):
        return self.name if not self.parent else f"{self.parent.name} > {self.name}"
    
class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name 
    
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.name

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link items to users
    name = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ManyToManyField(Color)        # multiple colors per item
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True) 
    price = models.FloatField(null=True, blank=True)
    wear_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)

    def cost_per_wear(self):
        return self.price / self.wear_count if self.wear_count > 0 else 0
    
    def __str__(self):
        return self.name if self.name else "Unnamed Item"
    
class WornItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate logs with a user
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="worn_logs")
    date = models.DateField()  # The date the item was worn