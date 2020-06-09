from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from catalog.models import Author, Book, BookInstance, Genre
from catalog.forms import RenewBookForm


def index(request):
    """Widok strony domowej"""
    # Generujemy liczbę obiektów
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()

    # Dostępne książki (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_books_wi = Book.objects.filter(title__istartswith='wi').count()

    # Liczba wizyt tego widoku w sesji
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_wi': num_books_wi,
        'num_visits': num_visits,
    }

    # Renderujemy szablon index.html z danych w zmiennej kontekstowej
    return render(request, 'catalog/index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5
    context_object_name = 'book_list'
    queryset = Book.objects.all()
    template_name = 'catalog/books/my_arbitrary_template_name_list.html'


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 3
    context_object_name = 'author_list'
    queryset = Author.objects.all()
    template_name = 'catalog/authors/my_arbitrary_template_name_list.html'


class BookDetailView(generic.DetailView):
    model = Book


class AuthorDetailView(generic.DetailView):
    model = Author


# def book_detail_view(request, primary_key):
#     book = get_object_or_404(Book, pk=primary_key)
#     return render(request, 'catalog/books/book_detail.html', context={'book': book})


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Ogólny widok oparty na klasach, zawierający listę wypożyczonych książek dla bieżącego użytkownika."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposal_renew_date = date.today() + timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposal_renew_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'data_zgonu': '05.01.2018'}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['imie', 'nazwisko', 'data_urodzenia', 'data_zgonu']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
