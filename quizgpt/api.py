from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from ninja import NinjaAPI, ModelSchema, Schema, Path

from quizdata.api import router as quizdata_router
from chatapi.api import router as chatapi_router

api = NinjaAPI(
    csrf=True,
    docs_decorator=staff_member_required,
    title="QuizGPT API",
    urls_namespace="quizgpt",
)

api.add_router("/quizdata", quizdata_router)
api.add_router("/chatapi", chatapi_router)


class UserSchema(ModelSchema):
    class Config:
        model = User
        model_exclude = ["password", "last_login", "user_permissions"]


class ErrorSchema(Schema):
    message: str


@api.get("/me", response={200: UserSchema, 403: ErrorSchema})
def me(request):
    if not request.user.is_authenticated:
        return 403, {"message": "Please sign in first"}
    return request.user


@api.post("/user", response={200: UserSchema, 403: ErrorSchema})
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
