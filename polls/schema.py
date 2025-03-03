"""GraphQL schema for the polls management system, defining types, queries, and mutations."""

from django.core.exceptions import ObjectDoesNotExist, ValidationError
import graphene
from graphene_django import DjangoObjectType
from polls.models import Question, Response, Choice


class ChoiceType(DjangoObjectType):
    """GraphQL type representing a choice in a poll."""
    class Meta:
        model = Choice


class ResponseType(DjangoObjectType):
    """GraphQL type representing a response to a poll question."""
    class Meta:
        model = Response


class QuestionType(DjangoObjectType):
    """GraphQL type representing a poll question."""
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'pub_date', 'edit_date', 'responses', 'choices',
                 'question_type')


class CreatePoll(graphene.Mutation):
    """Mutation to create a new poll with optional choices."""
    class Arguments:
        """Arguments for creating a poll."""
        question = graphene.String(required=True)
        question_type = graphene.String(required=True)
        choices = graphene.List(graphene.String)

    id = graphene.ID()
    pub_date = graphene.DateTime()
    question_text = graphene.String()
    edit_date = graphene.DateTime()
    question_type = graphene.String()
    choices = graphene.List(ChoiceType)

    def mutate(self, _info, question, question_type, choices=None):
        """Create a new poll with the given question text and type."""
        print(question)
        if question_type == Question.MULTIPLE_CHOICE and (not choices or len(choices) < 2):
            raise ValidationError('Multiple choice questions must have at least 2 choices')

        q = Question.objects.create(
            question_text=question,
            question_type=question_type
        )

        if choices:
            for choice_text in choices:
                q.choices.create(choice_text=choice_text)

        return CreatePoll(
            id=q.id,
            pub_date=q.pub_date,
            question_text=q.question_text,
            edit_date=q.edit_date,
            question_type=q.question_type,
            choices=q.choices.all()
        )


class UpdatePoll(graphene.Mutation):
    """Mutation to update an existing poll's text, type, and choices."""
    class Arguments:
        """Arguments for updating a poll."""
        question_id = graphene.ID(required=True)
        question = graphene.String()
        question_type = graphene.String()
        choices = graphene.List(graphene.String)

    id = graphene.ID()
    question_text = graphene.String()
    edit_date = graphene.DateTime()
    question_type = graphene.String()
    choices = graphene.List(ChoiceType)

    def mutate(self, _info, question_id, question=None, question_type=None, choices=None):
        """Update a poll with new text, type, and/or choices."""
        try:
            q = Question.objects.get(pk=question_id)
            if question:
                q.question_text = question
   
            if question_type:
                if question_type == Question.MULTIPLE_CHOICE:
                    if not choices or len(choices) < 2:
                        raise ValidationError('Multiple choice questions must have at least 2 choices')
                    
                    q.choices.all().delete()
                    
                    for choice_text in choices:
                        Choice.objects.create(question=q, choice_text=choice_text)
                
                elif q.question_type == Question.MULTIPLE_CHOICE and question_type == Question.OPEN_ENDED:
                    q.choices.all().delete()
                
                q.question_type = question_type
            
            q.save()
            return UpdatePoll(
                id=q.id,
                question_text=q.question_text,
                edit_date=q.edit_date,
                question_type=q.question_type,
                choices=q.choices.all() if q.question_type == Question.MULTIPLE_CHOICE else None
            )
        except ObjectDoesNotExist as exc:
            raise ValidationError('Question not found') from exc


class DeletePoll(graphene.Mutation):
    """Mutation to delete an existing poll."""
    class Arguments:
        """Arguments for deleting a poll."""
        question_id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, _info, question_id):
        """Delete a poll by ID."""
        try:
            q = Question.objects.get(pk=question_id)
            q.delete()
            return DeletePoll(success=True)
        except ObjectDoesNotExist as exc:
            raise ValidationError('Question not found') from exc


