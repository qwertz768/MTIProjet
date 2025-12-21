from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'core/templates/core/home.html')