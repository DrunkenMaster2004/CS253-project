from .models import Cart

def cart_items_count(request):
    if request.user.is_authenticated:
        return {'cart_items_count': Cart.objects.filter(user=request.user).count()}
    return {'cart_items_count': 0}