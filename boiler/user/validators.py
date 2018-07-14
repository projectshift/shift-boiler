from shiftschema.validators import AbstractValidator
from shiftschema.result import Error


class UniqueUserProperty(AbstractValidator):
    error = 'Set proper error message'
    property = None

    def validate(self, value, model=None, context=None):
        """ Perform validation """
        from boiler.user.services import user_service

        self_id = None
        if model:
            if isinstance(model, dict):
                self_id = model.get('id')
            else:
                self_id = getattr(model, 'id')

        params = dict()
        params[self.property] = value
        found = user_service.first(**params)
        if not found or (model and self_id == found.id):
            return Error()

        return Error(self.error)


class UniqueEmail(UniqueUserProperty):
    """ Validates that provided email is unique """
    error = 'Email already in use'
    property = 'email'


class UniqueRoleHandle(AbstractValidator):
    """ Role handle must be unique """
    error = 'Role handle already in use'

    def validate(self, value, model=None, context=None):
        """ Perform validation """
        from boiler.user.services import role_service

        self_id = None
        if model:
            if isinstance(model, dict):
                self_id = model.get('id')
            else:
                self_id = getattr(model, 'id')

        found = role_service.first(handle=value)
        if not found or (model and self_id == found.id):
            return Error()

        return Error(self.error)





