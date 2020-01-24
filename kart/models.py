from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image

from . import options


class User(AbstractUser):
	name = models.CharField(max_length=50)
	email = models.EmailField(unique=True)
	dob = models.DateField(null=True)
	state = models.IntegerField(choices=options.STATE_CHOICES, null=True)
	city = models.CharField(max_length=20, null=True)
	is_delivery_agent = models.BooleanField(default=False)
	is_shopping_user = models.BooleanField(default=False)


class DeliveryAgent(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.user.username


class ShoppingUser(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	currency = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.user.username


class Company(models.Model):
	name = models.CharField(max_length=20)

	def __str__(self):
		return self.name


class Product(models.Model):
	title = models.CharField(max_length=20)
	image = models.ImageField(default='default_product.png', upload_to='product_pics')
	description = models.TextField(max_length=250)
	price = models.PositiveIntegerField()
	company = models.ForeignKey(Company, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.title} by {self.company.name}"

	def save(self, *args, **kwargs):
		super().save()
		img = Image.open(self.image.path)
		if img.height > 300 or img.width > 300:
			output_size = (300,300)
			img.thumbnail(output_size)
			img.save(self.image.path)


class Order(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	shopping_user = models.ForeignKey(ShoppingUser, on_delete=models.CASCADE)
	delivery_agent = models.ForeignKey(DeliveryAgent, on_delete=models.CASCADE)
	order_datetime = models.DateTimeField(auto_now_add=True)			# when order is placed
	delivered_datetime = models.DateTimeField(default=None, null=True)	# when order is delivered
	accepted = models.BooleanField(default=False)	# true if accepted by the delivery agent
	arrived = models.BooleanField(default=False)	# true if product has arrived the delivery agent's location
	delivered = models.BooleanField(default=False)	# true if delivered to the shopping user

	def __str__(self):
		return f"{self.shopping_user.user.username}"


class Complaint(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	content = models.TextField(max_length=200)
	complaint_datetime = models.DateTimeField(auto_now_add=True)
	is_resolved = models.BooleanField(default=False)	# true if shopping user's complaint is resolved

	def __str__(self):
		return f"from {self.order.shopping_user.user.username}"