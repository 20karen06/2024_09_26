from . import views
from django.urls import path
from django.views.generic import TemplateView

from .views import AnimalListView, AnimalDetailView, AnimalCreateView, FeedbackCreateView, WishlistAddView, SignUpView
from .views import PaymentView, CreateCheckoutSessionView, PaymentSuccessView, PaymentCancelView
from .views import MessageCreateView, MessageListView

urlpatterns = [
    path('', AnimalListView.as_view(), name='animal-list'),
    path('animal/<int:pk>/', AnimalDetailView.as_view(), name='animal-detail'),
    path('animal/create/', AnimalCreateView.as_view(), name='animal-create'),
    path('search/', AnimalListView.as_view(), name='animal-search'),
    path('feedback/<int:seller_id>/<int:animal_id>/', FeedbackCreateView.as_view(), name='feedback-create'),
    path('wishlist/add/<int:animal_id>/', WishlistAddView.as_view(), name='wishlist-add'),
    path('payment/<int:animal_id>/', PaymentView.as_view(), name='payment'),
    path('create-checkout-session/<int:animal_id>/', CreateCheckoutSessionView.as_view(),
         name='create-checkout-session'),
    path('payment-success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payment-cancel/', PaymentCancelView.as_view(), name='payment-cancel'),

    path('message/send/<int:receiver_id>/', MessageCreateView.as_view(), name='send-message'),
    path('messages/', MessageListView.as_view(), name='messages'),
    path('animal-cruelty/', TemplateView.as_view(template_name='animal_cruelty.html'), name='animal-cruelty'),

    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('signup/', SignUpView.as_view(), name='signup'),
]


