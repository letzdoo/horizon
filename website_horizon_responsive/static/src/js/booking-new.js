$(document).ready(function(){
    
    function updateSendButton() {
        if($('#room').val() > 0) {
            $('#request-booking').removeAttr( 'disabled' );
        } else {
            $('#request-booking').attr( 'disabled', true );
        }
    }
    
    function updateRoomList() {
        var self = this;
        var fromTime = $('#from_hour').timepicker('getTime');
        var toTime = $('#to_hour').timepicker('getTime');
        if (fromTime < toTime) {
            var start = moment().local().set('hour',fromTime.getHours()).set('minutes',fromTime.getMinutes()).set('seconds',0).set('milliseconds',0);
            var stop = moment().local().set('hour',toTime.getHours()).set('minutes',toTime.getMinutes()).set('seconds',0).set('milliseconds',0);
            var day = $('#day').attr('value');
            if( day == 1 ) {
                start.add(1, 'days');
                stop.add(1, 'days');
            }
            $.ajax({
              type: "POST",
              dataType: "json",
              contentType: 'application/json',
              url: '/booking/rooms',
              data: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    "start": start.toISOString(),
                    "end": stop.toISOString(),
                    "self_id": 0,
                },
                id: Math.floor(Math.random()*100000000),
              }),
              success: function( result ) {
                console.log(result);
                $('#room').empty().html(' ');
                $('#room').append(
                  $("<option></option>")
                    .attr("value",0)
                    .text('Selectionnez un local...')
                );
                var rooms = result.result;
                if(rooms.length > 0) {
                    $('#room').removeAttr( "disabled" )
                    for(var room_idx in rooms) {
                        var room = rooms[room_idx];
                        $('#room').append(
                          $("<option></option>")
                            .attr("value",room.id)
                            .text(room.name)
                        );
                    }    
                } else {
                    $('#room').addAttr( "disabled", true);
                }
              }
            });
        }
    }
    
	$('#from_hour').timepicker({
        'timeFormat': 'H:i',
        'minTime': '8:00',
        'maxTime': '21:30',
    });
    
    $('#to_hour').timepicker({
        'timeFormat': 'H:i',
        'minTime': '8:30',
        'maxTime': '22:00',
        'showDuration': true,
    });
    
    $('#today').on('click',function() {
        $('#today').addClass("bg-danger border border-danger border-0")
        $('#tomorrow').removeClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "0" );
        updateRoomList();
        updateSendButton();
    });
    
    $('#tomorrow').on('click',function() {
        $('#today').removeClass("bg-danger border border-danger border-0")
        $('#tomorrow').addClass("bg-danger border border-danger border-0")
        $('#day').prop( "value", "1" );
        updateRoomList();
        updateSendButton();
    });
    
    $('#from_hour').on('change', function() {
        var fromTime = $('#from_hour').timepicker('getTime');
        var toTime = $('#to_hour').timepicker('getTime');
        $('#to_hour').timepicker('option', 'minTime', fromTime);
        if (fromTime > toTime) {
            $('#to_hour').timepicker('setTime', fromTime);
        }
        updateRoomList();
        updateSendButton();
    });
    
    $('#to_hour').on('change', function() {
        updateRoomList();
        updateSendButton();
    });
    
    $('#room').on('change', function() {
        updateSendButton();
    });
    
    $('#request-booking').on('click',function() {
        var fromTime = $('#from_hour').timepicker('getTime');
        var toTime = $('#to_hour').timepicker('getTime');
        var start = moment().local().set('hour',fromTime.getHours()).set('minutes',fromTime.getMinutes()).set('seconds',0).set('milliseconds',0);
        var stop = moment().local().set('hour',toTime.getHours()).set('minutes',toTime.getMinutes()).set('seconds',0).set('milliseconds',0);
        var day = $('#day').attr('value');
        if( day == 1 ) {
            start.add(1, 'days');
            stop.add(1, 'days');
        }
        var room = $('#room').val();
        var description  = $('#description').val();
        $.ajax({
            type: "POST",
            dataType: "json",
            contentType: 'application/json',
            url: '/web/dataset/call_kw/calendar.event/create',
            data: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: "calendar.event",
                    method: "create",
                    args: [{
                        name: description,
                        start: start.toISOString().replace('T',' '),
                        stop: stop.toISOString().replace('T',' '),
                        room_id: room,
                        categ_ids: [[4, 7]],
                    }],
                    kwargs: {}
                },
                id: Math.floor(Math.random()*100000000),
            }),
            success: function( result ) {
                window.location.href = "/responsive/bookings";
            },    
        });
    });
    
});