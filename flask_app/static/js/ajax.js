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
                var error = answer_object['error'] || '';
                $('#answer-text').text(answer);
                if (image == '') {
                    $('#answer-img').addClass('hidden');
                }
                else {
                    $('#answer-img').attr("src", image);
                    $('#answer-img').removeClass('hidden');
                }
                $('#answer').removeClass('hidden');
                console.log(error);
                if (!error) {
                    console.log(error);
                    $('#feedback-frame').removeClass('hidden');
                }
                else {
                    $('#feedback-frame').addClass('hidden');
                }

                var utterance = new SpeechSynthesisUtterance(answer);
                utterance.lang = 'ru-RU';
                speechUtteranceChunker(utterance, {
                    chunkLength: 120
                }, function () {
                    //some code to execute when done
                    console.log('done');
                });
            } else {
                $('#answer-text').html("Ошибка соединения с сервером!");
            }
            $('#answer-text').removeClass('hidden');

        }
    });
}

function set_feedback(isCorrect) {
    var data = {};
    data['question'] = $('#question-field').val().trim();
    data['language'] = 'ru';
    data['isCorrect'] = isCorrect;
    console.log(data);
    $.ajax({
        method: 'POST',
        url: '/set_feedback',
        data: data
    });
}
