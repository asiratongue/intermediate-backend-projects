from django.test import TestCase
from .models import URL
from django.urls import reverse


class URLShortenerTests(TestCase):
    def setUp(self):
        # Create a test URL object for use in tests
        self.test_url = URL.create_url(url="https://www.example.com/some/long/url")
        self.shortCode = self.test_url.shortCode  # Store the generated shortcode

    def test_create_valid_short_url(self):
        response = self.client.post(
            reverse('UrlShortenerAPP:shorten'), {"url": "https://www.validurl.com/another/long/url"}, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('shortCode', response.data)
        self.assertEqual(response.data['url'], "https://www.validurl.com/another/long/url")

    def test_retrieve_valid_short_url(self):
        response = self.client.get(f'/UrlShortenerAPI/shorten/{self.shortCode}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['url'], self.test_url.url)
        self.assertEqual(response.data['shortCode'], self.shortCode)

    def test_update_valid_short_url(self):
        updated_url = "https://www.updatedexample.com"
        response = self.client.put(f'/UrlShortenerAPI/shorten/{self.shortCode}/', {"url": updated_url}, content_type='application/json', format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['New_Url'], updated_url)
        self.assertEqual(response.data['shortCode'], self.shortCode)  # Ensure short code remains the same

    def test_delete_valid_short_url(self):
        response = self.client.delete(f'/UrlShortenerAPI/shorten/{self.shortCode}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(URL.objects.filter(shortCode=self.shortCode).exists())

    def test_get_url_statistics(self):
        response = self.client.get(f'/UrlShortenerAPI/shorten/{self.shortCode}/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['accessCount'], 0)  
        self.assertEqual(response.data['shortCode'], self.shortCode)
        self.assertEqual(response.data['url'], self.test_url.url)


class InvalidUrlsTest(TestCase):

    def setUp(self):
        testurl = "https://www.example.com/some/long/url"
        urltestobj = URL.create_url(url="https://www.example.com/some/long/url")


    def test_post_response(self):

        response = self.client.post('/UrlSortenerAPI/shorten/', {"url" : "https://www.example.com/some/long/url"}, format ='json')
        self.assertEqual(response.status_code, 404)

    def test_get_response(self):

        response = self.client.post('/UrlShortenerAPI/shorten/gj593h', format ='json')
        self.assertEqual(response.status_code, 301)


