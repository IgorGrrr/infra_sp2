from django.contrib import admin
from .models import Category, Comment, Genre, GenreTitle, Review, Title, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'email', 'is_superuser', 'role', 'confirmation_code',
        'password'
    )
    exclude = ('bio',)


admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(GenreTitle)
admin.site.register(Review)
admin.site.register(Comment)
