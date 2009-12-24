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
""" zojax.layoutform interfaces

$Id$
"""
from zope import interface, schema
from zope.i18nmessageid import MessageFactory
from z3c.form.interfaces import IButton, IActionHandler, IInputForm
from zojax.layoutform.interfaces import ISaveAction, IPageletSubform

_ = MessageFactory('zojax.wizard')


class ISaveable(interface.Interface):
    """ saveable step """


class IPreviousAction(interface.Interface):
    """A button that returns to some previous state or screen."""


class IForwardAction(interface.Interface):
    """A button that returns to some next state or screen."""


class IFinishAction(ISaveAction):
    """A button that finish wizard."""


class IWizard(IInputForm):
    """An interface marking the controlling wizard form."""

    label = interface.Attribute('Wizard label')
    title = interface.Attribute('Wizard title')
    description = interface.Attribute('Wizard description')

    step = interface.Attribute('Current wizard step.')
    steps = interface.Attribute("Ordered list of all wizard's steps.")

    def updateSteps():
        """Load and filter steps."""

    def updateDefaultStep(defaultName=''):
        """Set current step."""

    def getContent():
        """Return wizard content."""

    def isComplete():
        """Determines whether the wizard is complete."""

    def isFirstStep():
        """Determine whether the current step is the first one."""

    def isLastStep():
        """Determine whether the current step is the last one."""

    def finish():
        """Finish wizard processing."""

    def finishURL():
        """Finish url"""

    def cancel():
        """Cancel wizard processing."""

    def cancelURL():
        """Cancel url"""

    def clear():
        """Clear wizard data."""


class IWizardWithTabs(IWizard):

    nextStepName = schema.TextLine(
        title = u'Next Step Field Name',
        required = True)


class IWizardStep(IPageletSubform):
    """An interface marking a step."""

    wizard = interface.Attribute('Wizard')
    updated = interface.Attribute('Updated status')

    name = schema.TextLine(
        title = u'Name',
        description = u'Step name',
        required = True)

    label = schema.TextLine(
        title = u'Label',
        description = u'Step label',
        default = u'',
        required = False)

    title = schema.TextLine(
        title = u'Title',
        description = u'Step title',
        default = u'',
        required = True)

    weight = schema.Int(
        title = u'Weight',
        required = True,
        default = 99999)

    permission = schema.Bytes(
        title = u'Permission',
        required = False)

    def getContent():
        """Return wizard content"""

    def isComplete():
        """Determines whether a step is complete."""

    def isAvailable():
        """Determines whether a step is available.

        This method call before update method."""

    def isSaveable():
        """Determines whether a step saveable."""

    def render():
        """Render step."""

    def update():
        """Update step."""


class IWizardStepForm(IWizardStep):
    """ step implementation based on IForm """

    def applyChanges():
        """Apply changes to content.
        Step should extract data and save to content."""


class IPublisherPlugin(interface.Interface):
    """ Publisher plugin """

    def publishTraverse(request, name):
        """ publish """


class IDefaultWizardStep(interface.Interface):
    """ Default wizard step """


class IWizardButton(IButton):
    """ wizard button """

    content = interface.Attribute('Content')
    wizard = interface.Attribute('Wizard')
    request = interface.Attribute('Request')

    prefix = schema.BytesLine(
        title = u'Prefix',
        required = False)

    weight = schema.Int(
        title = u'Weight',
        required = False)

    def isAvailable():
        """Is button availabe in context"""

    def handleAction():
        """Simple buton action handler"""


class IWizardActionHandler(IActionHandler):
    """ wizard action handler """
