/* global $, moment */

$(document).ready(function () {
    search();

    function search() {
        var query = $("#query").val();
        var day = $("#day").val();
        var start = moment()
            .local()
            .set("hour", 0)
            .set("minutes", 0)
            .set("seconds", 0)
            .set("milliseconds", 0);
        var stop = moment()
            .local()
            .set("hour", 23)
            .set("minutes", 59)
            .set("seconds", 59)
            .set("milliseconds", 0);
        if (day == 1) {
            start.add(1, "days");
            stop.add(1, "days");
        }
        $.ajax({
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            url: "/booking/search",
            data: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    start: start.toISOString(),
                    end: stop.toISOString(),
                    query: query,
                },
                id: Math.floor(Math.random() * 100000000),
            }),
            success: function (result) {
                console.log(result);
                $("#booking-list").empty();
                var list = result.result;
                if (list.length > 0) {
                    for (var idx in list) {
                        var li = list[idx];
                        $("#booking-list").append(
                            "<li><div class='d-flex justify-content-between'><span class='pr-3'>" +
                                moment.utc(li.start).local().format("HH:mm") +
                                "<span class='mx-1'>›</span>" +
                                moment.utc(li.stop).local().format("HH:mm") +
                                "</span><span>" +
                                li.name +
                                "</span><span>" +
                                li.room_id[1] +
                                "</span></div></li>"
                        );
                    }
                } else {
                    $("#booking-list").append("<li>Pas de résultat.</li>");
                }
            },
        });
    }

    $("#today").on("click", function () {
        $("#today").addClass("bg-danger border border-danger border-0");
        $("#tomorrow").removeClass("bg-danger border border-danger border-0");
        $("#day").prop("value", "0");

        search();
    });

    $("#tomorrow").on("click", function () {
        $("#today").removeClass("bg-danger border border-danger border-0");
        $("#tomorrow").addClass("bg-danger border border-danger border-0");
        $("#day").prop("value", "1");

        search();
    });

    $("#search-booking").on("click", function () {
        search();
    });
});
