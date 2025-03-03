"""Test cases for GraphQL schema mutations in the polls application."""

from django.test import TestCase
from graphene.test import Client
from polls.models import Question, Choice, Response
from polls.schema import schema


class TestPollsMutations(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client(schema)
        # Create a test multiple choice question
        self.mc_question = Question.objects.create(
            question_text="What is your favorite color?",
            question_type=Question.MULTIPLE_CHOICE
        )
        self.choice1 = Choice.objects.create(
            question=self.mc_question,
            choice_text="Blue"
        )
        self.choice2 = Choice.objects.create(
            question=self.mc_question,
            choice_text="Red"
        )
        
        # Create a test open-ended question
        self.oe_question = Question.objects.create(
            question_text="What are your thoughts on GraphQL?",
            question_type=Question.OPEN_ENDED
        )

    def test_create_poll_open_ended(self):
        """Test creating an open-ended poll."""
        mutation = """
        mutation {
            createPoll(
                question: "What is your opinion on testing?",
                questionType: "OE"
            ) {
                id
                questionText
                questionType
            }
        }
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['createPoll']
        self.assertEqual(data['questionText'], "What is your opinion on testing?")
        self.assertEqual(data['questionType'], "OE")

    def test_create_poll_multiple_choice(self):
        """Test creating a multiple choice poll."""
        mutation = """
        mutation {
            createPoll(
                question: "Which testing framework do you prefer?",
                questionType: "MC",
                choices: ["PyTest", "UnitTest", "Jest"]
            ) {
                id
                questionText
                questionType
                choices {
                    choiceText
                }
            }
        }
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['createPoll']
        self.assertEqual(data['questionText'], "Which testing framework do you prefer?")
        self.assertEqual(data['questionType'], "MC")
        self.assertEqual(len(data['choices']), 3)

    def test_create_poll_multiple_choice_validation(self):
        """Test validation when creating a multiple choice poll without choices."""
        mutation = """
        mutation {
            createPoll(
                question: "Invalid multiple choice?",
                questionType: "MC"
            ) {
                id
            }
        }
        """
        result = self.client.execute(mutation)
        self.assertIsNotNone(result.get('errors'))

    def test_update_poll(self):
        """Test updating a poll's question text."""
        mutation = f"""
        mutation {{
            updatePoll(
                questionId: "{self.mc_question.id}",
                question: "What is your preferred color?"
            ) {{
                id
                questionText
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['updatePoll']
        self.assertEqual(data['questionText'], "What is your preferred color?")

    def test_update_poll_type_and_choices(self):
        """Test updating a poll's type and choices."""
        mutation = f"""
        mutation {{
            updatePoll(
                questionId: "{self.mc_question.id}",
                questionType: "MC",
                choices: ["Green", "Yellow", "Purple"]
            ) {{
                id
                questionType
                choices {{
                    choiceText
                }}
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['updatePoll']
        self.assertEqual(len(data['choices']), 3)

    def test_update_poll_invalid_id(self):
        """Test updating a non-existent poll."""
        mutation = """
        mutation {
            updatePoll(
                questionId: "999",
                question: "Invalid question"
            ) {
                id
            }
        }
        """
        result = self.client.execute(mutation)
        self.assertIsNotNone(result.get('errors'))

    def test_delete_poll(self):
        """Test deleting a poll."""
        mutation = f"""
        mutation {{
            deletePoll(questionId: "{self.oe_question.id}") {{
                success
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['deletePoll']
        self.assertTrue(data['success'])
        self.assertFalse(Question.objects.filter(id=self.oe_question.id).exists())

    def test_delete_poll_invalid_id(self):
        """Test deleting a non-existent poll."""
        mutation = """
        mutation {
            deletePoll(questionId: "999") {
                success
            }
        }
        """
        result = self.client.execute(mutation)
        self.assertIsNotNone(result.get('errors'))

    def test_add_choice(self):
        """Test adding a choice to a multiple choice question."""
        mutation = f"""
        mutation {{
            addChoice(
                questionId: "{self.mc_question.id}",
                choiceText: "Green"
            ) {{
                choice {{
                    choiceText
                    question {{
                        id
                    }}
                }}
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['addChoice']
        self.assertEqual(data['choice']['choiceText'], "Green")

    def test_add_choice_to_open_ended(self):
        """Test adding a choice to an open-ended question (should fail)."""
        mutation = f"""
        mutation {{
            addChoice(
                questionId: "{self.oe_question.id}",
                choiceText: "Invalid Choice"
            ) {{
                choice {{
                    choiceText
                }}
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNotNone(result.get('errors'))

    def test_remove_choice(self):
        """Test removing a choice from a multiple choice question."""
        # Add an extra choice first to maintain minimum of 2 choices
        extra_choice = Choice.objects.create(
            question=self.mc_question,
            choice_text="Green"
        )
        
        mutation = f"""
        mutation {{
            removeChoice(choiceId: "{extra_choice.id}") {{
                success
                questionId
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['removeChoice']
        self.assertTrue(data['success'])

    def test_remove_choice_minimum_validation(self):
        """Test removing a choice when only 2 choices exist (should fail)."""
        mutation = f"""
        mutation {{
            removeChoice(choiceId: "{self.choice1.id}") {{
                success
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNotNone(result.get('errors'))

    def test_create_multiple_choice_response(self):
        """Test creating a response for a multiple choice question."""
        mutation = f"""
        mutation {{
            createResponse(
                questionId: "{self.mc_question.id}",
                choiceId: "{self.choice1.id}"
            ) {{
                response {{
                    responseText
                    choice {{
                        choiceText
                    }}
                }}
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['createResponse']
        self.assertEqual(data['response']['choice']['choiceText'], "Blue")

    def test_create_open_ended_response(self):
        """Test creating a response for an open-ended question."""
        mutation = f"""
        mutation {{
            createResponse(
                questionId: "{self.oe_question.id}",
                responseText: "GraphQL is amazing!"
            ) {{
                response {{
                    responseText
                }}
            }}
        }}
        """
        result = self.client.execute(mutation)
        self.assertIsNone(result.get('errors'))
        data = result['data']['createResponse']
        self.assertEqual(data['response']['responseText'], "GraphQL is amazing!")

    def test_create_response_validation(self):
        """Test response validation for both question types."""
        # Test multiple choice without choice_id
        mutation1 = f"""
        mutation {{
            createResponse(
                questionId: "{self.mc_question.id}",
                responseText: "Invalid"
            ) {{
                response {{
                    id
                }}
            }}
        }}
        """
        result1 = self.client.execute(mutation1)
        self.assertIsNotNone(result1.get('errors'))

        # Test open-ended with choice_id
        mutation2 = f"""
        mutation {{
            createResponse(
                questionId: "{self.oe_question.id}",
                choiceId: "{self.choice1.id}"
            ) {{
                response {{
                    id
                }}
            }}
        }}
        """
        result2 = self.client.execute(mutation2)
        self.assertIsNotNone(result2.get('errors'))

        # Test open-ended with empty response
        mutation3 = f"""
        mutation {{
            createResponse(
                questionId: "{self.oe_question.id}",
                responseText: ""
            ) {{
                response {{
                    id
                }}
            }}
        }}
        """
        result3 = self.client.execute(mutation3)
        self.assertIsNotNone(result3.get('errors')) 