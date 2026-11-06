from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Product, ProductAttachment

# Create your tests here.
class ProductDetailTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="product-owner")
		self.product = Product.objects.create(
			user=self.user,
			name="Test product",
			handle="test-product",
			stripe_price=999,
		)

	def test_product_absolute_url_resolves(self):
		self.assertEqual(self.product.get_absolute_url(), "/products/test-product/")

	def test_product_detail_page_renders(self):
		response = self.client.get(reverse("products:detail", kwargs={"handle": self.product.handle}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.product.name)
		self.assertContains(response, str(self.product.price))

	def test_product_owner_sees_attachments_section(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("products:detail", kwargs={"handle": self.product.handle}))

		self.assertContains(response, "No attachments available.")

	def test_non_owner_sees_attachments_section(self):
		other_user = get_user_model().objects.create_user(username="other-user")
		self.client.force_login(other_user)
		response = self.client.get(reverse("products:detail", kwargs={"handle": self.product.handle}))

		self.assertContains(response, "No attachments available.")

	def test_manage_page_updates_existing_attachment(self):
		attachment = ProductAttachment.objects.create(
			product=self.product,
			file="products/test-product/attachments/manual.pdf",
			name="Old name",
		)
		self.client.force_login(self.user)

		response = self.client.post(
			reverse("products:manage", kwargs={"handle": self.product.handle}),
			{
				"name": self.product.name,
				"handle": self.product.handle,
				"price": str(self.product.price),
				"productattachment_set-TOTAL_FORMS": "1",
				"productattachment_set-INITIAL_FORMS": "1",
				"productattachment_set-MIN_NUM_FORMS": "0",
				"productattachment_set-MAX_NUM_FORMS": "1000",
				"productattachment_set-0-id": str(attachment.pk),
				"productattachment_set-0-file": attachment.file.name,
				"productattachment_set-0-name": "Updated name",
				"productattachment_set-0-is_free": "on",
				"productattachment_set-0-active": "on",
			},
		)

		self.assertRedirects(
			response,
			reverse("products:manage", kwargs={"handle": self.product.handle}),
		)
		attachment.refresh_from_db()
		self.assertEqual(attachment.name, "Updated name")

	def test_manage_page_renders_add_attachment_controls(self):
		self.client.force_login(self.user)
		response = self.client.get(
			reverse("products:manage", kwargs={"handle": self.product.handle})
		)

		self.assertContains(response, 'id="id_productattachment_set-TOTAL_FORMS"')
		self.assertContains(response, 'data-formset-prefix="productattachment_set"')
		self.assertContains(response, 'type="button" class="btn-submit mt-2" id="add-attachment-btn"')


class ProductCreateTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="product-creator")
		self.client.force_login(self.user)

	@patch("products.models.stripe.Price.create")
	@patch("products.models.stripe.Product.create")
	def test_create_product_uses_price_in_cents(
		self, stripe_product_create, stripe_price_create
	):
		stripe_product_create.return_value = SimpleNamespace(id="prod_test")
		stripe_price_create.return_value = SimpleNamespace(id="price_test")

		response = self.client.post(
			reverse("products:create"),
			{"name": "New product", "handle": "new-product", "price": "12.34"},
		)

		self.assertRedirects(
			response,
			reverse("products:manage", kwargs={"handle": "new-product"}),
		)
		stripe_price_create.assert_called_once_with(
			product="prod_test",
			unit_amount=1234,
			currency="usd",
		)
		product = Product.objects.get(handle="new-product")
		self.assertEqual(product.stripe_price, 1234)
