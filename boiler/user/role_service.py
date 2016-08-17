from boiler.feature.orm import db
from boiler.abstract.abstract_service import AbstractService
from boiler.user.models import RoleSchema, Role
from boiler.user import events


class RoleService(AbstractService):
    """
    Group service
    Handles common operations on role entities.
    """
    __model__ = Role

    def save(self, role, commit=True):
        """ Persist role model """
        self.is_instance(role)

        schema = RoleSchema()
        valid = schema.process(role)
        if not valid:
            return valid

        db.session.add(role)
        if commit:
            db.session.commit()

        events.role_saved_event.send(role)
        return role

    def create(self, handle, title=None, description=None):
        """ Create a role """
        role = Role(handle=handle, title=title, description=description)
        schema = RoleSchema()
        valid = schema.process(role)
        if not valid:
            return valid

        db.session.add(role)
        db.session.commit()

        events.role_created_event.send(role)
        return role

    def delete(self, role, commit=True):
        """ Delete a role """
        events.role_deleted_event.send(role)
        return super().delete(role, commit)