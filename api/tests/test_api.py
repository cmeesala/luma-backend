from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .factories import IntentFactory, InteractionEventFactory, GroupedIntentFactory, BillFactory
from api.services import bills_repository, intents_repository, grouped_intents_repository, interaction_events_repository

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Clear all repositories before each test
        bills_repository.clear()
        intents_repository.clear()
        grouped_intents_repository.clear()
        interaction_events_repository.clear()

    def test_health_check(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'healthy'})

    def test_record_intent(self):
        data = {
            'intent_text': 'test intent',
            'interaction_events': [
                {'event_type': 'click', 'timestamp': '2024-01-01T00:00:00Z'},
                {'event_type': 'scroll', 'timestamp': '2024-01-01T00:00:01Z'}
            ]
        }
        response = self.client.post(reverse('record_intent'), data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['intent_text'], 'test intent')
        self.assertEqual(len(response.data['interaction_events']), 2)

    def test_get_interactions(self):
        # First create an intent with interactions
        data = {
            'intent_text': 'test intent',
            'interaction_events': [
                {'event_type': 'click', 'timestamp': '2024-01-01T00:00:00Z'}
            ]
        }
        self.client.post(reverse('record_intent'), data, format='json')

        # Then test getting the interactions
        response = self.client.get(reverse('get_interactions'), {'intent_text': 'test intent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event_type'], 'click')

    def test_get_bills_found(self):
        # Create a bill
        bill = BillFactory.create()
        bills_repository[bill['user_id']] = bill

        response = self.client.get(reverse('get_bills'), {'user_id': bill['user_id']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_id'], bill['user_id'])

    def test_get_bills_not_found(self):
        response = self.client.get(reverse('get_bills'), {'user_id': 'non_existent'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'No bills found for this user')

    def test_get_bills_missing_param(self):
        response = self.client.get(reverse('get_bills'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'user_id is required')

    def test_create_bill(self):
        data = {
            'user_id': 'test_user',
            'electricity_bill': 100.50,
            'water_bill': 50.25,
            'internet_bill': 75.00,
            'phone_bill': 45.75
        }
        response = self.client.post(reverse('create_bill'), data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user_id'], 'test_user')
        self.assertEqual(response.data['electricity_bill'], '100.50')
        self.assertEqual(response.data['water_bill'], '50.25')
        self.assertEqual(response.data['internet_bill'], '75.00')
        self.assertEqual(response.data['phone_bill'], '45.75')

    def test_record_intent_missing_text(self):
        data = {
            'interaction_events': [
                {
                    'event_type': 'click',
                    'timestamp': '2024-01-01T00:00:00Z',
                    'view_id': 123,
                    'view_resource_name': 'test_button',
                    'screen_name': 'TestScreen',
                    'action_type': 'CLICK'
                }
            ]
        }
        response = self.client.post(reverse('record_intent'), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'intent_text is required')

    def test_get_interactions_found(self):
        # Create test data
        intent_text = "test intent"
        events = [
            {
                'event_type': 'click',
                'timestamp': '2024-01-01T00:00:00Z',
                'view_id': 123,
                'view_resource_name': 'test_button',
                'screen_name': 'TestScreen',
                'action_type': 'CLICK'
            }
        ]
        
        # Create a grouped intent with the events
        grouped_intent = GroupedIntentFactory.create(
            intent_text=intent_text,
            interaction_events=events
        )
        grouped_intents_repository[str(grouped_intent['id'])] = grouped_intent
        
        # Get interactions
        response = self.client.get(reverse('get_interactions'), {'intent_text': intent_text})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, events)

    def test_get_interactions_not_found(self):
        response = self.client.get(reverse('get_interactions'), {'intent_text': 'non-existent'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'No interactions found for this intent')

    def test_get_interactions_missing_param(self):
        response = self.client.get(reverse('get_interactions'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'intent_text is required') 