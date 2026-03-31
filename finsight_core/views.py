from django.http import JsonResponse


def health(request):
    # Docker compose healthcheck expects a plain 200 response.
    return JsonResponse({"status": "ok"})

