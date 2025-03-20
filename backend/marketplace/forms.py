from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Item, ItemImage

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@iitk.ac.in'):
            raise forms.ValidationError("Please use your IITK email address.")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'roll_no', 'phone_number', 'address', 'profile_picture']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'category', 'price', 'condition', 'age', 'is_negotiable']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image']

ItemImageFormSet = forms.inlineformset_factory(
    Item, ItemImage, form=ItemImageForm, extra=3
)