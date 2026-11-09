"""
Business layer for `assignments` (AssignmentService in the architecture diagram).

Assignments, questions (multiple choice / fill-in) and file attachments.
Put the rules of US-05, US-06, US-14 here as plain functions so they can be unit tested
without HTTP. Views call these functions; these functions use the models.
"""
