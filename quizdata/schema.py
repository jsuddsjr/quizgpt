from ninja import Field, Schema, ModelSchema
from typing import List, Optional
from .models import Topic, Question, Choice, QuestionBucket, AnswerHistory


class ChoiceSchema(ModelSchema):
    class Meta:
        model = Choice
        fields = "__all__"
        fields_optional = ["id"]


class QuestionSchema(ModelSchema):
    choices: List[ChoiceSchema] = Field(None, alias="choice_set")

    class Meta:
        model = Question
        fields = "__all__"
        fields_optional = ["id", "is_suppressed"]


class TopicSchema(ModelSchema):
    questions: List[ChoiceSchema] = Field(None, alias="question_set")

    class Meta:
        model = Topic
        fields = "__all__"
        fields_optional = ["id", "subtopic_of", "description"]


class ChoiceSchemaUpdate(ModelSchema):
    class Meta:
        model = Choice
        fields = "__all__"
        fields_optional = ["order", "is_correct"]
        exclude = ["id", "question", "created", "modified"]


class QuestionSchemaUpdate(ModelSchema):
    class Meta:
        model = Question
        fields = "__all__"
        fields_optional = ["is_suppressed", "choice_set"]
        exclude = ["id", "topic", "created", "modified"]


class TopicSchemaUpdate(ModelSchema):
    class Meta:
        model = Topic
        fields = "__all__"
        fields_optional = ["subtopic_of", "description", "questions"]
        exclude = ["id", "slug", "user", "created", "modified"]


class QuestionBucketSchema(ModelSchema):
    class Meta:
        model = QuestionBucket
        exclude = ["id"]


class AnswerHistorySchema(ModelSchema):
    class Meta:
        model = AnswerHistory
        exclude = ["id"]


class PostAnswerSchema(Schema):
    cid: str


class PostAnswerResponseSchema(Schema):
    correct: bool
    bucket: QuestionBucketSchema
    history: List[AnswerHistorySchema] = []


class GetAnswerResponseSchema(Schema):
    answers: List[AnswerHistorySchema] = []


class SuggestTopicQuerySchema(Schema):
    type: Optional[str] = "features or subtopics"
    level: Optional[int] = 0
    count: Optional[int] = 5


class SuggestQuestionResponseSchema(Schema):
    question: str
    answers: List[str]
    answer_index: int


class PostTopicResponseSchema(Schema):
    topic: TopicSchema
    subtopics: List[TopicSchema]


class ErrorMessage(Schema):
    error: str
    data: Optional[str] = None
