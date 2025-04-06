from datetime import datetime
from typing import Dict, List, Optional

# In-memory repositories
bills_repository: Dict[str, dict] = {}
intents_repository: Dict[int, dict] = {}
grouped_intents_repository: Dict[str, dict] = {}
interaction_events_repository: Dict[int, List[dict]] = {}

def get_bills(user_id: str) -> Optional[dict]:
    """Get bills for a specific user"""
    return bills_repository.get(user_id)

def create_bill(user_id: str, electricity_bill: float = 0, water_bill: float = 0,
               internet_bill: float = 0, phone_bill: float = 0) -> dict:
    """Create a new bill for a user"""
    bill = {
        'user_id': user_id,
        'electricity_bill': f"{float(electricity_bill):.2f}",
        'water_bill': f"{float(water_bill):.2f}",
        'internet_bill': f"{float(internet_bill):.2f}",
        'phone_bill': f"{float(phone_bill):.2f}"
    }
    bills_repository[user_id] = bill
    return bill

class IntentService:
    @staticmethod
    def create_intent(intent_text: str, interaction_events: List[dict]) -> dict:
        # Create intent
        intent_id = len(intents_repository) + 1
        intent = {
            'id': intent_id,
            'intent_text': intent_text,
            'interaction_events': interaction_events
        }
        intents_repository[intent_id] = intent

        # Store interaction events
        interaction_events_repository[intent_id] = interaction_events

        # Check for similar intents and group them
        similar_intent = None
        for grouped_intent in grouped_intents_repository.values():
            if grouped_intent['intent_text'] == intent_text:
                similar_intent = grouped_intent
                break

        if similar_intent:
            # Update existing grouped intent
            similar_intent['count'] += 1
            similar_intent['interaction_events'].extend(interaction_events)
        else:
            # Create new grouped intent
            grouped_intent_id = len(grouped_intents_repository) + 1
            grouped_intent = {
                'id': grouped_intent_id,
                'intent_text': intent_text,
                'count': 1,
                'interaction_events': interaction_events.copy()
            }
            grouped_intents_repository[str(grouped_intent_id)] = grouped_intent

        return intent

    @staticmethod
    def get_interactions(intent_text: str) -> Optional[List[dict]]:
        """
        Returns interaction events for a given intent text.
        First checks if the intent is part of a GroupedIntent, if so returns those events.
        Otherwise returns not found.
        """
        for grouped_intent in grouped_intents_repository.values():
            if grouped_intent['intent_text'] == intent_text:
                return grouped_intent['interaction_events']
        return None 