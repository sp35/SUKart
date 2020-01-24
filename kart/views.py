from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from .forms import DeliveryAgentSignUpForm, ShoppingUserSignUpForm, SearchForm
from .models import Product, ShoppingUser, DeliveryAgent, Order
from . import sendgrid_mail


def signup(request):
	return render(request, 'registration/signup.html')


def signup_delivery_agent(request):
	if request.method == 'POST':
		form = DeliveryAgentSignUpForm(request.POST)
		if form.is_valid():
			form.save()            
			messages.success(request, 'Your account has been created! You are now able to log in')
			return redirect('home')
	else:
		form = DeliveryAgentSignUpForm()
	return render(request, 'registration/signup_form.html', {'form': form, 'user_type': 'Delivery Agent'})


def signup_shopping_user(request):
	if request.method == 'POST':
		form = ShoppingUserSignUpForm(request.POST)
		if form.is_valid():
			form.save()            
			messages.success(request, 'Your account has been created! You are now able to log in')
			return redirect('home')
	else:
		form = ShoppingUserSignUpForm()
	return render(request, 'registration/signup_form.html', {'form': form, 'user_type': 'Shopping User'})


def index(request):
	if request.user.is_authenticated:
		return redirect('home')
	return render(request, 'landing.html')


@login_required
def home(request):
	if request.user.is_delivery_agent:
		orders = Order.objects.filter(delivery_agent=DeliveryAgent.objects.get(user=request.user), accepted=False)
		orders.order_by('order_datetime')
		if request.method == 'POST':
			s_form = SearchForm(request.POST)
			if s_form.is_valid():
				query = s_form.cleaned_data['query']
				orders = orders.filter(product__title__icontains=query)
		else:
			s_form = SearchForm()
		return render(request, "kart/delivery_agent_home.html", {'orders': orders, 's_form': s_form})
	elif request.user.is_shopping_user:
		if request.method == 'POST':
			s_form = SearchForm(request.POST)
			if s_form.is_valid():
				query = s_form.cleaned_data['query']
				products = Product.objects.filter(title__icontains=query)
		else:
			s_form = SearchForm()
			products = Product.objects.all()
		currency = ShoppingUser.objects.get(user=request.user).currency
		return render(request, "kart/shopping_user_home.html", {'products': products, 'currency': currency, 's_form': s_form})
	return redirect('login')


@login_required
def view_product(request, pk):
	if not request.user.is_shopping_user:
		return PermissionDenied()
	product = Product.objects.get(pk=pk)
	return render(request, "kart/product_detail.html", {'product': product})


@login_required
def view_order(request, pk):
	order = Order.objects.get(pk=pk)
	return render(request, "kart/order_detail.html", {'order': order})


@login_required
def order(request, pk):
	if not request.user.is_shopping_user:
		return PermissionDenied()
	shopping_user = ShoppingUser.objects.get(user=request.user)
	try:
		product = Product.objects.get(pk=pk)
	except Product.DoesNotExist:
		return HttpResponse("Product Does Not Exist")
	if shopping_user.currency < product.price:
		messages.warning(request, 'Insufficient Balance')
	else:
		Order.objects.create(product=product, shopping_user=shopping_user, delivery_agent=DeliveryAgent.objects.first())
		messages.success(request, "Ordered Successfully")

	return redirect('home')


@login_required
def order_accepted(request, pk):
	if not request.user.is_delivery_agent:
		return PermissionDenied()
	order = Order.objects.get(pk=pk)
	order.accepted = True
	order.save()

	return redirect('view-order', pk=pk)


@login_required
def order_arrived(request, pk):
	if not request.user.is_delivery_agent:
		return PermissionDenied()
	order = Order.objects.get(pk=pk)
	# send mail
	subject = "Order Arrived"
	html_content = f"""
	<strong>{ order.product.title }</strong>
	<em>by { order.product.company.name }</em> has arrived at the delivery agent's facility and will be delivered to you soon."""
	sent = sendgrid_mail.send_mail(to_email=order.shopping_user.user.email, subject=subject, html_content=html_content)
	if sent:
		order.arrived = True
		order.save()
		messages.success(request, "Marked as arrived and user notified")
	else:
		messages.error(request, "Sending mail failed")

	return redirect('view-order', pk=pk)


@login_required
def order_delivered(request, pk):
	if not request.user.is_delivery_agent:
		return PermissionDenied()
	order = Order.objects.get(pk=pk)
	# send mail
	subject = "Order Delivered"
	html_content = f"""
	<strong>{ order.product.title }</strong>
	<em>by { order.product.company.name }</em> has been delivered to you."""
	sent = sendgrid_mail.send_mail(to_email=order.shopping_user.user.email, subject=subject, html_content=html_content)
	if sent:
		order.delivered = True
		order.delivered_datetime = datetime.now()
		order.save()
		messages.success(request, "Marked as delivered and user notified")
	else:
		messages.error(request, "Sending mail failed")

	return redirect('view-order', pk=pk)


@login_required
def view_accepted_orders(request):
	if not request.user.is_delivery_agent:
		return PermissionDenied()
	orders = Order.objects.filter(delivery_agent=DeliveryAgent.objects.get(user=request.user), accepted=True, arrived=False, delivered=False)

	return render(request, 'kart/orders.html', {'orders': orders})


@login_required
def view_arrived_orders(request):
	if not request.user.is_delivery_agent:
		return PermissionDenied()
	orders = Order.objects.filter(delivery_agent=DeliveryAgent.objects.get(user=request.user), accepted=True, arrived=True, delivered=False)

	return render(request, 'kart/orders.html', {'orders': orders})


@login_required
def view_delivered_orders(request):
	if not request.user.is_delivery_agent:
		return PermissionDenied()
	orders = Order.objects.filter(delivery_agent=DeliveryAgent.objects.get(user=request.user), delivered=True)

	return render(request, 'kart/orders.html', {'orders': orders})


@login_required
def my_orders(request):
	if not request.user.is_shopping_user:
		return PermissionDenied()
	orders = Order.objects.filter(shopping_user=ShoppingUser.objects.get(user=request.user)).order_by('-order_datetime')

	return render(request, 'kart/orders.html', {'orders': orders})