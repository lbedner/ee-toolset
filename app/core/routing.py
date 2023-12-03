from typing import Type

from app.core.constants import ATTRIBUTES_ROUTE, ILLIANA_ROUTE, INDEX_ROUTE
from app.views import AttributesView, BaseView, IllianaView, IndexView

ROUTE_TO_VIEW: dict[str, Type[BaseView]] = {
    INDEX_ROUTE: IndexView,
    ATTRIBUTES_ROUTE: AttributesView,
    ILLIANA_ROUTE: IllianaView,
}
