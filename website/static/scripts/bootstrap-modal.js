/* Lier les boutons de création
*  Thanks to Derek Morgan, https://dmorgan.info/posts/django-views-bootstrap-modals/
*/
;(function($) {

  var formAjaxSubmit = function(form, modal)
  {
       $(form).submit(function (e) {
            e.preventDefault();
           $.ajax({
                 type: $(this).attr('method'),
                 url: $(this).attr('action'),
                 data: $(this).serialize(),
                 success: function (xhr, ajaxOptions, thrownError) {
                     if ( $(xhr).find('.has-error').length > 0 || $(xhr).find('.alert-danger').length > 0) {
                           $(modal).find('.modal-body').html(xhr);
                           formAjaxSubmit(form, modal);
                     } else {
                           $(modal).modal('toggle');
                          // Reload page ?
                           location.reload()
                     }
                 },
                 error: function (xhr, ajaxOptions, thrownError) {
                     // handle response errors here
                   }
             });
          });
  };

  $.fn.openModalEvent = function(id, href, title)
  {
    $('#'+id).click(function() {
      $('#form-modal-body').load(href, function()
        {
        $('.modal-title').text(title);
        $('#form-modal').modal('toggle');
        formAjaxSubmit("#form-modal-body form", "#form-modal");
        });
    });
  };
})(jQuery);

