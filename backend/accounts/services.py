"""
Business layer for `accounts` (AuthService in the architecture diagram).

Users, registration, login and JWT tokens.
Put the rules of US-01 here as plain functions so they can be unit tested
without HTTP. Views call these functions; these functions use the models.
"""
