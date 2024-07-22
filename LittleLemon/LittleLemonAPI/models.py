from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    inventory = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}"
    

class CartItem(models.Model):
    browser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='browser')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('browser', 'item')

    def __str__(self):
        return f"{self.item} for {self.browser.id}"


class Order(models.Model):
    class statusCodes(models.IntegerChoices):
       PENDING = 0, 'Pending',
       ASSIGNED = 1, 'Assigned',
       ENROUTE = 2, 'En route',
       DELIVERED = 3, 'Delivered'

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer', null=True)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.IntegerField(default=statusCodes.PENDING, choices=statusCodes.choices)
    driver = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='driver', blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"
    

class OrderItem(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='menu_item')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name = 'items_for_order')
    quantity = models.IntegerField(default=1)
    

    # class Meta:
    #     unique_together = ('item', 'order')
    
    


