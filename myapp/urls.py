from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('upload/', views.upload_product, name='upload_product'),
    path('search/', views.search_product, name='search_product'),
    path('edit/<str:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<str:product_id>/', views.delete_product, name='delete_product'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('line-pay-confirmation/<int:order_id>/', views.line_pay_confirmation, name='line_pay_confirmation'),
    path('bank-transfer-confirmation/<int:order_id>/', views.bank_transfer_confirmation, name='bank_transfer_confirmation'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='myapp/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='myapp/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='myapp/password_reset_complete.html'), name='password_reset_complete'),
    path('create-admin/', views.admin_register, name='admin_register'),
]