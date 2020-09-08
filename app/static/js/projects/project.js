function getClientForm(project_id, client_form)
{
    $.get({
        url: '/clients/new/' + project_id,
        success: function (data) {
            $(client_form).html(data);
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

function getCategoryForm(project_id, category_form)
{
    $.get({
        url: '/categories/new/' + project_id,
        success: function (data) {
            $(category_form).html(data);
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

function getAssetForm(project_id, asset_form)
{
    $.get({
        url: '/assets/new/' + project_id,
        success: function (data) {
            $(asset_form).html(data);
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

function closeSelect2()
{
    $(".selectpicker").select2("close");
};
