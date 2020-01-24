from django.urls import path, include

from . import views as kart_views

urlpatterns = [
	path('', kart_views.index, name='index'),
	path('home/', kart_views.home, name='home'),
	path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', kart_views.signup, name='signup'),
    path('signup/delivery_agent/', kart_views.signup_delivery_agent, name='signup-delivery-agent'),
    path('signup/shopping_user/', kart_views.signup_shopping_user, name='signup-shopping-user'),
    path('product/view/<int:pk>/', kart_views.view_product, name='view-product'),
    path('order/product/<int:pk>/', kart_views.order, name='order'),
    path('order/view/<int:pk>/', kart_views.view_order, name='view-order'),
    path('order/<int:pk>/mark/accepted/', kart_views.order_accepted, name='order-accepted'),
    path('order/<int:pk>/mark/arrived/', kart_views.order_arrived, name='order-arrived'),
    path('order/<int:pk>/mark/delivered/', kart_views.order_delivered, name='order-delivered'),
    path('order/view/accepted/', kart_views.view_accepted_orders, name='view-accepted-orders'),
    path('order/view/arrived/', kart_views.view_arrived_orders, name='view-arrived-orders'),
    path('order/view/delivered/', kart_views.view_delivered_orders, name='view-delivered-orders'),
    path('my_orders/', kart_views.my_orders, name='my-orders'),
    path('order/<int:pk>/add/complaint/', kart_views.add_complaint, name='add-complaint'),
    path('order/<int:pk>/view/complaints/', kart_views.view_order_complaints, name='view-order-complaints'),
    path('order/<int:pk>/cancel/', kart_views.cancel_order, name='order-cancel'),
    path('populate/products', kart_views.populate_products, name='populate-products'),
]
