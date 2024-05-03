from django.http import HttpResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

api = NinjaAPI(csrf=True)


@api.post("/csrftoken")
@ensure_csrf_cookie
@csrf_exempt
def get_csrf_token(request):
    return HttpResponse()


api.add_router("/accounts/", "account.api.router")
api.add_router("/", "store.api.router")


@api.exception_handler(ValidationError)
def validation_errors(request, exc: ValidationError):
    errors = {}
    for error in exc.errors:
        msg = error["msg"].split(",")[-1]
        msg = msg.strip()
        field = error["loc"][-1]
        errors[field] = msg

    msg = {"error": "Invalid input", "details": errors}
    return api.create_response(request, msg, status=400)
