(function () {
    var $user_settings_form = $('#user-settings-form');
    $user_settings_form.on('submit', function (event) {
        event.preventDefault();
        $.ajax({
            url: $user_settings_form.attr('action'),
            type: 'POST',
            data: $user_settings_form.serialize(),
            dataType: 'json',
            success: function (data) {
                $('#settings-update-success').slideDown();
                setTimeout(function () {
                    $('#settings-update-success').slideUp();
                }, 3000);
            },
            error: function (jqXHR) {
                var data = JSON.parse(jqXHR.responseText),
                    message = data.message;
                $('#settings-update-error').find('.message').text(message);
                $('#settings-update-error').slideDown();
                setTimeout(function () {
                    $('#settings-update-error').slideUp();
                }, 5000);
            }
        });
    });
}());