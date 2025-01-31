from django.contrib.auth.models import User
from django.db import models
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage

import os, boto3
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings


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
    image = models.ImageField(storage=S3Boto3Storage(), upload_to="media/item_images/", blank=True, null=True)

    def delete(self, *args, **kwargs):
        """
        Delete the image from S3 when the item is deleted.
        """
        if self.image:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.image.name)
        super().delete(*args, **kwargs)

    @receiver(pre_save, sender="myapp.Item")
    def delete_old_image(sender, instance, **kwargs):
        """
        Deletes the old image from S3 before saving the new one.
        """
        if not instance.pk:
            return  # No previous instance, means it's a new item

        try:
            old_instance = Item.objects.get(pk=instance.pk)
            if old_instance.image and old_instance.image != instance.image:
                s3 = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME,
                )
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=old_instance.image.name)
        except Item.DoesNotExist:
            pass  # The item didn't exist before

    @receiver(post_delete, sender="myapp.Item")
    def delete_image_on_delete(sender, instance, **kwargs):
        """
        Deletes image from S3 when an Item is deleted.
        """
        if instance.image:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=instance.image.name)

    wear_count = models.PositiveIntegerField(default=0)
    
    def cost_per_wear(self):
        return self.price / self.wear_count if self.wear_count > 0 else 0
    
    def __str__(self):
        return self.name if self.name else "Unnamed Item"
    
class WornItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate logs with a user
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="worn_logs")
    date = models.DateField()  # The date the item was worn