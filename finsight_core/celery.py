import os
from celery import Celery
from triage.ml_service import MLTriageService

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finsight_core.settings')
app = Celery('finsight_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = 'redis://localhost:6379/0'

ml_service = MLTriageService(openai_api_key=os.getenv('OPENAI_API_KEY'))

@app.task
def process_batch_triage(case_descriptions):
    results = []
    for desc in case_descriptions:
        case_type, confidence = ml_service.hybrid_predict(desc)
        results.append({
            'description': desc,
            'predicted_type': case_type,
            'confidence': confidence
        })
    return results