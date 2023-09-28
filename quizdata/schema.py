from django.contrib.auth.models import User
from ninja import Schema, ModelSchema
from typing import List
from .models import Topic, Question, Choice, QuestionBucket, AnswerHistory


class UserSchema(ModelSchema):
    class Config:
        model = User
        model_exclude = ["password", "last_login", "user_permissions"]


class ErrorSchema(Schema):
    message: str


class TopicSchema(ModelSchema):
    class Config:
        model = Topic
        model_fields = "__all__"
        model_fields_optional = ["id", "subtopic_of", "description"]


class QuestionSchema(ModelSchema):
    class Config:
        model = Question
        model_fields = "__all__"
        model_fields_optional = ["id", "is_suppressed"]


class ChoiceSchema(ModelSchema):
    class Config:
        model = Choice
        model_fields = "__all__"
        model_fields_optional = ["id"]


class QuestionBucketSchema(ModelSchema):
    class Config:
        model = QuestionBucket
        model_exclude = ["id"]


class AnswerHistorySchema(ModelSchema):
    class Config:
        model = AnswerHistory
        model_exclude = ["id"]


class PostAnswerSchema(Schema):
    cid: str


class PostAnswerResponseSchema(Schema):
    correct: bool
    bucket: QuestionBucketSchema
    history: List[AnswerHistorySchema] = []


class PostTopicSchema(Schema):
    topic: str
    type: str
    level: int
    count: int


class PostTopicResponseSchema(Schema):
    created: bool
    subtopics: List[TopicSchema] = []
