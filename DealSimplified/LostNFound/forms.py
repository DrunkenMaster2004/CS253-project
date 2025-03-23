from django import forms
from .models import LostItem, FoundItem, ItemImage, Claim
from .models import LostItem, LostFoundCategory

class LostItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=LostFoundCategory.objects.none(),  # Initially empty
        empty_label="Select Category",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = LostFoundCategory.objects.filter(
            name__in=["Electronics", "Clothing", "Accessories", "Documents", "Miscellaneous"]
        )

    class Meta:
        model = LostItem
        fields = ['name', 'description', 'category', 'lost_location', 'lost_date', 'color', 'additional_details', 'reward']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'additional_details': forms.Textarea(attrs={'rows': 3}),
            'lost_date': forms.DateInput(attrs={'type': 'date'}),
        }

class FoundItemForm(forms.ModelForm):
    class Meta:
        model = FoundItem
        fields = ['name', 'description', 'category', 'found_location', 'found_date', 'color', 'additional_details']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'additional_details': forms.Textarea(attrs={'rows': 3}),
            'found_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image']

LostItemImageFormSet = forms.inlineformset_factory(
    LostItem, ItemImage, form=ItemImageForm, extra=3, fk_name='lost_item'
)

FoundItemImageFormSet = forms.inlineformset_factory(
    FoundItem, ItemImage, form=ItemImageForm, extra=3, fk_name='found_item'
)

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['proof_details']
        widgets = {
            'proof_details': forms.Textarea(attrs={'rows': 4}),
        }