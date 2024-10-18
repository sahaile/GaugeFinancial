from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Bankstatements(models.Model):
   bankstatementID = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=100)
   account = models.CharField(max_length=100)
   start_period = models.DateField()
   end_period = models.DateField()
   file = models.FileField(upload_to='bank_statements/')
   upload_date = models.DateTimeField(auto_now_add=True)
   created_by = models.ForeignKey(User, on_delete=models.CASCADE)
   class Meta:
        verbose_name_plural = 'Bankstatements'




class Transactions(models.Model):
   transactionID = models.IntegerField(primary_key=True)
   bankstatementID = models.ForeignKey(Bankstatements, on_delete=models.CASCADE)
   date = models.DateField()
   revenue = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
   expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
   description = models.CharField(max_length=100)
   category = models.CharField(max_length=100, default='uncategorized') 



   class Meta:
        verbose_name_plural = 'Transactions'


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'
   

