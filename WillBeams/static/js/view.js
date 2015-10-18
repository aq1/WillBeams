function bindToggleButton(elm, url, activeClass, webmId){
    var busy = false;
    webmId = parseInt(webmId);

    function setState(v){
        if (v){
            elm.removeClass('btn-default').addClass(activeClass).addClass('active');
        } else {
            elm.addClass('btn-default').removeClass(activeClass).removeClass('active');
        }
        currentState = v;
    }

    function detectState(){
        return elm.hasClass('active');
    }

    var currentState = detectState();

    elm.click(function(){
        if (busy) return;
        busy = true;
        elm.prop('disabled', true);
        $.ajax(url, {
            method: 'POST',
            data: {
                id: webmId,
                state: !currentState,
            },
            success: function(resp){
                setState(resp);
            },
            complete: function(){
                elm.prop('disabled', false);
                busy = false;
            },
        });
    });
}

$(function(){
    $('[toggler-url]').each(function(){
        var j = $(this);
        bindToggleButton(
            j,
            j.attr('toggler-url'),
            j.attr('data-aclass'),
            j.attr('data-webm-id')
        );
    });
});

// bindToggleButton('#fav', '{# url "newapp.views.toggle_favourite" #}', 'btn-success');
// bindToggleButton('#nsfw', '{# url "newapp.views.toggle_nsfw" #}', 'btn-warning');
