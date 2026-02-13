
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Category
# Create your views here.

# def index(request):
    
#     categories = [
#         {"id": 1, "name": "Electronics"},
#         {"id": 2, "name": "Clothes"},
#         {"id": 3, "name": "Books"},
#         {"id": 4, "name": "Sports"},
#         {"id": 5, "name": "Home"},
#     ]

#     context={
#         'cat':categories
#     }

#     return render(request,'category/index.html',context)

def index(request):

    categories=Category.objects.all()

    context={
        'cat':categories
    }

    return render(request,'category/index.html',context)
