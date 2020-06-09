from django.db import models
from django.urls import reverse  # Służy do generowania adresów URL poprzez odwrócenie wzorców adresów URL
from django.contrib.auth.models import User
from uuid import uuid4  # Wymagane do unikalnych instancji książek
from datetime import date


class Genre(models.Model):
    """Model reprezentujący gatunek książki."""
    name = models.CharField(max_length=200, help_text='Wprowadź gatunek książki (np. Science fiction)')

    def __str__(self):
        """Ciąg do reprezentowania obiektu Modelu."""
        return self.name


class Language(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Wprowadź język naturalny książki (np. Angielski, francuski, japoński itp.)'
    )

    def __str__(self):
        return self.name


class Book(models.Model):
    """Model reprezentujący książkę (ale nie konkretną kopię książki)."""
    title = models.CharField('Tytuł', max_length=200)

    # Używany klucz obcy, ponieważ książka może mieć tylko jednego autora, ale autorzy mogą mieć wiele książek
    # Autor jako ciąg zamiast obiektu, ponieważ nie został jeszcze zadeklarowany w pliku
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Wprowadź krótki opis książki')
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 znakowy <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">numer ISBN</a>')

    # Używamy pola wiele do wielu, ponieważ gatunek może zawierać wiele książek.Książki mogą obejmować wiele gatunków.
    # Klasa gatunku została już zdefiniowana, więc możemy określić obiekt powyżej.
    genre = models.ManyToManyField(Genre, help_text='Wybierz gatunek książki')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def display_genre(self):
        """Utwórz tekst dla gatunku. Jest to wymagane do wyświetlenia gatunku w panelu Administracyjnym."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Gatunek'

    def __str__(self):
        """Ciąg reprezentujący obiekt Modelu."""
        return self.title

    def get_absolute_url(self):
        """Zwraca adres URL, aby uzyskać dostęp do rekordu szczegółów tej książki."""
        return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    """Model reprezentujący konkretną kopię książki (tj. Którą można wypożyczyć z biblioteki)."""
    id = models.UUIDField(primary_key=True, default=uuid4,
                          help_text="Unikalny identyfikator tej konkretnej książki w całej bibliotece")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, verbose_name='Książka')

    imprint = models.CharField('Wydawca', max_length=200)
    due_back = models.DateField('Z powrotem', null=True, blank=True)

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Pożyczający')

    @property
    def id_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS = (
        ('m', 'Konserwacja'),
        ('o', 'Wypożyczony'),
        ('a', 'Dostępne'),
        ('r', 'Rezerwacja'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m',
                              help_text='Dostępność książki')

    class Meta:
        ordering = ['due_back']
        permissions = (('can_mark_returned', 'Oddaj książkę'),)

    def __str__(self):
        """Ciąg reprezentujący obiekt Modelu."""
        return f'{self.book.title} - ({self.id})'


class Author(models.Model):
    """Model reprezentujący autora."""
    imie = models.CharField('Imię', max_length=100)
    nazwisko = models.CharField(max_length=100)
    data_urodzenia = models.DateField(null=True, blank=True)
    data_zgonu = models.DateField('Zmarł', null=True, blank=True)

    # def imie_pl(self):
    #     return f"{self.imie}".capitalize()
    # imie_pl.short_description = 'IMIĘ'

    class Meta:
        ordering = ['nazwisko', 'imie']

    def __str__(self):
        """Ciąg reprezentujący obiekt Modelu."""
        return f'{self.nazwisko}, {self.imie}'

    def get_absolute_url(self):
        """Zwraca adres URL, aby uzyskać dostęp do określonej instancji autora."""
        return reverse('author-detail', args=[str(self.id)])
