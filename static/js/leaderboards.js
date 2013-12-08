$(function () {
    function fetchLeaderboards() {
        var activity = $('#select-activity').find('li.active').data('type');
        var timespan = $('#select-timespan').find('li.active').data('type');

        if (!timespan) {
            timespan = $('#select-past-leaderboard-months').val();
        }

        $.ajax({
            url: '/leaderboards/get_leaderboard',
            data: {activity: activity, timespan: timespan},
            type: 'GET',
            dataType: 'html',
            success: function (html) {
                $('#leaderboard-container').html(html);
            },
            error: function (a, b, c) {
                console.log(a, b, c);
            }
        });
    }

    $('.selector').find('a.select').on('click', function (event) {
        event.preventDefault();
        var $this = $(this),
            $parent = $this.parent();
        if ($parent.hasClass('active')) {
            return;
        } else {
            $this.parent().addClass('active').siblings().removeClass('active');
            fetchLeaderboards();
        }
    });

    $('#select-past-leaderboard-months').on('change', function (event) {
        var $this = $(this);
        if (parseInt($this.val(), 10) === 0) {
            var $current_month = $('.selector').find('a.select.current-month');
            $current_month.parent().addClass('active');
            //$('.selector').trigger('click');
        } else {
            $('.timespan.select').each(function (i, o) {
                $(o).parent().removeClass('active');
            });
        }
        fetchLeaderboards();
    });

    fetchLeaderboards();
}());