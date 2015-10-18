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

function bindTagBox(tagbox, webmId, url, elms){
    var busy = false;
    var btn = tagbox.find('button');
    var inp = tagbox.find('input[type=text]');

    btn.click(function(){
        if (busy) return;
        busy = true;
        btn.prop('disabled', true);
        inp.prop('disabled', true);
        $.ajax(url, {
            method: 'POST',
            data: {
                id: webmId,
                tags: inp.val().split(',').map(function(x){return x.trim();})
            },
            success: function(resp){
                inp.val(resp.join(', '));
            },
            complete: function(){
                btn.prop('disabled', false);
                inp.prop('disabled', false);
                busy = false;
            },
        });
    });
}

function deleteButton(elm, url, webmId){
    var busy = false;
    elm.click(function(){
        if (busy) return;
        busy = true;
        elm.addClass('disabled');
        $.ajax(url, {
            method: 'POST',
            data: {
                id: webmId
            },
            success: function(resp){
                $('#controls').hide();
                $('#tagbox').after('<div class="alert alert-danger">Удалено</div>').hide();
            },
            complete: function(){
                elm.removeClass('disabled');
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

    var t = $('#tagbox');
    bindTagBox(
        t,
        t.attr('data-webm-id'),
        t.attr('target-url')
    );

    t = $('#delete');
    if (t.length){
        deleteButton(
            t,
            t.attr('target-url'),
            t.attr('data-webm-id')
        );
    }
});
