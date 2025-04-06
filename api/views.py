from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import get_bills, create_bill, IntentService

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'})

@api_view(['POST'])
def record_intent(request):
    intent_text = request.data.get('intent_text')
    interaction_events = request.data.get('interaction_events', [])
    
    if not intent_text:
        return Response({'error': 'intent_text is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    intent = IntentService.create_intent(intent_text, interaction_events)
    return Response(intent, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_interactions(request):
    intent_text = request.query_params.get('intent_text')
    if not intent_text:
        return Response({'error': 'intent_text is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    interactions = IntentService.get_interactions(intent_text)
    if not interactions:
        return Response({'error': 'No interactions found for this intent'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(interactions)

@api_view(['GET'])
def get_bills_view(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    bills = get_bills(user_id)
    if not bills:
        return Response({'error': 'No bills found for this user'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(bills)

@api_view(['POST'])
def create_bill_view(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    bill = create_bill(
        user_id=user_id,
        electricity_bill=request.data.get('electricity_bill', 0),
        water_bill=request.data.get('water_bill', 0),
        internet_bill=request.data.get('internet_bill', 0),
        phone_bill=request.data.get('phone_bill', 0)
    )
    return Response(bill, status=status.HTTP_201_CREATED)
