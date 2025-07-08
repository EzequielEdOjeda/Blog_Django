from django import forms
from .models import Comment, Post, Category
from django.utils import timezone
from django.db.models import Count # Importar Count para el filtro de comentarios

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu comentario aquí...'}), label="Comentario")

    class Meta:
        model = Comment
        fields = ('content',)


class PostForm(forms.ModelForm):
    # Campo opcional para crear una nueva categoría
    new_category_name = forms.CharField(
        max_length=100,
        required=False,
        label='Nueva categoría (opcional)',
        help_text="Opcional: Si la categoría no existe, ingresa un nombre para crear una nueva."
    )

    class Meta:
        model = Post
        fields = ('title', 'category', 'new_category_name', 'content', 'featured_image', 'status')
        labels = {
            'title': 'Título',
            'category': 'Categoría',
            'new_category_name': 'Nueva categoría (opcional)',
            'content': 'Contenido',
            'featured_image': 'Imagen destacada',
            'status': 'Estado',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'featured_image': forms.FileInput(attrs={'class': 'w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opciones de categoría: primero las existentes, luego una opción para "crear nueva"
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].required = False # Hacer la categoría opcional si se va a crear una nueva

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category_name = cleaned_data.get('new_category_name')

        if not category and not new_category_name:
            raise forms.ValidationError("Debes seleccionar una categoría existente o proporcionar un nombre para una nueva categoría.")
        if category and new_category_name:
            raise forms.ValidationError("No puedes seleccionar una categoría existente Y crear una nueva al mismo tiempo.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_category_name = self.cleaned_data.get('new_category_name')

        if new_category_name:
            # Crear nueva categoría si se proporcionó un nombre
            instance.category, created = Category.objects.get_or_create(name=new_category_name)
        elif not instance.category:
            # Si no se seleccionó categoría y no se creó una nueva (esto no debería pasar si clean funciona bien)
            pass # O raise an error, depending on desired strictness

        if commit:
            instance.save()
            self.save_m2m() # Guardar relaciones ManyToMany si las hay

        return instance


class PostFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        label="Categoría"
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha Desde"
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha Hasta"
    )
    min_comments = forms.IntegerField(
        required=False,
        min_value=0,
        label="Mín. Comentarios"
    )
    query = forms.CharField(
        max_length=100,
        required=False,
        label="Buscar"
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            self.add_error('start_date', "La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.")
            self.add_error('end_date', "La fecha 'Hasta' no puede ser anterior a la fecha 'Desde'.")

        return cleaned_data
