#__all__ = ('StateField',)

from django.db import models
from django.utils.functional import curry
from twemoir.lib.states2.machine import StateMachine

from twemoir.lib.states2.model_methods import (get_STATE_transitions,
                                   get_public_STATE_transitions,
                                   get_STATE_info, get_STATE_machine)


class MixIntrospector(object):

   def south_field_triple(self):
       """ Returns the field's module/classname pseudo-modulepath for South. """
       from south.modelsinspector import introspector
       field_class = "twemoir.lib.states2.fields.%s" % self.__class__.__name__
       args, kwargs = introspector(self)
       return (field_class, args, kwargs)


class StateField(models.CharField, MixIntrospector):
    '''
    Add state information to a model.

    This will add extra methods to the model.

    Usage::

        status = StateField(machine=PowerState)
    '''
    def __init__(self, **kwargs):
        # State machine parameter. (Fall back to default machine.
        # e.g. when South is creating an instance.)
        self._machine = kwargs.pop('machine', StateMachine)

        kwargs.setdefault('max_length', 100)
        kwargs['choices'] = None
        super(StateField, self).__init__(**kwargs)
    
    def get_internal_type(self):
        return "CharField"

    def contribute_to_class(self, cls, name):
        '''
        Adds methods to the :class:`~django.db.models.Model`.

        The extra methods will be added for each :class:`StateField` in a
        model:

        - :meth:`~states2.model_methods.get_STATE_transitions`
        - :meth:`~states2.model_methods.get_public_STATE_transitions`
        - :meth:`~states2.model_methods.get_STATE_info`
        - :meth:`~states2.model_methods.get_STATE_machine`
        '''
        super(StateField, self).contribute_to_class(cls, name)

        # Set choice options (for combo box)
        self._choices = self._machine.get_state_choices()
        self.default = self._machine.initial_state

        # do we need logging?
        if self._machine.log_transitions:
            from twemoir.lib.states2.log import _create_state_log_model
            log_model = _create_state_log_model(cls, name, self._machine)
        else:
            log_model = None

        setattr(cls, '_%s_log_model' % name, log_model)

        # adding extra methods
        setattr(cls, 'get_%s_transitions' % name,
            curry(get_STATE_transitions, field=name))
        setattr(cls, 'get_public_%s_transitions' % name,
            curry(get_public_STATE_transitions, field=name))
        setattr(cls, 'get_%s_info' % name,
            curry(get_STATE_info, field=name, machine=self._machine))
        setattr(cls, 'get_%s_machine' % name,
            curry(get_STATE_machine, field=name, machine=self._machine))

        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        '''
        Override ``save``, call initial state handler on save.

        When ``.save(no_state_validation=True)`` has been used, the state won't
        be validated, and the handler won't we executed. It's recommended to
        use this parameter in South migrations, because South is not really
        aware of which state machine is used for which classes.

        Note that we wrap ``save`` only after the ``class_prepared`` signal
        has been sent, it won't work otherwise when the model has a
        custom ``save`` method.
        '''
        real_save = sender.save

        def new_save(obj, *args, **kwargs):
            created = not obj.id

            # Validate whether this is an existing state
            if kwargs.pop('no_state_validation', True):
                state = None
            else:
                # Can raise UnknownState
                state = self._machine.get_state(obj.state)

            # Save first using the real save function
            result = real_save(obj, *args, **kwargs)

            # Now call the handler
            if created and state:
                state.handler(obj)
            return result

        sender.save = new_save
    
    def south_field_triple(self):
        """ Returns the field's module/classname pseudo-modulepath for South. """
        from south.modelsinspector import introspector
        field_class = "twemoir.lib.states2.fields.StateField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
