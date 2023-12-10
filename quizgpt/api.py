from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from ninja import NinjaAPI, ModelSchema, Schema, Path
from ninja.security import django_auth, django_auth_superuser

from quizdata.api import router as quizdata_router
from chatapi.api import router as chatapi_router

api = NinjaAPI(
    csrf=True,
    title="QuizGPT API",
    version="0.1.0",
    urls_namespace="quizgpt",
)

api.add_router("/quizdata", quizdata_router, tags=["quizdata"])
api.add_router("/chatapi", chatapi_router, tags=["chatapi"])


class UserSchema(ModelSchema):
    class Meta:
        model = User
        model_exclude = ["password", "last_login", "user_permissions"]


class ErrorSchema(Schema):
    message: str


@api.get(
    "/me",
    auth=django_auth,
    tags=["user"],
    summary=_("Retrieve the logged in user"),
    response={200: UserSchema, 403: ErrorSchema}
)
def me(request):
    if not request.user.is_authenticated:
        return 403, {"message": _("Please sign in first")}
    return request.user

@api.post(
    "/user",
    auth=django_auth_superuser,
    tags=["user"],
    summary=_("Add a new user to the database"),
    response={200: UserSchema, 403: ErrorSchema}
)
def create_user(request, user: UserSchema):
    try:
        user = User.objects.create_user(**user.dict())
        return {id: user.id}
    except Exception as e:
        return 403, {"message": str(e)}


##! NOTE: All of the following imports are for the example code only.

# class HelloSchema(Schema):
#     name: str = "world"


# @api.get("/hello")
# def hello_get(request, name: str):
#     return f"Hello {name}"


# @api.post("/hello")
# def hello_post(request, data: HelloSchema):
#     return f"Hello {data.name}"


# @api.get("/math")
# def math(request, a: int, b: int):
#     return {"add": a + b, "multiply": a * b}


# @api.get("/math/{a}and{b}")
# def math_path(request, a: int, b: int):
#     return {"add": a + b, "multiply": a * b}


# @api.get("/dir/{path:value}")
# def get_path(request, value: str):
#     return value


# class PathDate(Schema):
#     year: int
#     month: int
#     day: int

#     def value(self):
#         return datetime.date(self.year, self.month, self.day)


# @api.get("/events/{year}/{month}/{day}")
# def events(request, date: PathDate = Path(...)):
#     return {"date": date.value(), "dateParts": [date.year, date.month, date.day]}
