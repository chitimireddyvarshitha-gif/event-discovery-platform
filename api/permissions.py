from rest_framework import permissions


class IsOrganizer(permissions.BasePermission):
    """Permit access only to users with the 'organizer' role."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'organizer'
        )


class IsAttendee(permissions.BasePermission):
    """Permit access only to users with the 'attendee' role."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'attendee'
        )


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Permit modifications only by organizers; everyone else has read-only access."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'organizer'
        )
