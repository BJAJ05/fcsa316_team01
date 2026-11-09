"""
Presentation / API layer for `analytics` (US-12, US-13).

Views (DRF APIView/ViewSet) check permissions, validate input with serializers and
call functions in `services.py`. Keep business logic out of views.
"""
