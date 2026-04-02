"""
Formularios para la aplicación de tienda.
"""
from django import forms
from .models import MovimientoInventario, StockActual, Producto


class MovimientoInventarioEntradaForm(forms.ModelForm):
    """Formulario para registrar entrada de productos al inventario."""
    
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo_entrada', 'cantidad', 'referencia', 'descripcion']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'tipo_entrada': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '1',
                'required': True,
                'placeholder': 'Cantidad'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Número de compra, factura, etc.'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(disponible=True).order_by('categoria', 'nombre')
        self.fields['producto'].label = 'Producto'
        self.fields['tipo_entrada'].label = 'Tipo de Entrada'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['referencia'].label = 'Referencia'
        self.fields['referencia'].required = False
        self.fields['descripcion'].label = 'Descripción'
        self.fields['descripcion'].required = False


class MovimientoInventarioSalidaForm(forms.ModelForm):
    """Formulario para registrar salida de productos del inventario."""
    
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo_salida', 'cantidad', 'referencia', 'descripcion']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'tipo_salida': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '1',
                'required': True,
                'placeholder': 'Cantidad'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Número de venta, referencia, etc.'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(disponible=True).order_by('categoria', 'nombre')
        self.fields['producto'].label = 'Producto'
        self.fields['tipo_salida'].label = 'Tipo de Salida'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['referencia'].label = 'Referencia'
        self.fields['referencia'].required = False
        self.fields['descripcion'].label = 'Descripción'
        self.fields['descripcion'].required = False


class StockMinimoForm(forms.ModelForm):
    """Formulario para ajustar el stock mínimo por producto."""
    
    class Meta:
        model = StockActual
        fields = ['stock_minimo']
        widgets = {
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '0',
                'required': True,
                'placeholder': 'Stock mínimo'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock_minimo'].label = 'Stock Mínimo'


class AjusteStockForm(forms.ModelForm):
    """Formulario para hacer ajustes manuales al stock."""
    
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'cantidad', 'descripcion']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '0',
                'required': True,
                'placeholder': 'Nueva cantidad'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo del ajuste'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(disponible=True).order_by('categoria', 'nombre')
        self.fields['producto'].label = 'Producto'
        self.fields['cantidad'].label = 'Nueva Cantidad'
        self.fields['descripcion'].label = 'Motivo'
        self.fields['descripcion'].required = False
