$.ajax({
  url: "/announcements",
  type:"POST",
  contentType:"application/json",
  dataType:"json",
  data:"{}",
}).done(function( data ) {
    console.log(data);
    $.each(data.result, function(i, announcement) {
        $('<div class="mdl-card mdl-cell mdl-cell--12-col mdl-shadow--2dp">').append(
            $('<div class="mdl-card__title">').append(
                announcement.author_avatar ? $('<img alt="Avatar" class="mdl-list__item-avatar">').attr("src","/web/image/res.partner/"+announcement.author_id[0]+"/image_small") : $('<i class="material-icons mdl-list__item-avatar">').text("person"),
                $('<span style="padding-left:10px;">').text(announcement.author_id[1]))).append(
                $('<div class="mdl-card__supporting-text">').html(announcement.body)
                ).appendTo('.announcements-list');
    });
    
});