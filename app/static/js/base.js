/* eslint-disable */
$(document).ready(function ($) {
    $('.hamburger').on('click', function () {
        $('#sidebar').toggleClass('open');
    });

    // Make cards and trs clickable
    $("*[data-href]").on('click', function () {
        location.href = $(this).data("href");
    });

    // $('#bucket-list-edit-form').on('submit', function() {
    //     const url = $(this).attr('action');
    //     const type = $(this).attr('method');
    //     const data = {};
    //
    //     $(this).find('[name]').each(function(index, value) {
    //         const name = $(this).attr('name');
    //         const val = $(this).val();
    //
    //         data[name] = val;
    //     });
    //
    //     $.ajax({
    //         url,
    //         type,
    //         data,
    //         success: function(res) {
    //             console.log(res)
    //         },
    //         error: function (err) {
    //             console.log(err)
    //         }
    //     });
    //
    //     return false;
    // });
});
