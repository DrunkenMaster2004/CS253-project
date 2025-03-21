from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Item, ItemImage, ItemCategory

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
    category = forms.ModelChoiceField(
        queryset=ItemCategory.objects.all(),
        empty_label="Select a Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Item
        fields = ['name', 'price', 'description', 'category', 'is_available']

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image']

ItemImageFormSet = forms.inlineformset_factory(
    Item, ItemImage, form=ItemImageForm, extra=3
)