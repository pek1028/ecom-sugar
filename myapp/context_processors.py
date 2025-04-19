# myapp/context_processors.py
def cart_item_count(request):
    cart = request.session.get('cart', {})
    return {'cart_item_count': sum(cart.values()) if cart else 0}