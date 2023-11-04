from app.core.constants import INDEX_ROUTE, ATTRIBUTES_ROUTE
from app.views import AttributesView, BaseView, IndexView

ROUTE_TO_VIEW: dict[str, BaseView] = {
    INDEX_ROUTE: IndexView,
    ATTRIBUTES_ROUTE: AttributesView,
}
