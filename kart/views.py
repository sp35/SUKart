from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import xlrd

from .forms import DeliveryAgentSignUpForm, ShoppingUserSignUpForm, SearchForm, AddComplaintForm
from .models import Product, ShoppingUser, DeliveryAgent, Order, Complaint, Company
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
	elif request.user.is_superuser:
		return render(request, 'kart/admin_home.html')
	return redirect('login')


@login_required
def view_product(request, pk):
	if not request.user.is_shopping_user:
		return PermissionDenied()
	product = Product.objects.get(pk=pk)
	currency = ShoppingUser.objects.get(user=request.user).currency
	return render(request, "kart/product_detail.html", {'product': product, "currency": currency})


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
		# delivery agent algorithm
		delivery_agents = DeliveryAgent.objects.filter(user__state=request.user.state)
		if len( delivery_agents.filter(user__city=request.user.city) ):
			delivery_agents = delivery_agents.filter(user__city=request.user.city)
			d_dict = { delivery_agent: len( Order.objects.filter(delivery_agent=delivery_agent, delivered=False) ) for delivery_agent in delivery_agents }
			sorted_d_dict = {}
			for k in sorted(d_dict, key=lambda k: d_dict[k]):
				sorted_d_dict[k] = d_dict[k]
			d_dict = sorted_d_dict
			delivery_agents = list(d_dict.keys())
		else:
			delivery_agents = delivery_agents.exclude(user__city=request.user.city)
			d_dict = { delivery_agent: len( Order.objects.filter(delivery_agent=delivery_agent, delivered=False) ) for delivery_agent in delivery_agents }
			sorted_d_dict = {}
			for k in sorted(d_dict, key=lambda k: d_dict[k]):
				sorted_d_dict[k] = d_dict[k]
			d_dict = sorted_d_dict
			delivery_agents = list(d_dict.keys())

		if len(delivery_agents):
			delivery_agent = delivery_agents[0]
			Order.objects.create(product=product, shopping_user=shopping_user, delivery_agent=delivery_agent)
			shopping_user.currency -= product.price
			shopping_user.save()
			messages.success(request, "Ordered Successfully")
			return redirect('home')
		else:
			messages.error(request, "Error: No delivery agent found for this order")
	return redirect('view-product', pk=pk)


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


@login_required
def add_complaint(request, pk):
	if not request.user.is_shopping_user:
		return PermissionDenied()
	try:
		order = Order.objects.get(pk=pk)
	except Order.DoesNotExist:
		return HttpResponse("Order Does Not Exist")
	if request.method == 'POST':
		form = AddComplaintForm(request.POST)
		if form.is_valid():
			content = form.cleaned_data['content']
			Complaint.objects.create(order=order, content=content)
			return redirect('view-order', pk=pk)
	else:
		form = AddComplaintForm()

	return render(request, 'kart/complaint_form.html', {'form': form, 'pk': pk})


@login_required
def view_order_complaints(request, pk):
	if not request.user.is_shopping_user:
		return PermissionDenied()
	try:
		order = Order.objects.get(pk=pk)
	except Order.DoesNotExist:
		return HttpResponse("Order Does Not Exist")
	complaints = Complaint.objects.filter(order=order).order_by('-complaint_datetime')

	return render(request, 'kart/order_complaints.html', {'complaints': complaints})


@login_required
def cancel_order(request, pk):
	if not request.user.is_shopping_user:
		return PermissionDenied()
	try:
		order = Order.objects.get(pk=pk)
		if not order.delivered:
			order.delete()
			messages.success(request, "Order Cancelled")
			return redirect('home')
		else:
			messages.error(request, "Order can't be cancelled now")
			return redirect('view-order', pk=pk)
	except Order.DoesNotExist:
		return HttpResponse("Order Does Not Exist")


@login_required
def populate_products(request):
	if not request.user.is_superuser:
		return PermissionDenied()
	if request.method == "GET":
		return render(request, 'kart/admin_home.html')
	else:
		excel_file = request.FILES['excel_file']
		wb = xlrd.open_workbook(file_contents=excel_file.read())
		sheet = wb.sheet_by_index(0)
		excel_data = []
		for row in range(sheet.nrows):
			row_data = []
			for col in range(sheet.ncols):
				if sheet.cell(row, col).ctype == xlrd.XL_CELL_NUMBER:
					row_data.append(int(sheet.cell_value(row, col)))
				else:
					row_data.append(str(sheet.cell_value(row, col)))
			excel_data.append(row_data)
		for row in excel_data[1:]:
			company, created = Company.objects.get_or_create(name=row[4])
			Product.objects.get_or_create(title=row[1], description=row[2], price=int(row[3]), company=company)

	return render(request, 'kart/admin_home.html', {"excel_data": excel_data})