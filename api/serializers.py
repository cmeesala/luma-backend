from rest_framework import serializers
from .models import Intent, InteractionEvent, Bill

class InteractionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionEvent
        fields = ['timestamp', 'view_id', 'view_resource_name', 'screen_name', 'action_type']

class IntentSerializer(serializers.ModelSerializer):
    interaction_events = InteractionEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Intent
        fields = ['intent_id', 'intent_text', 'interaction_events', 'created_at', 'is_grouped', 'grouped_intent']
        read_only_fields = ['intent_id', 'created_at', 'is_grouped', 'grouped_intent']

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ['user_id', 'electricity_bill', 'water_bill', 'internet_bill', 'phone_bill', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 