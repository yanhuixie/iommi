import pytest
from docs.models import *
from iommi import *
from tests.helpers import (
    req,
    show_output,
)

pytestmark = pytest.mark.django_db


request = req('get')


def fill_dummy_data(): pass


def test_tables():
    # language=rst
    """
    Tables
    ======

    iommi tables makes it easy to create full featured HTML tables easily:

    * generates header, rows and cells
    * sorting
    * filtering
    * pagination
    * bulk edit
    * link creation
    * customization on multiple levels, all the way down to templates for cells
    * automatic rowspan
    * grouping of headers

    .. image:: tables_example_albums.png

    The code for the example above:


    """
    Table(
        auto__model=Album,
        page_size=10,
    )

    # language=rst
    """
    Read the full documentation and the :doc:`cookbook` for more.

    """
    

def test_creating_tables_from_models():
    # language=rst
    """
    Creating tables from models
    ---------------------------

    Say I have some model:

    """
    class Foo(models.Model):
        a = models.IntegerField()

        def __str__(self):
            return f'Foo: {self.a}'

    # @test
        class Meta:
            app_label = 'docs_tables'
    assert str(Foo(a=7)) == 'Foo: 7'

    # @end

    class Bar(models.Model):
        b = models.ForeignKey(Foo, on_delete=models.CASCADE)
        c = models.CharField(max_length=255)

    # @test
        class Meta:
            app_label = 'docs_tables'

    # @end
    # language=rst
    """
    Now I can display a list of `Bar` in a table like this:


    """
    def my_view(request):
        return Table(auto__model=Bar)

    # @test
    my_view(req('get'))
    # @end

    # language=rst
    """
    This automatically creates a table with pagination and sorting. If you pass
    `query_from_indexes=True` you will get filters for all the model fields
    that have database indexes. This filtering system includes an advanced filter
    language. See :doc:`queries` for more on filtering.


    """


def test_explicit_tables(small_discography):
    # language=rst
    """
    Explicit tables
    ---------------

    You can also create tables explicitly:


    """
    def albums(request):
        class AlbumTable(Table):
            # Shortcut for creating checkboxes to select rows
            select = Column.select()

            name = Column()

            # Show the name field from Artist. This works for plain old objects too.
            artist_name = Column.number(
                attr='artist__name',

                # put this field into the query language
                filter__include=True,
            )
            year = Column(
                # Enable bulk editing for this field
                bulk__include=True,
            )

        return AlbumTable(rows=Album.objects.all())

    # language=rst
    """
    This gives me a view with filtering, sorting, bulk edit and pagination.
    """

    # @test
    show_output(albums(req('get')))
    # @end


def test_table_of_plain_python_objects():
    # language=rst
    """
    Table of plain python objects
    -----------------------------


    """
    def plain_objs_view(request):
        # Say I have a class...
        class Foo(object):
            def __init__(self, i):
                self.a = i
                self.b = 'foo %s' % (i % 3)
                self.c = (i, 1, 2, 3, 4)

        # and a list of them
        foos = [Foo(i) for i in range(4)]

        # I can declare a table:
        class FooTable(Table):
            a = Column.number()

            b = Column()

            # Display the last value of the tuple
            c = Column(
                cell__format=lambda value, **_: value[-1],
            )

            # Calculate a value not present in Foo
            sum_c = Column(
                cell__value=lambda row, **_: sum(row.c),
                sortable=False,
            )

        # now to get an HTML table:
        return FooTable(rows=foos)

    # @test
    show_output(plain_objs_view(req('get')))
    # @end

    # language=rst
    """
    All these examples and a bigger example using many more features can be found in the examples project.
    """
