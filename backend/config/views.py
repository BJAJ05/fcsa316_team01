from django.db import DatabaseError, connection
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    """Lets the frontend (and you) check that the API and the database are reachable."""
    try:
        connection.ensure_connection()
        database = "ok"
    except DatabaseError:
        database = "unavailable"

    status_code = 200 if database == "ok" else 503
    return Response({"status": "ok", "database": database}, status=status_code)
