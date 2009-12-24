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
from zope.proxy import removeAllProxies
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL

from zojax.wizard.interfaces import IPreviousAction, IForwardAction
from zojax.layoutform.interfaces import ISaveAction


class WizardWithTabsLayout(object):

    currentClass = 'z-wizard-selected'
    searchLink = 'ul.z-wizard-wizardsteps li a'

    saveButtonName = ''
    forwardButtonName = ''
    previousButtonName = ''

    def update(self):
        super(WizardWithTabsLayout, self).update()

        #find forward and previous actions
        if not hasattr(self.context, 'actions'):
            return

        for name, action in self.context.actions.items():
            field = removeAllProxies(action).field
            if IPreviousAction.providedBy(field):
                self.previousButtonName = name
            if IForwardAction.providedBy(field):
                self.forwardButtonName = name
            if ISaveAction.providedBy(field):
                self.saveButtonName = name

    def getSteps(self):
        context = self.context
        request = self.request
        try:
            name = context.step.name
        except:
            name = u''

        return [
            {'name': step.name,
             'title': step.title,
             'current': step.name == name,
             'url': '%s/%s/'%(absoluteURL(context, request), step.name),
             'completed': step.isComplete(),
             'icon': queryMultiAdapter((step, request), name='zmi_icon'),
             }
            for step in self.context.steps if step is not None]

    def subscribeScript(self):
        return """$(document).ready(function()
                  {subscribeWizardTabs('%(formId)s', '%(prev)s', '%(next)s',
                                       '%(save)s', '%(currentClass)s',
                                       '%(searchLink)s', '%(nextStep)s');
                  });
               """ % {'formId': self.context.id,
                      'prev': self.previousButtonName,
                      'next': self.forwardButtonName,
                      'save': self.saveButtonName,
                      'currentClass': self.currentClass,
                      'searchLink': self.searchLink,
                      'nextStep': self.context.nextStepName,
                      }
