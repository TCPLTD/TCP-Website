/* Enquiry form. The site has no server, so the form opens the visitor's email app with the message filled in.
   To receive enquiries directly instead, connect a form service (e.g. Formspree) and post to it here. */
(function () {
  var form = document.getElementById('enquiry');
  if (!form) return;
  var status = document.getElementById('f-status');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = form.elements.name.value.trim();
    var contact = form.elements.contact.value.trim();
    if (!name || !contact) { status.textContent = 'Please add your name and a phone number or email so we can reply.'; return; }
    var body = 'Name: ' + name + '\nContact: ' + contact + '\nProperty: ' + form.elements.area.value + '\nProject: ' + form.elements.type.value + '\n\n' + form.elements.message.value;
    window.location.href = 'mailto:martin@tcpltd.net?subject=' + encodeURIComponent('Website enquiry: ' + (form.elements.type.value || 'new project')) + '&body=' + encodeURIComponent(body);
    status.textContent = 'Your email app should open with your message ready to send. If it does not, email martin@tcpltd.net or call 07843 561129.';
  });
})();
