from django.urls import path, include
from .views import *

urlpatterns = [
    path("menu-items/", menu_items.as_view()),
    path("menu-items/<int:pk>", single_menu_item.as_view()),
    path("orders/", orders.as_view()),
    path("orders/<int:pk>", single_order.as_view()),
    path("cart/", cart.as_view()),
    path("groups/manager/users", managers),
    path("groups/manager/users/<int:pk>", delete_manager),
    path("groups/drivers/users", drivers),
    path("groups/drivers/users/<int:pk>", delete_driver),

]