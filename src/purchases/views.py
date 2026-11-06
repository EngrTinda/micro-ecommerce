import random
from django.urls import reverse
import stripe
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render

from products.models import Product
from .models import Purchase
# Create your views here.

from cfehome.env import config

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default=None)
stripe.api_key = STRIPE_SECRET_KEY

def purchase_start_view(request):
    if not request.method == "POST":
        return HttpResponseBadRequest()
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    handle = request.POST.get("handle")
    obj = Product.objects.get(handle=handle)
    stripe_price_id = obj.stripe_price_id
    if stripe_price_id is None:
        return HttpResponseBadRequest()
    purchase = Purchase.objects.create(
        user=request.user, product=obj)
    request.session["purchase_id"] = purchase.id




    success_path = reverse("purchases:success")
    cancel_path = reverse("purchases:stopped")
    success_url = request.build_absolute_uri(success_path)
    cancel_url = request.build_absolute_uri(cancel_path)
    print(success_url, cancel_url)
    checkout_session = stripe.checkout.Session.create (
        line_items=[
            {
                "price": stripe_price_id,
                "quantity": 1,

            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    purchase.stripe_checkout_session_id = checkout_session.id
    purchase.save()
    return HttpResponseRedirect(checkout_session.url)



    # number = random.randint(0, 1)
    # if number == 1:
    #     return HttpResponseRedirect("/purchases/success/")
    # return HttpResponseRedirect("/purchases/stopped/")
    # return HttpResponse("started")


def purchase_success_view(request):
    purchase_id = request.session.get("purchase_id")
    if purchase_id:

        purchase = Purchase.objects.get(id=purchase_id)
        purchase.completed = True
        purchase.save()
        del request.session['purchase_id']
        return HttpResponseRedirect(purchase.product.get_absolute_url())
    

    return HttpResponse(f"Finished {purchase_id}")


def purchase_stopped_view(request):
    purchase_id = request.session.get("purchase_id")
    if purchase_id:
        purchase = Purchase.objects.get(id=purchase_id)
        product = purchase.product
        del request.session['purchase_id']
        return HttpResponseRedirect(product.get_absolute_url())
    
    return HttpResponse("stopped")