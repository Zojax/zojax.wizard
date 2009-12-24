function submitAndMove2Step(formId, action, saveAction, nextStep, index)
{
    var form = $(document.getElementById(formId));

    if (action) {
	//add hidden input for emulating press button action
	form.append('<input type="hidden" name="'+action+'" value="1"/>');
    }
    if (saveAction) {
	// save action
	form.append('<input type="hidden" name="'+saveAction+'" value="1"/>');
    }
    if (nextStep) {
	// add hidden with next step index
	form.append('<input type="hidden" name="'+nextStep+'" value="'+index+'"/>');
    }

    // submit form
    form.submit();

    return false;
}

var wizardTabsHandler = function(formId, action, save, nextStep, index) {
    return function(e)
    {
        return submitAndMove2Step(formId, action, save, nextStep, index);
    };
};

function subscribeWizardTabs(
    formId, prevActionName, nextActionName, 
    saveActionName, currentClass, searchLink, nextStep) {

    //subscribe tabs
    var elems = $(searchLink);
    var nextAction = false;
    for (var i = 0; i < elems.length; i++)
    {
      var el = $(elems[i]);
      if (el.parent('li').is("."+currentClass))
      {
          nextAction = true;
      }
      else if (nextAction)
      {
	  if (nextActionName) {
              el.bind("click", wizardTabsHandler(formId, nextActionName, saveActionName, nextStep, i));
	  }
      }
      else
      {
	  if (prevActionName) {
              el.bind("click", wizardTabsHandler(formId, prevActionName, saveActionName, nextStep, i));
	  }
      }
    }
}
