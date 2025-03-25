from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.timezone import now

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20)
    email_id = models.EmailField(unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.roll_no})"

class ItemCategory(models.Model):
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Clothing', 'Clothing'),
        ('Accessories', 'Accessories'),
        ('Documents', 'Documents'),
        ('Miscellaneous', 'Miscellaneous'),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(null=True, blank=True)  # Allowing null values

    def __str__(self):
        return self.name


class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='selling_items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    age = models.PositiveIntegerField(help_text="Age of item in months", default=0)
    is_negotiable = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='item_images')
    
    def __str__(self):
        return f"Image for {self.item.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'item')
        
    def __str__(self):
        return f"{self.user.name}'s wishlist item: {self.item.name}"

class Chat(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_chats')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_chats')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat between {self.sender.name} and {self.receiver.name}"
# class Message(models.Model):
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
#     sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
#     content = models.TextField()  # This might be renamed to `text` by accident
#     is_read = models.BooleanField(default=False)
#     timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)
    
    # def __str__(self):
    #     return f"Message from {self.sender.name} at {self.timestamp}"
    def __str__(self):
        return f"{self.sender.user.username}: {self.content[:20]} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, email_id=instance.email)
class ChatThread(models.Model):
    participants = models.ManyToManyField(User)



# class Message(models.Model):
#     thread = models.ForeignKey(ChatThread, related_name='messages', on_delete=models.CASCADE)
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     text = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)p