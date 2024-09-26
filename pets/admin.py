from django.contrib import admin

from .models import Seller, Animal, Feedback, Wishlist

admin.site.register(Seller)
admin.site.register(Animal)
admin.site.register(Feedback)
admin.site.register(Wishlist)


