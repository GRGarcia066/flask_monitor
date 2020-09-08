function getTopicForm(project_id, topic_form)
{
    $.get({
        url: '/topics/new/' + project_id,
        success: function (data) {
            $(topic_form).html(data);
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("El servidor está desconectado.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error, para más informacion consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function GetTopicsStructure(project_id) 
{
    return $.get('/topics/json/' + project_id);
};

function GetSubtopics(topic_id) 
{
    return $.get('/topics/subtopics/'+ topic_id);
};

function delTopic(topic_id) 
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea eliminarlo?',

    function() 
    { 
        $.ajax({
            url: '/topics/'+ topic_id,
            type: 'DELETE',
            success: function () {
                window.location.reload();
            },
            error: function (error) 
            {
                switch(error.status)
                {
                    case 408 /*REQUEST TIMEOUT*/:
                        alertify.error("El servidor está desconectado.");
                        break;
    
                    default:
                        alertify.error("Ha ocurrido un error, para más informacion consulte los registros de la aplicación.");
                        break;
                }
                console.log(error);
            }
        });
    },
    function() {});
}
