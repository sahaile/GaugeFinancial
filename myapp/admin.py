from django.contrib import admin
from .models import Bankstatements, Transactions, Chat

admin.site.register(Chat)
admin.site.register(Bankstatements)
admin.site.register(Transactions)

