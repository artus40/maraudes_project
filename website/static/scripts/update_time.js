  $(function() {

    var input = $('#id_heure_debut')

    $.fn.editHeureValue = function(mod) {
      var value = input.attr('value').split(":");
      var new_hour = parseInt(value[0]);
      var new_minutes = parseInt(value[1]) + mod;
      if (new_minutes >= 60) {
        new_hour += 1;
        new_minutes -= 60;
      } else if (new_minutes < 0) {
        new_hour -= 1;
        new_minutes += 60;
      };
      if (new_hour >= 24) {
        new_hour -= 24;
      } else if (new_hour < 0) {
        new_hour += 24
      };

      value[0] = new_hour;
      value[1] = new_minutes;
      input.attr('value', value.join(":"));

    };

    $('#minus-5').click(function() {
      $.fn.editHeureValue(-5)
      //console.log('minus 5')
    });
    $('#plus-5').click(function() {
      $.fn.editHeureValue(5)
      //console.log('plus 5')
    });
  });
