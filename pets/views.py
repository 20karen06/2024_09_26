from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Animal, Seller, Feedback, Wishlist
from .forms import AnimalForm, FeedbackForm, AnimalSearchForm, SignUpForm
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Animal
from django.views.generic import CreateView, ListView
from .models import Message


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('animal-list')


class AnimalListView(ListView):
    model = Animal
    template_name = 'animal_list.html'
    context_object_name = 'animals'
    paginate_by = 5

    def get_queryset(self):
        queryset = Animal.objects.all()
        form = AnimalSearchForm(self.request.GET)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            breed = form.cleaned_data.get('breed')
            animal_type = form.cleaned_data.get('animal_type')
            min_age = form.cleaned_data.get('min_age')
            max_age = form.cleaned_data.get('max_age')

            if name:
                queryset = queryset.filter(name__icontains=name)
            if breed:
                queryset = queryset.filter(breed__icontains=breed)
            if animal_type:
                queryset = queryset.filter(breed__icontains=animal_type)
            if min_age is not None:
                queryset = queryset.filter(age__gte=min_age)
            if max_age is not None:
                queryset = queryset.filter(age__lte=max_age)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AnimalSearchForm(self.request.GET)
        return context


class AnimalDetailView(DetailView):
    model = Animal
    template_name = 'animal_detail.html'
    context_object_name = 'animal'


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animal_form.html'
    success_url = reverse_lazy('animal-list')

    def form_valid(self, form):
        form.instance.seller = self.request.user.seller
        return super().form_valid(form)


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedback_form.html'

    def form_valid(self, form):
        form.instance.buyer = self.request.user
        form.instance.seller = get_object_or_404(Seller, id=self.kwargs['seller_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('animal-detail', kwargs={'pk': self.kwargs['animal_id']})


class WishlistAddView(LoginRequiredMixin, CreateView):
    model = Wishlist

    def post(self, request, *args, **kwargs):
        animal = get_object_or_404(Animal, id=kwargs['animal_id'])
        Wishlist.objects.create(user=request.user, animal=animal)
        return redirect('animal-detail', pk=animal.id)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['message']
    template_name = 'message_form.html'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.receiver = get_object_or_404(User, id=self.kwargs['receiver_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('messages')


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'message_list.html'

    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user)


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        animal_id = self.kwargs['animal_id']
        animal = Animal.objects.get(id=animal_id)
        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'animal': animal
        }
        return render(request, 'payment.html', context)


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        animal_id = self.kwargs['animal_id']
        animal = Animal.objects.get(id=animal_id)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': animal.breed,
                    },
                    'unit_amount': int(animal.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment-success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payment-cancel')),
        )

        return redirect(session.url)


class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Confirm the payment and allow the seller to post the animal.
        return render(request, 'payment_success.html')


class PaymentCancelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'payment_cancel.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You Have Been Logged In!"))
            return redirect("animal-list")
        else:
            messages.success(request, ("There was an error, please try again!"))
            return redirect("login")
    else:
        return render(request, "login.html")


def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out!"))
    return redirect("animal-list")
