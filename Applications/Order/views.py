from django.shortcuts import render

# Create your views here.


def take_order(request):
    return render(request, 'Order/take_order.html')
