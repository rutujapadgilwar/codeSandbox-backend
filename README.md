# TIFIN Backend Code Exercise

Thank you for taking the time to complete this take-home exercise. We believe this is the good way to determine whether a candidate has the skills to succeed here as a Backend Engineer here. We do not want this to be a burden, so this exercise should only take a couple of hours.

If you have any questions, feel free to simply note an assumption and move on. We would prefer you get through the full assessment making assumptions, over not getting to the end.

Likewise, some of the requirements listed are purposefully vague - in those instances, use your judgment to determine a solution.

Your solutions will be evaluated based both on “correctness”, in terms of the listed requirements, and on other factors like overall approach, architecture, quality, and general best practices.  This is where well-documented code can be your friend!



## Instructions

This is a simple Django GraphQL API project for tracking polls (questions).  Contained is a very simple API schema already present for listing, creating, and deleting questions.  You will be asked to make a number of changes to this API as the exercise progresses.

### Setup
This CodeSandbox should have everything you need to compelte the exercise, apart from any additional libraries you may want to utilize.  If you wish to add libraries then you can do so by adding them to the `requirements.txt` and running the `install` task.

There are several other tasks you may find useful, which can all be executed from a button in the toolbar, next to your avatar.

- `runserver` - start the Django server
- `install` - install PIP requirements
- `make_migrations` - generate new migration files from Django models
- `migrate` - apply migrations to the local `./db.sqlite3` database
- `shell_plus` - launches Django's interactive shell

You can also open the interactive GraphQL console in the web preview by navigating to `/graphql`.

Restarting this sandbox will automatically wipe your database and run `install` -> `migrate` -> `runserver`.  If at any point you need to reset your database manually, just delete `./db.sqlite3` and run the `migrate` task.


### Task 1 - Add support for question CRUD

The current API only allows you to fetch and create questions, but we would like the ability to update and delete questions as well.  Please add these capabilities to the existing API.

**Requirements:**
- Client can update the text of a specific question by ID.
- New field `edit_date` shows the timestamp of the most recent update
- Client can delete a question by ID


### Task 2 - Add support for responses

A poll is no good if we can't collection answers! Please create a new API which will let us submit free-form answers to questions.

**Requirements:**
- Client can create a response with a free-form value
- Client can only create a new response for an existing question
- Client can fetch a question along with all of its responses


### Task 3  - Add support for "multiple choice" questions

Up to this point we can only ask open-ended questions, but we don't want people just writing in "Chuck Norris" for all of our questions!  We should
be able to support multiple-choice questions, which have a list of pre-defined responses.

**Requirements:**
- Client can create a multiple-choice question
- Client must provide at least 2 valid responses when creating a multiple-choice question
- Client can add or remove responses for a question
- Client can only submit one of the question's pre-defined responses as their response