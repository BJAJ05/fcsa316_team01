"""
Presentation / API layer for `classrooms` (US-02, US-03, US-04).

Views (DRF APIView/ViewSet) check permissions, validate input with serializers and
call functions in `services.py`. Keep business logic out of views.
"""
