from django import forms
from .models import LostItem, FoundItem, ItemImage, Claim, LostFoundCategory, AutoDeleteEmptyFormSet
from django.forms import BaseInlineFormSet
class LostItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=LostFoundCategory.objects.all(),  # Load all categories dynamically
        empty_label="Select Category",
        required=True
    )

    class Meta:
        model = LostItem
        fields = ['name', 'description', 'category', 'lost_location', 'lost_date', 'color', 'additional_details']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'additional_details': forms.Textarea(attrs={'rows': 3}),
            'lost_date': forms.DateInput(attrs={'type': 'date'}),
        }

class FoundItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=LostFoundCategory.objects.all(),  # Load all categories dynamically
        empty_label="Select Category",
        required=True
    )

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

class RequiredInlineFormSet(BaseInlineFormSet):
    """Auto-remove empty image forms"""
    def clean(self):
        super().clean()
        self.forms = [form for form in self.forms if form.cleaned_data.get('image')]

LostItemImageFormSet = forms.inlineformset_factory(
    LostItem, ItemImage, form=ItemImageForm, extra=3, fk_name='lost_item',
    formset=AutoDeleteEmptyFormSet
)

FoundItemImageFormSet = forms.inlineformset_factory(
    FoundItem, ItemImage, form=ItemImageForm, extra=3, fk_name='found_item',
    formset=AutoDeleteEmptyFormSet
)
from django.forms import BaseInlineFormSet





class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['proof_details']
        widgets = {
            'proof_details': forms.Textarea(attrs={'rows': 4}),
        }
