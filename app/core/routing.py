from flet_route import path

from app.core.constants import INDEX_ROUTE, ATTRIBUTES_ROUTE
from app.views import AttributesView, IndexView

app_routes = [
    path(
        INDEX_ROUTE,
        clear=True,
        view=IndexView,
    ),
    path(
        ATTRIBUTES_ROUTE,
        clear=True,
        view=AttributesView,
    ),
]
