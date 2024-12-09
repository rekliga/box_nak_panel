from django import forms

class ProductoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    CATEGORIAS = [
        ("electro", "Electrónica"),
        ("ropa", "Ropa"),
        ("alimentos", "Alimentos"),
    ]

    categoria = forms.ChoiceField(
        choices=CATEGORIAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Categoría"
    )
    precio = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    stock = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    imagen = forms.ImageField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
