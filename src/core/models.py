from tortoise import fields
from tortoise.models import Model
from src.core.vote_outcome import VoteOutcome

class Model(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    modelfile = fields.TextField()
    
    class Meta:
        table = "models"

class Vote(Model):
    id = fields.IntField(pk=True)
    model_a = fields.ForeignKeyField('models.Model', related_name='votes_as_a')
    model_b = fields.ForeignKeyField('models.Model', related_name='votes_as_b')
    outcome = fields.IntEnumField(VoteOutcome)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "votes"

class Message(Model):
    id = fields.IntField(pk=True)
    vote = fields.ForeignKeyField('models.Vote', related_name='messages')
    model = fields.ForeignKeyField('models.Model', related_name='messages')
    content = fields.TextField()
    is_user = fields.BooleanField()
    timestamp = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "messages"
