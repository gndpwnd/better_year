// duplicate forms
function duplicateForm(form_selector, form_title_selector) {
    var original = document.querySelector(form_selector);
    var clone = original.cloneNode(true);
    original.parentNode.insertBefore(clone, original.nextSibling);
    var title_num = parseInt(document.querySelector(form_title_selector).innerHTML.replace('#', ''));
    document.querySelector(form_title_selector).innerHTML = '#' + (title_num + 1);
 }
 
 // if button is clicked, duplicate form
 document.querySelector('#add-more-meals').addEventListener('click', function() {
    duplicateForm('#meal-form', '.meal-form-title');
 });
 document.querySelector('#add-more-workouts').addEventListener('click', function() {
    duplicateForm('#workout-form', '.workout-form-title');
 });
 document.querySelector('#add-more-memories').addEventListener('click', function() {
    duplicateForm('#memory-form', '.memory-form-title');
 });
 document.querySelector('#add-more-images').addEventListener('click', function() {
    duplicateForm('#image-form', '.image-form-title');
 });

 // hide submit url
 document.querySelector('#submit_url').style.display = 'none';
 var submit_url = document.querySelector('#submit_url').innerHTML;

 function submitAllForms() {
    // get all forms
    var forms = document.querySelectorAll('form');
    // combine forms into a data object
    // submit data object to submission url

    //create data object
    var data = {};

    // for each form, get all inputs and add to data object
    for (var i = 0; i < forms.length; i++) {
       var form = forms[i];
       var inputs = form.querySelectorAll('input');
       for (var j = 0; j < inputs.length; j++) {
          var input = inputs[j];
          data[input.name] = input.value;
       }
       var textareas = form.querySelectorAll('textarea');
       for (var j = 0; j < textareas.length; j++) {
          var textarea = textareas[j];
          data[textarea.name] = textarea.value;
       }
    }

    // submit data object to submission url
    var xhr = new XMLHttpRequest();
    xhr.open('POST', submit_url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));

    console.log('submitted');
    console.log(data);
 }

 // clear form after submit
 function clearForm(form) {
    var inputs = form.querySelectorAll('input');
    for (var i = 0; i < inputs.length; i++) {
       var input = inputs[i];
       input.value = '';
    }
    var textareas = form.querySelectorAll('textarea');
    for (var i = 0; i < textareas.length; i++) {
       var textarea = textareas[i];
       textarea.value = '';
    }
    var sliders = document.querySelectorAll('.slider');
    for (var i = 0; i < sliders.length; i++) {
       var slider = sliders[i];
       slider.value = 5;
       // change paragraph with class 'slider-value' to match slider value
       var slider_value = slider.value;
       var slider_paragraph = slider.parentNode.querySelector('.slider-value');
       slider_paragraph.innerHTML = slider_value;
    }
    // reload page
    location.reload();
 }

 //when clear button is clicked, clear all forms
 document.querySelector('#clear-form').addEventListener('click', function() {
    clearForm(document.querySelector('#success-form'));
    clearForm(document.querySelector('#meal-form'));
    clearForm(document.querySelector('#workout-form'));
    clearForm(document.querySelector('#memory-form'));
    clearForm(document.querySelector('#image-form'));
 });
 
 // when submit button is clicked, submit all forms
 document.querySelector('#submit').addEventListener('click', function() {
    submitAllForms();
    clearForm(document.querySelector('#success-form'));
    clearForm(document.querySelector('#meal-form'));
    clearForm(document.querySelector('#workout-form'));
    clearForm(document.querySelector('#memory-form'));
    clearForm(document.querySelector('#image-form'));
 });

 // display current slider value next to slider
 var sliders = document.querySelectorAll('.slider');
 for (var i = 0; i < sliders.length; i++) {
    var slider = sliders[i];
    // add paragraph with class of 'slider-value'
    var output = document.createElement('p');
    output.className = 'slider-value';
    output.innerHTML = slider.value;
    slider.parentNode.insertBefore(output, slider.nextSibling);
    slider.oninput = function() {
       this.nextSibling.innerHTML = this.value;
    }
 }