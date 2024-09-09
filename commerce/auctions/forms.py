from django import forms

class Create_listing(forms.Form):
    title = forms.CharField(
        label="Title",
        max_length=64,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter Title'}))
    
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Enter Description'}))
    
    bid = forms.DecimalField(
        label="Bid",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter Starting Bid'}))
    
    image = forms.URLField(
        label="Image",
        required=False,
        widget=forms.URLInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter Image URL'}))
    
    category = forms.CharField(
        label="Category",
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter Category'}))