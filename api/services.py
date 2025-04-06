from datetime import datetime
from typing import Dict, List, Optional
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

def are_intents_similar(intent1: str, intent2: str) -> bool:
    """Use OpenAI to determine if two intents are similar"""
    try:
        logger.info(f"Checking similarity between intents: '{intent1}' and '{intent2}'")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that determines if two user intents are similar. Respond with only 'true' or 'false'."},
                {"role": "user", "content": f"Are these intents similar? Intent 1: '{intent1}' Intent 2: '{intent2}'"}
            ],
            temperature=0.1,
            max_tokens=10
        )
        result = response.choices[0].message.content.strip().lower() == 'true'
        logger.info(f"OpenAI Response for similarity check: {response.choices[0].message.content}")
        logger.info(f"Similarity result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error checking intent similarity: {e}")
        return False

def find_most_similar_intent(target_intent: str) -> Optional[dict]:
    """Find the most similar grouped intent using LLM"""
    if not grouped_intents_repository:
        logger.info("No grouped intents available for comparison")
        return None

    # First try exact match
    for grouped_intent in grouped_intents_repository.values():
        if grouped_intent['intent_text'] == target_intent:
            logger.info(f"Found exact match for intent: '{target_intent}'")
            return grouped_intent

    # If no exact match, use LLM to find the most similar
    try:
        # Create a prompt with all available intents
        intents_list = [intent['intent_text'] for intent in grouped_intents_repository.values()]
        logger.info(f"Finding most similar intent to '{target_intent}' among: {intents_list}")
        
        prompt = f"""Given the target intent: '{target_intent}'
And these available intents: {', '.join(intents_list)}
Which intent is most similar to the target intent? Return only the exact matching intent text."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that finds the most similar intent from a list. Return only the exact matching intent text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=50
        )

        matched_intent_text = response.choices[0].message.content.strip()
        logger.info(f"OpenAI suggested most similar intent: '{matched_intent_text}'")
        
        # Find the grouped intent with the matched text
        for grouped_intent in grouped_intents_repository.values():
            if grouped_intent['intent_text'] == matched_intent_text:
                logger.info(f"Found matching grouped intent for '{matched_intent_text}'")
                return grouped_intent

        logger.warning(f"OpenAI suggested intent '{matched_intent_text}' not found in repository")
        return None
    except Exception as e:
        logger.error(f"Error finding similar intent: {e}")
        return None

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
        logger.info(f"Created new intent with ID {intent_id}: '{intent_text}'")

        # Store interaction events
        interaction_events_repository[intent_id] = interaction_events

        # Find similar intent using LLM
        similar_intent = find_most_similar_intent(intent_text)

        if similar_intent:
            # Update existing grouped intent
            similar_intent['count'] += 1
            # TODO: Consider whether to extend interaction events or keep them separate
            # similar_intent['interaction_events'].extend(interaction_events)
            logger.info(f"Updated existing grouped intent '{similar_intent['intent_text']}' with new interactions")
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
            logger.info(f"Created new grouped intent with ID {grouped_intent_id}: '{intent_text}'")

        return intent

    @staticmethod
    def get_interactions(intent_text: str) -> Optional[List[dict]]:
        """
        Returns interaction events for a given intent text.
        Uses LLM to find the most similar grouped intent and returns its events.
        """
        logger.info(f"Searching for interactions with intent: '{intent_text}'")
        # Find the most similar grouped intent
        similar_intent = find_most_similar_intent(intent_text)
        if similar_intent:
            logger.info(f"Found similar intent: '{similar_intent['intent_text']}'")
            return similar_intent['interaction_events']
        logger.info(f"No similar intent found for: '{intent_text}'")
        return None 