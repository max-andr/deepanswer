function get_answer() {
    var data = {};
    data['question'] = $('#question-field').val().trim();
    // Кто был научным руководителем Тьюринга?
    data['language'] = 'ru';
    console.log(data);
    $.ajax({
        method: 'GET',
        url: '/get_answer',
        data: data,
        success: function (answer_json) {
            var answer_object = JSON.parse(answer_json);
            console.log(answer_object);
            if (typeof(answer_object) != "undefined") {
                var answer = answer_object['answer'];
                var image = answer_object['image'] || '';
                $('#answer-text').text(answer);
                $('#answer-img').attr("src", image);
                $('#answer').removeClass('hidden');
            } else {
                $('#answer-text').html("Ошибка!");
            }
            $('#answer-text').removeClass('hidden');

        }
    });
}

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
    // AJAX on click
    $('#question-btn').on('click', function () {
        get_answer();
    });
    $('#question-hint').on('click', function () {
        var question_hint_text = $('#question-hint-text').text();
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
        };
        recognition.start();
    });
});

