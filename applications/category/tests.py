import pytest
from applications.category.models import Category


@pytest.mark.django_db
def test_category_str():
    cat = Category.objects.create(category_name='Shirts', slug='shirts')
    assert str(cat) == 'Shirts'


@pytest.mark.django_db
def test_category_get_url():
    cat = Category.objects.create(category_name='Jeans', slug='jeans')
    assert 'jeans' in cat.get_url()
