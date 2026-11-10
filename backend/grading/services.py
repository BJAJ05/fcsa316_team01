"""
Business layer for `grading` (GradingService in the architecture diagram).

Submissions, automatic grading and retrying wrong answers.
Put the rules of US-07, US-08 here as plain functions so they can be unit tested
without HTTP. Views call these functions; these functions use the models.
"""
