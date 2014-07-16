function FileThumbsBlock(runtime, element, data) {
    function updateVotes(votes) {
        $('.upvote .count', element).text(votes.up);
        $('.downvote .count', element).text(votes.down);
    }

    $('.upvote .arrow', element).html('<img height="14" width="10" src="'+data.uparrow+'"/>');
    $('.downvote .arrow', element).html('<img height="14" width="10" src="'+data.downarrow+'"/>');

    updateVotes(data)
    
    var handlerUrl = runtime.handlerUrl(element, 'vote');

    $('.upvote', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({voteType: 'up'}),
            success: updateVotes
        });
    });

    $('.downvote', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({voteType: 'down'}),
            success: updateVotes
        });
    });
};
