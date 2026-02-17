from django.http import JsonResponse

def root(request):
    return JsonResponse({"app": "DAASOM", "status": "running"})