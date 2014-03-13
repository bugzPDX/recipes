from django import forms
from recipes.models import Recipe, Category, UserProfile
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
    name  = forms.CharField(max_length=128, help_text="Please enter a category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Category

class RecipeForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the recipe.")
    directions = forms.CharField(widget=forms.Textarea, help_text="Enter the recipe directions.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the recipe.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If url is not empty and doesn't start with 'http://', prepend 'http://'
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Recipe

        # Here we are hiding the foreign key.
        fields = ('title','directions', 'url', 'views')

class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter a username")
    email = forms.CharField(help_text="Please enter your email address")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    website = forms.URLField(help_text="Please enter your website URL", required=False)
    picture = forms.ImageField(help_text="Select a profile image to upload", required=False)
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
