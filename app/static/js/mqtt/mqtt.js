function getCredentialsForm()
{
    $.get({
        url: '/mqtt/credentials',
        success: function (data) {
            $("div#credentials").html(data);
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("El servidor está desconectado.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error, para más información consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function ActivateMQTT(status)
{
    $.post({
        url: "/mqtt/"+status,
        success: function() {
            if (status == 1)
                alertify.success('Se ha conectado con éxito a mqtt.');
            else
                alertify.success('Se ha detenido con éxito la conexión.');
        },
        error: function(data){
            alertify.error(data.responseText);
            console.log(data);
        }
    });
};
