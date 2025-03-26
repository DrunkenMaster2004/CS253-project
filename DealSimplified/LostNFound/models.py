from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Profile
# from django.utils import timezone

class LostFoundCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class LostItem(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('found', 'Found'),
        ('closed', 'Closed'),
    ]
    
    reporter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(LostFoundCategory, on_delete=models.CASCADE)
    lost_location = models.CharField(max_length=200)
    lost_date = models.DateField()
    color = models.CharField(max_length=50)
    additional_details = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    date_reported = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.name} (Lost)"

class FoundItem(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('claimed', 'Claimed'),
        ('closed', 'Closed'),
    ]
    
    reporter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(LostFoundCategory, on_delete=models.CASCADE)
    found_location = models.CharField(max_length=200)
    found_date = models.DateField()
    color = models.CharField(max_length=50)
    additional_details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    date_reported = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} (Found)"

class ItemImage(models.Model):
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='lostfound_images')
    
    def __str__(self):
        if self.lost_item:
            return f"Image for lost item: {self.lost_item.name}"
        return f"Image for found item: {self.found_item.name}"

class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    claimant = models.ForeignKey(Profile, on_delete=models.CASCADE)
    proof_details = models.TextField(help_text="Details to prove ownership")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_claimed = models.DateTimeField(auto_now_add=True)
    review = models.TextField(blank=True, null=True)  # Add this field
    
    def __str__(self):
        return f"Claim for {self.found_item.name} by {self.claimant.name}"


class Match(models.Model):
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE)
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    match_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    date_matched = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Match between lost:{self.lost_item.name} and found:{self.found_item.name}"


    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('claim', 'New Claim'),
        ('match', 'Potential Match'),
        ('chat', 'New Message'),
        ('status', 'Status Update'),
    ]
    
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    item = models.ForeignKey(LostItem, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.user.username}: {self.message[:50]}"
   