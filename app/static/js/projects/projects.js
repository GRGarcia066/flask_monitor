function getProjectForm()
{
    $.get({
        url: '/projects/new',
        success: function (data) {
            $("#project_form_content").html(data);
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

function delProject(project_id)
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea eliminarlo?',

    function()
    { 
        $.ajax({
            url: '/projects/'+ project_id,
            type: 'DELETE',
            success: function (data) {
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
};

$(document).ready(function () 
{ 
    getProjectForm(); 
});
