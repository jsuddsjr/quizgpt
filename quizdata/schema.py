from ninja import Schema, ModelSchema
from typing import List
from .models import Topic, Question, Choice, QuestionBucket, AnswerHistory


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

class GetAnswerResponseSchema(Schema):
    answers: List[AnswerHistorySchema] = []

class PostTopicSchema(Schema):
    topic: str
    slug: str = ""
    subtopic_of: str = ""
    type: str = ""
    level: int = 0
    count: int = 5


class PostTopicResponseSchema(Schema):
    topic: TopicSchema
    subtopics: List[TopicSchema]


class ErrorMessage(Schema):
    error: str
    data: str = None



class PostQuestionResponseSchema(Schema):
    topic_id: int
    questions: List[int] = []
