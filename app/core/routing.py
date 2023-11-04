from app.core.constants import INDEX_ROUTE, ATTRIBUTES_ROUTE, ILLIANA_ROUTE
from app.views import AttributesView, BaseView, IndexView, IllianaView

ROUTE_TO_VIEW: dict[str, BaseView] = {
    INDEX_ROUTE: IndexView,
    ATTRIBUTES_ROUTE: AttributesView,
    ILLIANA_ROUTE: IllianaView,
}
