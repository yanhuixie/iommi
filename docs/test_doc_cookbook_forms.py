from docs.models import *
from iommi import *
from tests.helpers import (
    req,
    show_output,
)

request = req('get')

from tests.helpers import req, user_req, staff_req
from django.template import Template
import pytest
pytestmark = pytest.mark.django_db


def test_forms():
    # language=rst
    """
    Forms
    -----

    """


def test_how_do_i_supply_a_custom_parser_for_a_field():
    # language=rst
    """
    .. _Field.parse:


    How do I supply a custom parser for a field?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pass a callable to the `parse` member of the field:


    """
    form = Form(
        auto__model=Track,
        fields__index__parse=
            lambda field, string_value, **_: int(string_value[:-3]),
    )

    # @test

    form = form.bind(request=req('get', index='123abc'))
    assert not form.get_errors()
    assert form.fields.index.value == 123


def test_how_do_i_make_a_field_non_editable():
    # language=rst
    """
    .. _Field.editable:

    How do I make a field non-editable?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pass a callable or `bool` to the `editable` member of the field:


    """
    form = Form(
        auto__model=Album,
        fields__name__editable=
            lambda request, **_: request.user.is_staff,
        fields__artist__editable=False,
    )

    # @test
    user_form = form.bind(request=user_req('get'))
    assert user_form.fields.name.editable is False
    assert user_form.fields.artist.editable is False

    staff_form = form.bind(request=staff_req('get'))
    assert staff_form.fields.name.editable is True
    assert staff_form.fields.artist.editable is False


def test_how_do_i_make_an_entire_form_non_editable(album):
    # language=rst
    """
    .. _Form.editable:

    How do I make an entire form non-editable?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a very common case so there's a special syntax for this: pass a `bool` to the form:


    """
    form = Form.edit(
        auto__instance=album,
        editable=False,
    )

    # @test

    form = form.bind(request=req('get'))
    assert form.fields.name.editable is False
    assert form.fields.year.editable is False
    show_output(form)

    # @end


def test_how_do_i_supply_a_custom_validator():
    # language=rst
    """
    .. _Field.is_valid:

    How do I supply a custom validator?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pass a callable that has the arguments `form`, `field`, and `parsed_data`. Return a tuple `(is_valid, 'error message if not valid')`.


    """
    form = Form.create(
        auto__model=Album,
        auto__include=['name'],
        fields__name__is_valid=
            lambda form, field, parsed_data: (False, 'invalid!'),
    )

    # @test

    form = form.bind(request=req('post', name='foo', **{'-submit': ''}))
    assert form.get_errors() == {'fields': {'name': {'invalid!'}}}
    show_output(form)


def test_how_do_i_validate_multiple_fields_together():
    # language=rst
    """
    How do I validate multiple fields together?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Refine the `post_validation` hook on the `form`. It is run after all the individual fields validation
    has run. But note that it is run even if the individual fields validation was not successful.

    """


def test_how_do_i_exclude_a_field():
    # language=rst
    """
    How do I exclude a field?
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    See `How do I say which fields to include when creating a form from a model?`_


    """


def test_how_do_i_say_which_fields_to_include_when_creating_a_form_from_a_model():
    # language=rst
    """
    How do I say which fields to include when creating a form from a model?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    `Form()` has four methods to select which fields are included in the final form:

    1. the `auto__include` parameter: this is a list of strings for members of the model to use to generate the form.
    2. the `auto__exclude` parameter: the inverse of `include`. If you use this the form gets all the fields from the model excluding the ones with names you supply in `exclude`.
    3. for more advanced usages you can also pass the `include` parameter to a specific field like `fields__my_field__include=True`. Here you can supply either a `bool` or a callable like `fields__my_field__include=lambda request, **_: request.user.is_staff`.
    4. you can also add fields that are not present in the model by passing configuration like `fields__foo__attr='bar__baz'` (this means create a `Field` called `foo` that reads its data from `bar.baz`). You can either pass configuration data like that, or pass an entire `Field` instance.

    """


def test_how_do_i_supply_a_custom_initial_value():
    # language=rst
    """
    .. _Field.initial:

    How do I supply a custom initial value?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pass a value or callable to the `initial` member:


    """
    form = Form(
        auto__model=Album,
        fields__name__initial='Paranoid',
        fields__year__initial=lambda field, form, **_: 1970,
    )

    # @test

    form = form.bind(request=req('get'))
    assert form.fields.name.value == 'Paranoid'
    assert form.fields.year.value == 1970
    show_output(form)

    # language=rst
    """
    If there are `GET` parameters in the request, iommi will use them to fill in the appropriate fields. This is very handy for supplying links with partially filled in forms from just a link on another part of the site.

    """


