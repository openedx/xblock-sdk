function ProblemBlock(runtime, element) {

    function callIfExists(obj, fn) {
        if (typeof obj[fn] == 'function') {
            return obj[fn].apply(obj, Array.prototype.slice.call(arguments, 2));
        } else {
            return undefined;
        }
    }

    function handleCheckResults(data) {
	// We have a closure so we can have both the results of AJAX
	// (whether answer is correct) and the submission (the answer
	// itself) in one place for eventing
        return function(results) {
            $.each(results.submitResults || {}, function(input, result) {
                callIfExists(runtime.childMap(element, input), 'handleSubmit', result);
            });
            var answers = {};
            var correct_map = {};
            $.each(results.checkResults || {}, function(checker, result) {
                for(var key in JSON.parse(JSON.stringify(data))) {
                    answers[checker] = data[key][0].value;
                }
                if(result) {
                    correct_map[checker] = {"correctness": "correct"};
                } else {
                    correct_map[checker] = {"correctness": "incorrect"};
                }
                callIfExists(runtime.childMap(element, checker), 'handleCheck', result);
            });
            var event = {"answers":answers,
			 "correct_map":correct_map};
            Logger.log("problem_check", event);

        };
    }

    // To submit a problem, call all the named children's submit()
    // function, collect their return values, and post that object
    // to the check handler.
    $(element).find('.check').bind('click', function() {
        var data = {};
        var children = runtime.children(element);
        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            if (child.name !== undefined) {
                data[child.name] = callIfExists(child, 'submit');
            }
        }
        var handlerUrl = runtime.handlerUrl(element, 'check');
        $.post(handlerUrl, JSON.stringify(data)).success(handleCheckResults(data));
    });

    $(element).find('.rerandomize').bind('click', function() {
        var handlerUrl = runtime.handlerUrl(element, 'rerandomize');
        $.post(handlerUrl, JSON.stringify({}));
    });
}
