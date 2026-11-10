"""
Presentation / API layer for `assignments` (US-05, US-06, US-14).

Views (DRF APIView/ViewSet) check permissions, validate input with serializers and
call functions in `services.py`. Keep business logic out of views.
"""
