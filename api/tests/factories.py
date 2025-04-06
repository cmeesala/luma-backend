from datetime import datetime

class IntentFactory:
    @staticmethod
    def create(**kwargs):
        return {
            'id': kwargs.get('id', 1),
            'intent_text': kwargs.get('intent_text', 'test intent'),
            'interaction_events': kwargs.get('interaction_events', [])
        }

class InteractionEventFactory:
    @staticmethod
    def create(**kwargs):
        return {
            'event_type': kwargs.get('event_type', 'click'),
            'timestamp': kwargs.get('timestamp', datetime.now().isoformat()),
            'view_id': kwargs.get('view_id', 123),
            'view_resource_name': kwargs.get('view_resource_name', 'test_button'),
            'screen_name': kwargs.get('screen_name', 'TestScreen'),
            'action_type': kwargs.get('action_type', 'CLICK')
        }

class GroupedIntentFactory:
    @staticmethod
    def create(**kwargs):
        return {
            'id': kwargs.get('id', 1),
            'intent_text': kwargs.get('intent_text', 'test intent'),
            'count': kwargs.get('count', 1),
            'interaction_events': kwargs.get('interaction_events', [])
        }

class BillFactory:
    @staticmethod
    def create(**kwargs):
        return {
            'user_id': kwargs.get('user_id', 'test_user'),
            'electricity_bill': str(kwargs.get('electricity_bill', 100.00)),
            'water_bill': str(kwargs.get('water_bill', 50.00)),
            'internet_bill': str(kwargs.get('internet_bill', 75.00)),
            'phone_bill': str(kwargs.get('phone_bill', 60.00))
        } 