def test_how_do_i_set_if_a_field_is_required():
    # language=rst
    """
    .. _Field.required:

    How do I set if a field is required?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Normally this will be handled automatically by looking at the model definition, but sometimes you want a form to be more strict than the model. Pass a `bool` or a callable to the `required` member:


    """
    form = Form(
        auto__model=Album,
        fields__name__required=True,
        fields__year__required=lambda field, form, **_: True,
    )

    # @test

    form = form.bind(request=req('get'))
    assert form.fields.name.required is True
    assert form.fields.year.required is True


def test_how_do_i_change_the_order_of_the_fields():
    # language=rst
    """
    .. _Field.after:

    How do I change the order of the fields?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can change the order in your model definitions as this is what iommi uses. If that's not practical you can use the `after` member. It's either the name of a field or an index. There is a special value `LAST` to put a field last.


    """
    from tri_declarative import LAST

    form = Form(
        auto__model=Album,
        fields__name__after=LAST,
        fields__year__after='artist',
        fields__artist__after=0,
    )

    # @test

    form = form.bind(request=req('get'))
    assert list(form.fields.keys()) == ['artist', 'year', 'name']
    show_output(form)

    # language=rst
    """
    This will make the field order `artist`, `year`, `name`.

    If there are multiple fields with the same index or name the order of the fields will be used to disambiguate.

    """


def test_how_do_i_specify_which_model_fields_the_search_of_a_choice_queryset_use():
    # language=rst
    """
    .. _Field.search_fields:

    How do I specify which model fields the search of a choice_queryset use?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    `Form.choice_queryset` uses the registered search fields for filtering and ordering.
    See :doc:`registrations` for how to register one. If present it will default
    to a model field `name`.


    In special cases you can override which attributes it uses for
    searching by specifying `search_fields`:


    """
    form = Form(
        auto__model=Album,
        fields__name__search_fields=('name', 'year'),
    )

    # language=rst
    """
    This last method is discouraged though, because it will mean searching behaves
    differently in different parts of your application for the same data.


    """


def test_how_do_i_insert_a_css_class_or_html_attribute():
    # language=rst
    """
    How do I insert a CSS class or HTML attribute?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    See :doc:`Attrs`.

    """


def test_how_do_i_override_rendering_of_an_entire_field():
    # language=rst
    """
    .. _Field.template:

    How do I override rendering of an entire field?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pass a template name:


    """
    form = Form(
        auto__model=Album,
        fields__year__template='my_template.html',
    )

    # @test
    show_output(form)
    # @end
    
    # language=rst
    """
    or a `Template` object:
    """

    form = Form(
        auto__model=Album,
        fields__year__template=Template('This is from the inline template'),
    )

    # @test
    show_output(form)
    # @end


def test_how_do_i_override_rendering_of_the_input_field():
    # language=rst
    """
    .. _Field.input:

    How do I override rendering of the input field?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    Pass a template name or a `Template` object to the `input` namespace:


    """
    form = Form(
        auto__model=Album,
        fields__year__input__template='my_template.html',
    )

    # @test
    show_output(form)
    # @end
    
    # language=rst
    """
    
    """

    form = Form(
        auto__model=Album,
        fields__year__input__template=Template('This is from the inline template'),
    )

    # @test
    show_output(form)
    # @end


def test_how_do_i_change_how_fields_are_rendered_everywhere_in_my_project():
    # language=rst
    """
    How do I change how fields are rendered everywhere in my project?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Define a custom style and override the appropriate fields. For
    example here is how you could change `Field.date` to use a text
    based input control (as opposed to the date picker that `input type='date'`
    uses).

    """
    # @test
    from iommi.style_bootstrap_docs import bootstrap_docs as bootstrap
    # @end

    my_style = Style(bootstrap, Field__shortcuts__date__input__attrs__type='text')

    # language=rst
    """
    When you do that you will get English language relative date parsing
    (e.g. "yesterday", "3 days ago") for free, because iommi used to use a
    text based input control and the parser is applied no matter what
    (its just that when using the default date picker control it will
    always only see ISO-8601 dates).
    """

    # @test
    form = Form(fields__date=Field.date(), iommi_style=my_style)
    show_output(form)
    # @end
