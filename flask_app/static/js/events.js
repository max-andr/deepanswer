// Enter for input field
$("#question-field").keyup(function (event) {
    if (event.keyCode == 13) {
        $("#question-btn").click();
    }
});

$body = $("body");
$(document).on({
    ajaxStart: function () {
        $body.addClass("loading");
    },
    ajaxStop: function () {
        $body.removeClass("loading");
    }
});


$(document).ready(function () {
    $('#feedback-btn-group').on('click', function () {
        $('#feedback-frame').addClass('hidden');
    });
    $('#btn-no').on('click', function () {
        set_feedback(false);
    });
    $('#btn-yes').on('click', function () {
        set_feedback(true);
    });
    // AJAX on click
    $('#question-btn').on('click', function () {
        get_answer();
    });
    $('#question-hint-text1').on('click', function () {
        var question_hint_text = $('#question-hint-text1').text();
        console.log(question_hint_text);
        $('#question-field').val(question_hint_text);
        get_answer();
    });
    $('#question-hint-text2').on('click', function () {
        var question_hint_text = $('#question-hint-text2').text();
        console.log(question_hint_text);
        $('#question-field').val(question_hint_text);
        get_answer();
    });
    $('#question-microphone').on('click', function () {
        var recognition = new webkitSpeechRecognition();
        recognition.lang = "ru-RU";
        // recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = function (event) {
            var text_from_speech = event['results'][0][0]['transcript'];
            $('#question-field').val(text_from_speech);
            console.log(event);
            console.log(text_from_speech);
        };
        recognition.onend = function (event) {
            get_answer();
            $('#question-microphone').css('background-color', 'orangered');
        };
        $('#question-microphone').css('background-color', 'gray');
        recognition.start();
    });
});






