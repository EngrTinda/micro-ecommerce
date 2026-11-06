from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Product
from .models import Purchase

# Create your tests here.
class PurchaseFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="buyer")
        self.client.force_login(self.user)
        self.product = Product(
            user=self.user,
            name="Test product",
            handle="test-product",
            stripe_product_id="prod_test",
            stripe_price_id="price_test",
            stripe_price=999,
        )
        Product.objects.bulk_create([self.product])
        self.product = Product.objects.get(handle="test-product")

    @patch("purchases.views.stripe.checkout.Session.create")
    def test_canceling_checkout_returns_to_buy_page_without_ownership(
        self, create_checkout_session
    ):
        create_checkout_session.return_value = SimpleNamespace(
            id="cs_test", url="https://checkout.stripe.test/session"
        )

        response = self.client.post(
            reverse("purchases:start"), {"handle": self.product.handle}
        )

        self.assertRedirects(
            response,
            "https://checkout.stripe.test/session",
            fetch_redirect_response=False,
        )
        purchase = Purchase.objects.get()
        self.assertFalse(purchase.completed)
        create_checkout_session.assert_called_once()
        self.assertEqual(
            create_checkout_session.call_args.kwargs["cancel_url"],
            f"http://testserver{reverse('purchases:stopped')}",
        )

        response = self.client.get(reverse("purchases:stopped"))

        self.assertRedirects(
            response,
            reverse("products:detail", kwargs={"handle": self.product.handle}),
        )
        product_page = self.client.get(
            reverse("products:detail", kwargs={"handle": self.product.handle})
        )
        self.assertContains(product_page, "Buy Now")
        self.assertNotContains(product_page, "You own this product.")

    @patch("purchases.views.stripe.checkout.Session.create")
    def test_successful_checkout_marks_purchase_completed(self, create_checkout_session):
        create_checkout_session.return_value = SimpleNamespace(
            id="cs_test", url="https://checkout.stripe.test/session"
        )
        self.client.post(reverse("purchases:start"), {"handle": self.product.handle})

        response = self.client.get(reverse("purchases:success"))

        self.assertRedirects(
            response,
            reverse("products:detail", kwargs={"handle": self.product.handle}),
        )
        self.assertTrue(Purchase.objects.get().completed)
