"""
Business layer for `assignments` (AssignmentService in the architecture diagram).

US-05: teachers create, change and delete assignments in their own classes; teachers and
enrolled students list and open them. Access goes through classrooms.services, so a user
only ever reaches assignments of classes they teach or have joined.
"""

from classrooms.services import get_class, list_classes

from .models import Assignment


class AssignmentNotFound(Exception):
    """No assignment with that id, or one in a class the user may not see."""


def list_assignments(user, class_id):
    """Assignments of one class the user may see, earliest due date first."""
    classroom = get_class(user, class_id)  # raises ClassNotFound
    return Assignment.objects.filter(classroom=classroom)


def get_assignment(user, assignment_id):
    """
    One assignment in a class the user teaches or has joined. Raises AssignmentNotFound for
    any other assignment, so the API answers 404 without revealing that it exists.
    """
    try:
        return Assignment.objects.select_related("classroom").get(
            pk=assignment_id, classroom__in=list_classes(user)
        )
    except Assignment.DoesNotExist as error:
        raise AssignmentNotFound(assignment_id) from error


def create_assignment(teacher, class_id, title, instructions, due_date):
    """Create an assignment in one of the teacher's own classes (raises ClassNotFound)."""
    classroom = get_class(teacher, class_id)
    return Assignment.objects.create(
        classroom=classroom, title=title, instructions=instructions, due_date=due_date
    )


def update_assignment(teacher, assignment_id, **fields):
    """Change the title, instructions and/or due date of the teacher's own assignment."""
    assignment = get_assignment(teacher, assignment_id)
    for name, value in fields.items():
        setattr(assignment, name, value)
    if fields:
        assignment.save(update_fields=list(fields))
    return assignment


def delete_assignment(teacher, assignment_id):
    """Delete the teacher's own assignment (raises AssignmentNotFound for any other)."""
    get_assignment(teacher, assignment_id).delete()
