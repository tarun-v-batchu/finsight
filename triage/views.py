from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import SupportCase
from .ml_service import MLTriageService
from .serializers import SupportCaseSerializer
import os

ml_service = MLTriageService(openai_api_key=os.getenv('OPENAI_API_KEY'))

class SupportCaseViewSet(viewsets.ModelViewSet):
    queryset = SupportCase.objects.all()
    serializer_class = SupportCaseSerializer
    
    def create(self, request):
        description = request.data.get('description')
        if not description or not isinstance(description, str):
            return Response(
                {"detail": "Field 'description' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        case_type, confidence = ml_service.hybrid_predict(description)
        
        case = SupportCase.objects.create(
            description=description,
            predicted_case_type=case_type,
            confidence_score=confidence
        )
        
        return Response({
            'case_id': case.case_id,
            'predicted_type': case_type,
            'confidence': confidence
        }, status=status.HTTP_201_CREATED)