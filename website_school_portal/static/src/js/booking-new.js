/* global $, moment, date_today, date_tomorrow, toastr */
(function () {
    "use strict";
    $(document).ready(function () {
        function lpad(str, size) {
            str = String(str);
            return new Array(size - str.length + 1).join("0") + str;
        }

        function datetime_to_str(obj) {
            if (!obj) {
                return false;
            }
            return (
                lpad(obj.getUTCFullYear(), 4) +
                "-" +
                lpad(obj.getUTCMonth() + 1, 2) +
                "-" +
                lpad(obj.getUTCDate(), 2) +
                " " +
                lpad(obj.getUTCHours(), 2) +
                ":" +
                lpad(obj.getUTCMinutes(), 2) +
                ":" +
                lpad(obj.getUTCSeconds(), 2)
            );
        }

        function updateSendButton() {
            if ($("#room").val() > 0) {
                $("#request-booking").removeAttr("disabled");
            } else {
                $("#request-booking").attr("disabled", true);
            }
        }

        function updateRoomList() {
            var fromTime = $("#from_hour").val();
            var toTime = $("#to_hour").val();
            $("#room").val(0);
            if (fromTime < toTime) {
                var start = date_today
                    .clone()
                    .set("hour", fromTime.slice(0, 2))
                    .set("minutes", fromTime.slice(-2))
                    .set("seconds", 0)
                    .set("milliseconds", 0);
                var stop = date_today
                    .clone()
                    .set("hour", toTime.slice(0, 2))
                    .set("minutes", toTime.slice(-2))
                    .set("seconds", 0)
                    .set("milliseconds", 0);
                var selected_date = $("#selected_date").attr("value");
                if (selected_date == 0) {
                    var day = $("#day").attr("value");
                    if (day == 1) {
                        start = date_tomorrow
                            .clone()
                            .set("hour", fromTime.slice(0, 2))
                            .set("minutes", fromTime.slice(-2))
                            .set("seconds", 0)
                            .set("milliseconds", 0);
                        stop = date_tomorrow
                            .clone()
                            .set("hour", toTime.slice(0, 2))
                            .set("minutes", toTime.slice(-2))
                            .set("seconds", 0)
                            .set("milliseconds", 0);
                    }
                } else {
                    start = moment(selected_date)
                        .set("hour", fromTime.slice(0, 2))
                        .set("minutes", fromTime.slice(-2))
                        .set("seconds", 0)
                        .set("milliseconds", 0);
                    stop = moment(selected_date)
                        .set("hour", toTime.slice(0, 2))
                        .set("minutes", toTime.slice(-2))
                        .set("seconds", 0)
                        .set("milliseconds", 0);
                }
                $.ajax({
                    type: "POST",
                    dataType: "json",
                    contentType: "application/json",
                    url: "/booking/rooms",
                    data: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {
                            start: start.toISOString(),
                            end: stop.toISOString(),
                            self_id: 0,
                        },
                        id: Math.floor(Math.random() * 100000000),
                    }),
                    success: function (result) {
                        $("#room").empty().html(" ");
                        $("#room").append(
                            $("<option></option>")
                                .attr("value", 0)
                                .text("Selectionnez un local...")
                        );
                        var rooms = result.result;
                        if (rooms.length > 0) {
                            $("#room").removeAttr("disabled");
                            for (var room_idx in rooms) {
                                var room = rooms[room_idx];
                                $("#room").append(
                                    $("<option></option>")
                                        .attr("value", room.id)
                                        .text(room.name)
                                );
                            }
                        } else {
                            $("#room").addAttr("disabled", true);
                        }
                    },
                });
            }
        }

        function updateSelectHours() {
            var from_hour_select = document.querySelector("#from_hour");
            var to_hour_select = document.querySelector("#to_hour");

            for (var i = 0; i < from_hour_select.options.length; i++) {
                to_hour_select[i].disabled = from_hour_select.selectedIndex > i;
            }

            if (
                from_hour_select.selectedIndex < from_hour_select.options.length &&
                from_hour_select.selectedIndex >= to_hour_select.selectedIndex
            ) {
                to_hour_select.selectedIndex = from_hour_select.selectedIndex;
            }
        }

        $("#today").on("click", function () {
            $("#today").addClass("bg-danger border border-danger border-0");
            $("#tomorrow").removeClass("bg-danger border border-danger border-0");
            $("#day").prop("value", "0");
            updateRoomList();
            updateSendButton();
        });

        $("#tomorrow").on("click", function () {
            $("#today").removeClass("bg-danger border border-danger border-0");
            $("#tomorrow").addClass("bg-danger border border-danger border-0");
            $("#day").prop("value", "1");
            updateRoomList();
            updateSendButton();
        });

        $("#from_hour").on("change", function () {
            updateSelectHours();
            updateRoomList();
            updateSendButton();
        });

        $("#to_hour").on("change", function () {
            updateSelectHours();
            updateRoomList();
            updateSendButton();
        });

        $("#room").on("change", function () {
            updateSendButton();
        });

        $("#request-booking").on("click", function (event) {
            event.preventDefault();
            var fromTime = $("#from_hour").val();
            var toTime = $("#to_hour").val();
            var start = date_today
                .clone()
                .set("hour", fromTime.slice(0, 2))
                .set("minutes", fromTime.slice(-2))
                .set("seconds", 0)
                .set("milliseconds", 0);
            var stop = date_today
                .clone()
                .set("hour", toTime.slice(0, 2))
                .set("minutes", toTime.slice(-2))
                .set("seconds", 0)
                .set("milliseconds", 0);
            var selected_date = $("#selected_date").attr("value");
            if (selected_date == 0) {
                var day = $("#day").attr("value");
                if (day == 1) {
                    start = date_tomorrow
                        .clone()
                        .set("hour", fromTime.slice(0, 2))
                        .set("minutes", fromTime.slice(-2))
                        .set("seconds", 0)
                        .set("milliseconds", 0);
                    stop = date_tomorrow
                        .clone()
                        .set("hour", toTime.slice(0, 2))
                        .set("minutes", toTime.slice(-2))
                        .set("seconds", 0)
                        .set("milliseconds", 0);
                }
            } else {
                start = moment(selected_date)
                    .set("hour", fromTime.slice(0, 2))
                    .set("minutes", fromTime.slice(-2))
                    .set("seconds", 0)
                    .set("milliseconds", 0);
                stop = moment(selected_date)
                    .set("hour", toTime.slice(0, 2))
                    .set("minutes", toTime.slice(-2))
                    .set("seconds", 0)
                    .set("milliseconds", 0);
            }
            var room = $("#room").val();
            var description = $("#description").val();
            var event_type = $("#event_type").val();

            start.locale("fr");
            $.ajax({
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                url: "/web/dataset/call_kw/calendar.event/create",
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {
                        model: "calendar.event",
                        method: "create",
                        args: [
                            {
                                name: description,
                                start: datetime_to_str(start.toDate()),
                                stop: datetime_to_str(stop.toDate()),
                                room_id: parseInt(room),
                                categ_ids: [[4, parseInt(event_type)]],
                            },
                        ],
                        kwargs: {},
                    },
                    id: Math.floor(Math.random() * 100000000),
                }),
                success: function (result) {
                    if (result.error) {
                        $("#horizon-error").empty().html(result.error.data.message);
                        $("#horizon-error").toggle();
                    } else {
                        toastr.options = {
                            closeButton: false,
                            debug: false,
                            newestOnTop: false,
                            progressBar: false,
                            positionClass: "toast-top-right",
                            preventDuplicates: false,
                            onclick: null,
                            showDuration: "300",
                            hideDuration: "1000",
                            timeOut: "2000",
                            extendedTimeOut: "1000",
                            showEasing: "swing",
                            hideEasing: "linear",
                            showMethod: "fadeIn",
                            hideMethod: "fadeOut",
                            onHidden: function () {
                                window.location.href = "/reservations/mes-reservations";
                            },
                        };
                        toastr.success(
                            "Votre réservation pour le " +
                                start.format("L") +
                                " à " +
                                fromTime +
                                " a bien été enregistrée."
                        );
                    }
                },
            });
        });
    });
})();
