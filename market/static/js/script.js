document.addEventListener('DOMContentLoaded', function() {
  const openModalButtons = document.querySelectorAll('.btn-info');
  const closeModalButtons = document.querySelectorAll('.close-modal');

  openModalButtons.forEach(button => {
    button.addEventListener('click', function() {
      const modalId = this.dataset.modal;
      const modal = document.getElementById(modalId);
      modal.showModal();
    });
  });

  closeModalButtons.forEach(button => {
    button.addEventListener('click', function() {
      const modal = this.closest('dialog');
      modal.close();
    });
  });
});

var purchaseButtons = document.querySelectorAll('.btn-purchase');


purchaseButtons.forEach(function(button) {
  button.addEventListener('click', function() {
    var modalId = this.getAttribute('data-target');    
    var modal = document.querySelector(modalId);
    modal.showModal();    
  });
});

var closeModalButtons = document.querySelectorAll('.close-modal');

closeModalButtons.forEach(function(button) {
  button.addEventListener('click', function(event) {
    event.preventDefault();
    var modal = this.closest('dialog');
    modal.close();
  });
});