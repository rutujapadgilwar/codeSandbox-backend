"""Models for the polls management system, handling questions, choices, and responses."""

from django.core.exceptions import ValidationError
from django.db import models
# pylint: disable=no-member

class Question(models.Model):
    """Model representing a poll question that can be either open-ended or multiple choice."""
    objects = models.Manager()
    OPEN_ENDED = 'OE'
    MULTIPLE_CHOICE = 'MC'
    QUESTION_TYPES = [
        (OPEN_ENDED, 'Open Ended'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]

    question_text = models.CharField(max_length=200)
    print(question_text)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    edit_date = models.DateTimeField('last edited', auto_now=True)
    question_type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPES,
        default=OPEN_ENDED
    )

    def clean(self) -> None:
        """Validate that multiple choice questions have at least 2 choices."""
        if self.question_type == self.MULTIPLE_CHOICE:
            if self.choices.count() < 2:
                raise ValidationError('Multiple choice questions must have at least 2 choices')


class Choice(models.Model):
    """Model representing a predefined choice for multiple choice questions."""
    objects = models.Manager()
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class Response(models.Model):
    """Model representing a user's response to a question, supporting both open-ended
    and multiple choice answers."""
    objects = models.Manager()
    question = models.ForeignKey(Question, related_name='responses', on_delete=models.CASCADE)
    response_text = models.TextField()
    
    choice = models.ForeignKey(
        Choice,
        null=True,
        blank=True,
        related_name='responses',
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_response_preview(self, length: int = 50) -> str:
        """Return a truncated preview of the response text."""
        return str(self.response_text)[:length]

    def clean(self) -> None:
        """Validate response based on question type."""
        if self.question.question_type == Question.MULTIPLE_CHOICE:
            if not self.choice:
                raise ValidationError('Multiple choice questions require selecting a predefined choice')
            if self.choice.question_id != self.question_id:
                raise ValidationError('Selected choice does not belong to this question')
        else:
            if self.choice:
                raise ValidationError('Open-ended questions should not have a choice selected')

    def save(self, *args, **kwargs) -> None:
        """Save response after validation."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return string representation of the response."""
        if self.question.question_type == Question.MULTIPLE_CHOICE:
            print(self.choice.choice_text)
            return f"Response to {self.question.question_text}: {self.choice.choice_text}"
        preview = self.get_response_preview()
        return f"Response to {self.question.question_text}: {preview}..."