class AddChoice(graphene.Mutation):
    """Mutation to add a new choice to a multiple-choice question."""
    class Arguments:
        """Arguments for adding a choice."""
        question_id = graphene.ID(required=True)
        choice_text = graphene.String(required=True)

    choice = graphene.Field(ChoiceType)

    def mutate(self, _info, question_id, choice_text):
        """Add a new choice to a multiple-choice question."""
        try:
            question = Question.objects.get(pk=question_id)
            if question.question_type != Question.MULTIPLE_CHOICE:
                raise ValidationError('Can only add choices to multiple choice questions')
            
            choice = Choice.objects.create(
                question=question,
                choice_text=choice_text
            )
            return AddChoice(choice=choice)
        except ObjectDoesNotExist as exc:
            raise ValidationError('Question not found') from exc


class RemoveChoice(graphene.Mutation):
    """Mutation to remove a choice from a multiple-choice question."""
    class Arguments:
        """Arguments for removing a choice."""
        choice_id = graphene.ID(required=True)

    success = graphene.Boolean()
    question_id = graphene.ID()

    def mutate(self, _info, choice_id):
        """Remove a choice by ID, ensuring at least 2 choices remain."""
        try:
            choice = Choice.objects.get(pk=choice_id)
            question = choice.question
            if question.choices.count() <= 2:
                raise ValidationError(
                    'Cannot remove choice: multiple choice questions must have at least 2 choices'
                )            
            choice.delete()
            return RemoveChoice(success=True, question_id=question.id)
        except ObjectDoesNotExist as exc:
            raise ValidationError('Choice not found') from exc


class CreateResponse(graphene.Mutation):
    """Mutation to create a response to a poll question."""
    class Arguments:
        """Arguments for creating a response."""
        question_id = graphene.ID(required=True)
        response_text = graphene.String()
        choice_id = graphene.ID()

    response = graphene.Field(ResponseType)

    def mutate(self, _info, question_id, response_text=None, choice_id=None):
        """Create a response to either a multiple-choice or open-ended question."""
        try:
            question = Question.objects.get(pk=question_id)
            
            if question.question_type == Question.MULTIPLE_CHOICE:
                if not choice_id:
                    raise ValidationError('Multiple choice questions require selecting a choice')
                if choice_id and response_text:
                    raise ValidationError(
                        'Multiple choice questions should not include response text'
                    )
                choice = Choice.objects.get(pk=choice_id)
                if choice.question_id != question.id:
                    raise ValidationError('Selected choice does not belong to this question')
                response = Response.objects.create(
                    question=question,
                    choice=choice,
                    response_text=choice.choice_text
                )
            else:
                if choice_id:
                    raise ValidationError('Open-ended questions should not include a choice')
                if not response_text or not response_text.strip():
                    raise ValidationError('Open-ended questions require non-empty response text')
                if len(response_text) > 1000:
                    raise ValidationError('Response text is too long (maximum 1000 characters)')
                response = Response.objects.create(
                    question=question,
                    response_text=response_text.strip()
                )
            
            return CreateResponse(response=response)
        except ObjectDoesNotExist as exc:
            raise ValidationError('Question or Choice not found') from exc


class DeleteResponse(graphene.Mutation):
    """Mutation to delete an existing response."""
    class Arguments:
        """Arguments for deleting a response."""
        response_id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, _info, response_id):
        """Delete a response by ID."""
        try:
            response = Response.objects.get(pk=response_id)
            response.delete()
            return DeleteResponse(success=True)
        except ObjectDoesNotExist as exc:
            raise ValidationError('Response not found') from exc


class Query(graphene.ObjectType):
    """Root query type for the polls application."""
    questions = graphene.List(QuestionType, n=graphene.Int(required=True))
    question = graphene.Field(QuestionType, question_id=graphene.ID(required=True))

    def resolve_questions(self, _info, n=5):
        """Resolve a list of questions, limited to n items."""
        return Question.objects.all()[:n]

    def resolve_question(self, _info, question_id):
        """Resolve a single question by ID."""
        try:
            return Question.objects.get(pk=question_id)
        except ObjectDoesNotExist:
            return None


class Mutation(graphene.ObjectType):
    """Root mutation type for the polls application."""
    create_poll = CreatePoll.Field()
    update_poll = UpdatePoll.Field()
    delete_poll = DeletePoll.Field()
    create_response = CreateResponse.Field()
    delete_response = DeleteResponse.Field()
    add_choice = AddChoice.Field()
    remove_choice = RemoveChoice.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
