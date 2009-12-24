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
from zope import interface, event
from zope.location import Location
from zope.component import subscribers
from zope.component import getAdapters, getMultiAdapter, queryMultiAdapter
from zope.security import checkPermission
from zope.publisher.interfaces import NotFound
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import Attributes, ObjectModifiedEvent

from z3c.form import button
from z3c.form.interfaces import NOVALUE, IDataManager, IActionHandler, ISubForm

from zojax.layout.pagelet import queryLayout
from zojax.layoutform import PageletForm
from zojax.layoutform.interfaces import \
    ISaveAction, IPageletForm, IPageletSubform, IFormWrapper
from zojax.statusmessage.interfaces import IStatusMessage

from interfaces import _, \
    ISaveable, IWizardStep, IWizardStepForm, IPublisherPlugin


class WizardStep(Location):
    interface.implements(IWizardStep, IFormWrapper)

    label = None
    saveable = None
    permission = None
    permissionAllowed = True

    @property
    def name(self):
        return self.__name__

    def __init__(self, context, wizard, request, *args):
        super(WizardStep, self).__init__(context, request)

        self.wizard = wizard
        self.context = context
        self.__parent__ = wizard

        if self.permission and self.permission != 'zope.Public':
            self.permissionAllowed = checkPermission(self.permission, self)

    def __call__(self, *args, **kw):
        if self.request._traversed_names[-1] != '':
            self.request._traversed_names.append('')

        response = self.request.response
        if self.isRedirected or response.getStatus() in (302, 303):
            return u''

        layout = queryLayout(
            self, self.request, self.__parent__, name=self.layoutname)
        if layout is None:
            return self.render()
        else:
            return layout()

    def publishTraverse(self, request, name):
        view = queryMultiAdapter((self, request), name=name)
        if view is not None:
            if ISaveable.providedBy(view):
                self.saveable = True
            else:
                self.saveable = False

            self.wizard.updateActions()
            return view

        for publisher in subscribers((self, request), IPublisherPlugin):
            try:
                view = publisher.publishTraverse(request, name)
                if ISaveable.providedBy(view):
                    self.saveable = True
                else:
                    self.saveable = False

                self.wizard.updateActions()
                return view
            except NotFound:
                pass

        raise NotFound(self, name, request)

    def isComplete(self):
        return True

    def isAvailable(self):
        return self.permissionAllowed

    def isSaveable(self):
        if self.saveable is None:
            return ISaveable.providedBy(self)
        else:
            return self.saveable

    def postUpdate(self):
        pass

    def getContent(self):
        return self.wizard.getContent()


class WizardStepDisabled(WizardStep):

    title = ''
    weight = 0

    def isAvailable(self):
        return False


class WizardStepForm(WizardStep, PageletForm):
    interface.implements(IWizardStepForm, ISubForm)

    def _loadSubforms(self):
        return [(name, form) for name, form in getAdapters(
                (self.getContent(), self, self.request), IPageletSubform)]

    @property
    def parentForm(self):
        return self.wizard

    @property
    def prefix(self):
        return str(self.name)

    def isComplete(self):
        for form in (self,) + tuple(self.groups) + tuple(self.subforms):
            content = form.getContent()
            for field in form.fields.values():
                if not field.field.required:
                    continue

                dm = getMultiAdapter((content, field.field), IDataManager)
                value = dm.query()
                if value is NOVALUE or value is field.field.missing_value:
                    return False

        return True

    def applyChanges(self, data):
        content = self.getContent()
        changes = applyChanges(self, content, data)
        if changes:
            descriptions = []
            for interface, names in changes.items():
                descriptions.append(Attributes(interface, *names))

            event.notify(ObjectModifiedEvent(content, *descriptions))

        return changes

    _saved = False

    @button.handler(ISaveAction)
    def handleSave(self, action):
        if self._saved:
            return

        self._saved = True

        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                (self.formErrorsMessage,) + errors, 'formError')
        else:
            changes = self.applyChanges(data)
            if changes:
                IStatusMessage(self.request).add(self.successMessage)
            else:
                for subform in self.subforms:
                    if subform.changesApplied:
                        IStatusMessage(self.request).add(self.successMessage)
                        return

                IStatusMessage(self.request).add(self.noChangesMessage)

    def executeActions(self):
        if self.wizard.step.name != self.name:
            return

        request = self.request
        content = self.getContent()

        # execute wizard actions
        for action in self.wizard.actions.executedActions:
            adapter = queryMultiAdapter(
                (self, request, content, action), IActionHandler)
            if adapter:
                adapter()

        # execute step actions
        if self.actions:
            for action in self.actions.executedActions:
                adapter = queryMultiAdapter(
                    (self, request, content, action), IActionHandler)
                if adapter:
                    adapter()

    def update(self):
        if not self.permissionAllowed:
            return

        super(WizardStepForm, self).update()

    def postUpdate(self):
        for form in self.groups:
            form.postUpdate()
        for form in self.subforms:
            form.postUpdate()
        for form in self.forms:
            form.postUpdate()
        for form in self.views:
            form.postUpdate()

        self.executeActions()

        super(WizardStepForm, self).postUpdate()


def applyChanges(form, content, data):
    changes = {}

    forms = [form]
    if IPageletForm.providedBy(form):
        forms.extend(list(form.groups))

    for grp in forms:
        for name, field in grp.fields.items():
            if name not in data:
                continue

            dm = getMultiAdapter((content, field.field), IDataManager)
            try:
                value = dm.get()
            except:
                value = object()

            if value != data[name]:
                dm.set(data[name])
                changes.setdefault(dm.field.interface, []).append(name)

    return changes
