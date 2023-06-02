$(function () {
    $('button').click(function () {
        var a = $('input[name="a"]').val();
        var b = $('input[name="b"]').val();
        $.ajax({
            url: '/_add_numbers',
            data: $('form').serialize(),
            type: 'POST',
            success: function (response) {
                console.log(response);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});