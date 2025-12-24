from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.exceptions import ValidationError
from django.db import transaction

class Order(models.Model):
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    def save(self, *args, **kwargs):
        is_newly_paid = False
        if self.pk:
            old_status = Order.objects.get(pk=self.pk).is_paid
            if not old_status and self.is_paid:
                is_newly_paid = True
        with transaction.atomic():
            super().save(*args,**kwargs)
            if is_newly_paid:
                for item in self.items.all():
                    if item.quantity > item.product.stock:
                        raise ValidationError('Not enough stock for your order.')
                    item.product.stock -= item.quantity
                    item.product.save()
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False  # unit price snapshot
    )

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def clean(self):
        super().clean()
        if self.quantity > self.product.stock:
            raise ValidationError("Quantity exceeds stock.")
        if not self.product.is_active:
            raise ValidationError("Inactive product.")
        if self.order.is_paid:
            raise ValidationError('Can not modify items after payment.')

    def save(self, *args, **kwargs):
        self.price = self.product.price  # unit price snapshot
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.price * self.quantity

