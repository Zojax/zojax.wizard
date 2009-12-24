##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
""" Generic Wizard Implementation

$Id$
"""
from zope import interface
from zope.component import getAdapters
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import NotFound
from zope.traversing.browser import absoluteURL

from zojax.layoutform import button, PageletForm
from zojax.layoutform.interfaces import ISaveAction, ICancelAction, IPageletForm
from zojax.statusmessage.interfaces import IStatusMessage

from interfaces import _
from interfaces import IWizard, IWizardWithTabs, IWizardStep, IDefaultWizardStep
from interfaces import IPreviousAction, IForwardAction, IFinishAction


class Wizard(PageletForm):
    interface.implements(IWizard)

    title = u''
    description = u''

    step = None

    def isComplete(self):
        for step in self.steps:
            if not step.isComplete():
                return False
        return True

    def isFirstStep(self):
        if self.steps:
            return self.step is self.steps[0]
        else:
            return False

    def isLastStep(self):
        if self.steps:
            return self.step is self.steps[-1]
        else:
            return False

    def _loadSteps(self):
        return [form for name, form in
                getAdapters((self.context, self, self.request), IWizardStep)]

    def updateSteps(self):
        _steps = [(step.weight, step.name, step) for step in self._loadSteps()]
        _steps.sort()

        steps = []
        for weight, name, step in _steps:
            step.update()
            if step.isAvailable():
                steps.append((weight, name, step))

        steps.sort()
        steps = [step for weight, name, step in steps]

        self.steps = steps
        self.stepsByName = dict([(step.name, step) for step in steps])

    def updateDefaultStep(self, defaultStep=''):
        if defaultStep:
            if defaultStep in self.stepsByName:
                self.step = self.stepsByName[defaultStep]
        else:
            if self.steps:
                self.step = self.steps[0]

        if self.step is None:
            for step in self.steps:
                if IDefaultWizardStep.providedBy(step):
                    self.step = step
                    return

    def update(self):
        self.subforms = (self.step,)

        self.updateWidgets()
        self.updateActions()

        self.step.postUpdate()
        self.actions.execute()

    @button.handler(IPreviousAction)
    def handlePrevious(self, action):
        for pos, step in enumerate(self.steps):
            if self.step.name == step.name:
                break

        self.redirect('%s/'%absoluteURL(self.steps[pos-1], self.request))

    @button.handler(IForwardAction)
    def handleNext(self, action):
        currentStep = self.step

        if not currentStep.isComplete():
            return

        self.updateSteps()
        for pos, step in enumerate(self.steps):
            if currentStep.name == step.name:
                break

        self.redirect('%s/'%absoluteURL(self.steps[pos+1], self.request))

    @button.handler(ISaveAction)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return

        if not self.step.isComplete():
            return

    @button.handler(IFinishAction)
    def handleFinish(self, action):
        data, errors = self.extractData()
        if errors:
            return

        if not self.isComplete():
            return

        self.finish()

    @button.handler(ICancelAction)
    def handleCancel(self, action):
        self.cancel()

    def getContent(self):
        return self.context

    def clear(self):
        pass

    def finish(self):
        self.clear()
        self.redirect(self.finishURL())

    def cancel(self):
        self.clear()
        self.redirect(self.cancelURL())

    def finishURL(self):
        return '%s/'%absoluteURL(self.context, self.request)

    def cancelURL(self):
        return '%s/'%absoluteURL(self.context, self.request)

    def publishTraverse(self, request, name):
        self.updateSteps()
        self.updateDefaultStep(name)

        if self.step is None:
            if name:
                view = queryMultiAdapter((self, request), name=name)
                if view is not None:
                    return view
            raise NotFound(self, name, request)
        else:
            self.update()

        return self.step

    def browserDefault(self, request):
        return self, (u'',)


class WizardWithTabs(Wizard):
    interface.implements(IWizardWithTabs)

    nextStepName = 'nextstep'

    handlers = Wizard.handlers.copy()

    @button.handler(IPreviousAction)
    def handlePrevious(self, action):
        nextStep = self.request.get(self.nextStepName)
        if nextStep:
            try:
                nextStep = int(nextStep)
            except:
                nextStep = int(nextStep[0])
            self.redirect(
                '%s/'%absoluteURL(self.steps[nextStep], self.request))
        else:
            Wizard.handlePrevious(self, action)

    @button.handler(IForwardAction)
    def handleNext(self, action):
        currentStep = self.step

        if IPageletForm.providedBy(currentStep):
            data, errors = currentStep.extractData()
            if errors:
                return

        if not currentStep.isComplete():
            return

        self.updateSteps()

        nextStep = self.request.get(self.nextStepName)
        if nextStep:
            try:
                nextStep = int(nextStep)
            except:
                nextStep = int(nextStep[0])
            self.redirect(
                '%s/'%absoluteURL(self.steps[nextStep], self.request))
        else:
            for pos, step in enumerate(self.steps):
                if currentStep.name == step.name:
                    break
            self.redirect('%s/'%absoluteURL(self.steps[pos+1], self.request))
