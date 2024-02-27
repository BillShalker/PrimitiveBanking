from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])


class Transaction(models.Model):
    from_account = models.ForeignKey(Account, related_name='outgoing_transactions', on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, related_name='incoming_transactions', on_delete=models.CASCADE)
    amount = models.FloatField(validators=[MinValueValidator(0.01)])
    timestamp = models.DateTimeField(auto_now_add=True)

# Create your models here.
