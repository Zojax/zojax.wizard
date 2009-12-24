##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface, component, event
from zope.location import locate
from zope.component import getAdapters, getMultiAdapter, queryMultiAdapter

from z3c.form import util, action, interfaces
from z3c.form.widget import AfterWidgetUpdateEvent
from z3c.form.button import Button, ButtonActions
from z3c.form.button import ButtonAction, ButtonActionHandler

from interfaces import IWizard, IWizardButton, IWizardActionHandler


class WizardButton(Button):
    interface.implements(IWizardButton)

    def __init__(self, provides=None, prefix='', weight=0, *args, **kwargs):
        super(WizardButton, self).__init__(self, *args, **kwargs)

        self.prefix = prefix
        self.weight = weight

        if provides:
            interface.alsoProvides(self, provides)

    def isAvailable(self):
        if self.condition:
            return self.condition(self.wizard)

        return True

    def actionHandler(self):
        pass

    def __call__(self, content, wizard, request):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)

        # set parent
        clone.content = content
        clone.wizard = wizard
        clone.request = request
        return clone


class DisabledWizardButton(WizardButton):

    def isAvailable(self):
        return False

disabledWizardButton = DisabledWizardButton(title = u'Disabled')


class WizardButtonActionHandler(ButtonActionHandler):
    interface.implementsOnly(IWizardActionHandler)

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.field)
        if handler is not None:
            return handler(self.form, self.action)

        if IWizardButton.providedBy(self.action.field):
            return self.action.field.actionHandler()


class WizardButtonActions(ButtonActions):
    component.adapts(IWizard, interface.Interface, interface.Interface)

    def execute(self):
        for baction in self.executedActions:
            handler = queryMultiAdapter(
                (self.form, self.request, self.content, baction),
                IWizardActionHandler)
            if handler is not None:
                try:
                    result = handler()
                except interfaces.ActionExecutionError, error:
                    event.notify(action.ActionErrorOccurred(action, error))
                else:
                    event.notify(action.ActionSuccessful(action))
                    return result

    def update(self):
        form = self.form
        content = self.content
        request = self.request
        formbuttons = form.buttons

        buttons = []

        allbuttons = [formbuttons]
        allbuttons.extend(
            [b for n, b in getAdapters(
                    (content, form, request), interfaces.IButtons)])

        prefix = util.expandPrefix(form.prefix)

        weight = 100

        for btns in allbuttons:
            bprefix = prefix + util.expandPrefix(btns.prefix)

            for name, button in btns.items():
                if button.condition is not None and not button.condition(form):
                    continue

                weight += 1
                bweight = getattr(button, 'weight', weight)
                buttons.append((bweight, bprefix + name, button))

        for name, button in getAdapters((content, form, request), IWizardButton):
            if not button.isAvailable():
                continue

            bprefix = prefix + util.expandPrefix(
                button.prefix or formbuttons.prefix)

            weight += 1
            bweight = button.weight or weight
            buttons.append((bweight, str(bprefix + name), button))

        buttons.sort()

        for weight, name, button in buttons:
            if button.actionFactory is not None:
                buttonAction = button.actionFactory(request, button)
            else:
                buttonAction = getMultiAdapter(
                    (request, button), interfaces.IButtonAction)

            # Step 3: Set the name on the button
            buttonAction.name = name

            # Step 4: Set any custom attribute values.
            title = queryMultiAdapter(
                (form, request, content, button, self),
                interfaces.IValue, name='title')

            if title is not None:
                buttonAction.title = title.get()

            # Step 5: Set the form
            buttonAction.form = form
            interface.alsoProvides(buttonAction, interfaces.IFormAware)

            # Step 6: Update the new action
            buttonAction.update()
            event.notify(AfterWidgetUpdateEvent(buttonAction))

            # Step 7: Add the widget to the manager
            self._data_keys.append(name)
            self._data_values.append(buttonAction)
            self._data[name] = buttonAction

            locate(buttonAction, self, name)
