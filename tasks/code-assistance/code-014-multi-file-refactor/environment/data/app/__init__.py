"""Application package."""

from .models import User, Product
from .views import render_user, render_product
from .utils import clean_name, clean_title
