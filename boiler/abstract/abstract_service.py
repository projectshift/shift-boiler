import logging
from flask import current_app
from boiler.feature.orm import db

class AbstractService:
    """
    Abstract service
    Base class for services that encapsulates common model operations.
    Extend your concrete services from this class and define __model__
    """
    __model__ = None
    __create_validator__ = None
    __persist_validator__ = None

    def log(self, message, level=None):
        """ Write a message to log """
        if level is None:
            level = logging.INFO

        current_app.logger.log(msg=message, level=level)

    def is_instance(self, model):
        """
        Is instance?
        Checks if provided object is instance of this service's model.

        :param model:           object
        :return:                bool
        """
        result = isinstance(model, self.__model__)
        if result is True:
            return True

        err = 'Object {} is not of type {}'
        raise ValueError(err.format(model, self.__model__))

    def commit(self):
        """
        Commit
        Commits orm transaction. Used mostly for bulk operations when
        flush is of to commit multiple items at once.

        :return:                None
        """
        db.session.commit()

    def new(self, **kwargs):
        """
        New
        Returns a new unsaved instance of model, populated from the
        provided arguments.

        :param kwargs:          varargs, data to populate with
        :return:                object, fresh unsaved model
        """
        return self.__model__(**kwargs)

    def create(self, **kwargs):
        """
        Create
        Instantiates and persists new model populated from provided
        arguments

        :param kwargs:          varargs, data to populate with
        :return:                object, persisted new instance of model
        """
        model = self.new(**kwargs)
        return self.save(model)

    def save(self, model, commit=True):
        """
        Save
        Puts model into unit of work for persistence. Can optionally
        commit transaction. Returns persisted model as a result.

        :param model:           object, model to persist
        :param commit:          bool, commit transaction?
        :return:                object, saved model
        """
        self.is_instance(model)
        db.session.add(model)
        if commit:
            db.session.commit()

        return model

    def delete(self, model, commit=True):
        """
        Delete
        Puts model for deletion into unit of work and optionall commits
        transaction

        :param model:           object, model to delete
        :param commit:          bool, commit?
        :return:                object, deleted model
        """
        self.is_instance(model)
        db.session.delete(model)
        if commit:
            db.session.commit()

        return model

    def get(self, id):
        """
        Get
        Returns single entity found by id, or None if not found

        :param id:              int, entity id
        :return:                object or None
        """
        return self.__model__.query.get(id)

    def get_or_404(self, id):
        """
        Get or 404
        Returns single entity found by its unique id, or raises
        htp 404 exception if nothing is found.

        :param id:              int, entity id
        :return:                object
        """
        return self.__model__.query.get_or_404(id)

    def get_multiple(self, ids):
        pass

    def find(self, **kwargs):
        return self.__model__.query.filter_by(**kwargs).all()

    def first(self, **kwargs):
        return self.__model__.query.filter_by(**kwargs).first()

    def collection(self, page=None, per_page=None, serialized=None, **kwargs):
        pass

