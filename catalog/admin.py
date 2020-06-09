from django.contrib import admin

from .models import Author, Genre, Book, BookInstance, Language


class BookInLine(admin.TabularInline):
    model = Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('nazwisko', 'imie', 'data_urodzenia', 'data_zgonu')
    fields = ['imie', 'nazwisko', ('data_urodzenia', 'data_zgonu')]
    inlines = [BookInLine]


class BookInstanceInLine(admin.TabularInline):
    model = BookInstance


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    def author_pl(self, obj):
        """Właściwość po polsku"""
        return obj.__str__()

    author_pl.short_description = 'Autor'
    list_display = ('title', 'author_pl', 'display_genre')
    inlines = [BookInstanceInLine]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    def book_pl(self, obj):
        return obj.__str__()

    book_pl.short_description = 'Książka'

    list_display = ('book_pl', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Dostępność', {
            'fields': ('status', 'due_back', 'borrower')
        })
    )


admin.site.register(Genre)
admin.site.register(Language)
