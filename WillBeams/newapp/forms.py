from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    def formfield_callback(f, **kwargs):
        if f.name == 'email':
            kwargs['required'] = True
        return f.formfield(**kwargs)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)
