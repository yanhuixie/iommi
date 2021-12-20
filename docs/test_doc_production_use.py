from iommi import *
from iommi.admin import Admin
from django.urls import (
    include,
    path,
)
from django.db import models
from tests.helpers import req, user_req, staff_req
from docs.models import *
request = req('get')



def test_production_use():
    # language=rst
    """
    Production use
    --------------

    You probably want to define your own `Style` in a production scenario. See
    :doc:`How to create a Style <styles>`, and especially the section on how to integrate into
    an existing code base.

    Just like you have your own custom base class for Django's `Model` to have a
    central place to put customization you will want to do the same for the base
    classes of iommi. In iommi this is even more important since you will almost
    certainly want to add more shortcuts that are specific to your product.

    Copy this boilerplate to some place in your code and import these classes
    instead of the corresponding ones from iommi:


    """
    import iommi


    class Page(iommi.Page):
        pass


    class Action(iommi.Action):
        pass


    class Field(iommi.Field):
        pass


    class Form(iommi.Form):
        class Meta:
            member_class = Field
            page_class = Page
            action_class = Action


    class Filter(iommi.Filter):
        pass


    class Query(iommi.Query):
        class Meta:
            member_class = Filter
            form_class = Form


    class Column(iommi.Column):
        pass


    class Table(iommi.Table):
        class Meta:
            member_class = Column
            form_class = Form
            query_class = Query
            page_class = Page
            action_class = Action


    class Menu(iommi.Menu):
        pass


    class MenuItem(iommi.MenuItem):
        pass
