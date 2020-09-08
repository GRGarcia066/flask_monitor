function assets()
{
    $.get({
        url: '/clients/all_assets/' + project_id,
        success: function (data) 
        {
            $("#assets").html(data);
        },
        error: function (error) 
        {            
            switch(error.status)
            {
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("El servidor está desconectado.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error al intentar recuperar los asset, para más informacion consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function client_assets()
{
    $.get({
        url: '/clients/assets/' + client_id,
        success: function (data) 
        {
            $("#client_assets").html(data);
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("El servidor está desconectado.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error al intentar recuperar los asset, para más informacion consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function addAsset(asset_id) 
{
    $.post({
        url: '/assets/upload/' + client_id + '/' + asset_id,
        success: function () 
        {
            client_assets(client_id);
            alertify.success("Operación completada con éxito.");
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 401 /*UNAUTHORIZED*/:
                    alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                    break;

                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("La pantalla está desconectada.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error al intentar añadir el asset, para más información consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function delAsset(asset_id) 
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea eliminarlo?',

    function()
    { 
        $.ajax({
            url: '/assets/'+ asset_id,
            type: 'DELETE',
            success: function () {
                window.location.reload();
            },
            error: function (error) 
            {
                switch(error.status)
                {
                    case 401 /*UNAUTHORIZED*/:
                        alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                        break;

                    case 408 /*REQUEST TIMEOUT*/:
                        alertify.error("La pantalla está desconectada.");
                        break;

                    default:
                        alertify.error("Ha ocurrido un error, para más información consulte los registros de la aplicación.");
                        break;
                }
                console.log(error);
            }
        });
    }, 
    function() {});
};

function delClient(client_id) 
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea eliminarlo?',

    function()
    { 
        $.ajax({
            url: '/clients/'+ client_id,
            type: 'DELETE',
            success: function (data) {
                window.location.reload();
            },
            error: function (error) 
            {
                switch(error.status)
                {
                    case 401 /*UNAUTHORIZED*/:
                        alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                        break;
                        
                    case 408 /*REQUEST TIMEOUT*/:
                        alertify.error("La pantalla está desconectada.");
                        break;

                    default:
                        alertify.error("Ha ocurrido un error, para más información consulte los registros de la aplicación.");
                        break;
                }
                console.log(error);
            }
        });
    }, 
    function() {});
};

function enableAsset(client_id, asset_id) 
{
    $.ajax({
        url: '/assets/enable/' + client_id + '/' + asset_id,
        type: 'PUT',
        success: function () 
        {
            getAssetsTable(client_id);
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 401 /*UNAUTHORIZED*/:
                    alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                    break;
                    
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("La pantalla que trata de controlar está desconectada.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error al intentar controlar la pantalla, para más información consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function controlAsset(client_id, command, asset_id = null) 
{
    let url;
    if (command != 'asset')
        url = '/assets/control/' + client_id + '/' + command;
    else
        url = '/assets/control/' + client_id + '/' + command + '&' + asset_id;

    $.post({
        url: url,
        success: function () 
        {
            clearTimeout(cardtimeout);
            cardtimeout = setTimeout(getScreenshot, 500, client_id);
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 401 /*UNAUTHORIZED*/:
                    alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                    break;
                    
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("La pantalla que trata de controlar está desconectada.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error al intentar controlar la pantalla, para más información consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function getScreenshot(client_id) 
{
    let image = $("img#img-" + client_id);
    let card_status = $("#client-" + client_id + "-status");

    $.get({
        url: '/assets/screenshot/' + client_id,
        success: function (data)
        {
            card_status.attr("class", "badge badge-success");
            card_status.html('conectado');
            image.attr("src", "data:image/png;base64," + data[0]);
            cardtimeout = setTimeout(getScreenshot, check_timer, client_id);
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 401 /*UNAUTHORIZED*/:
                    alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                    card_status.attr("class", "badge badge-danger");
                    card_status.html('no autorizado');
                    break;
                    
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("La pantalla está desconectada.");
                    card_status.attr("class", "badge badge-danger");
                    card_status.html('desconectado');
                    break;

                default:
                    alertify.error("Ha ocurrido un error, para más información consulte los registros de la aplicación.");
                    card_status.attr("class", "badge badge-danger");
                    card_status.html('error');
                    break;
            }
            image.attr("src", "/static/img/no-image-available.jpg");
            console.log(error);
        }
    });
};

function reCheck(client_id) 
{
    clearTimeout(cardtimeout);
    cardtimeout = setTimeout(getScreenshot, 1000, client_id);
};

function turnOnOff(client_id, status, option) 
{
    $.post({
        url: '/clients/display/' + client_id + '/' + status + '/' + option,
        success: function () 
        {
            alertify.success("Operación completada con éxito.");
        },
        error: function (error) 
        {
            switch(error.status)
            {
                case 401 /*UNAUTHORIZED*/:
                    alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                    break;
                    
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("La pantalla que trata de apagar/encender está desconectada.");
                    break;

                default:
                    alertify.error("Ha ocurrido un error al intentar apagar/encender la pantalla, para más información consulte los registros de la aplicación.");
                    break;
            }
            console.log(error);
        }
    });
};

function UpdateCheckInterval(client_id)
{
    let value = $("input#addon_check_interval")[0].value;

    $.post({
        url: "/clients/update/" + client_id + "/" + value * 1000,
        success: function() 
        {
            alertify.success('Se ha actualizado con éxito el intervalo.');
            check_timer = value * 1000;
            clearTimeout(cardtimeout);
        },
        error: function(error) 
        {
            switch(error.status)
            {
                case 408 /*REQUEST TIMEOUT*/:
                    alertify.error("El servidor está desconectado.");
                    break;

                default:
                    alertify.error('Ha ocurrido un error durante la actualización, para más información consulte los registros de la aplicación.');
                    break;
            }
            console.log(error);
        }
    });
};

function delClientAsset(asset_id) 
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea eliminarlo?', 

    function() 
    { 
        $.ajax({
            url: '/assets/'+ client_id + '/' + asset_id,
            type: 'DELETE',
            statusCode: {
                200: function() {
                    alertify.warning("No existe el asset con id: " + asset_id + " en el cliente.");
                    client_assets(client_id);
                },
                204: function() {
                    alertify.success("Asset eliminado con éxito");
                    client_assets(client_id);
                }
            },
            error: function (error) 
            {
                switch(error.status)
                {
                    case 401 /*UNAUTHORIZED*/:
                        alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                        break;
                        
                    case 408 /*REQUEST TIMEOUT*/:
                        alertify.error("La pantalla está desconectada.");
                        break;

                    default:
                        alertify.error("Ha ocurrido un error al intentar eliminar el asset, para más información consulte los registros de la aplicación.");
                        break;
                }
                console.log(error);
            }
        });
    }, 
    function() {});
};

function delClientAsset2(client_id, asset_id) 
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea eliminarlo?', 

    function() 
    { 
        $.ajax({
            url: '/assets/'+ client_id + '/' + asset_id,
            type: 'DELETE',
            statusCode: {
                200: function() {
                    alertify.warn("No existe el asset con id: " + asset_id + " en el cliente.");
                    getAssetsTable(client_id);
                },
                204: function() {
                    alertify.success("Asset eliminado con éxito");
                    getAssetsTable(client_id);
                }
            },
            error: function (error) 
            {
                switch(error.status)
                {
                    case 401 /*UNAUTHORIZED*/:
                        alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                        break;
                        
                    case 408 /*REQUEST TIMEOUT*/:
                        alertify.error("La pantalla está desconectada.");
                        break;

                    default:
                        alertify.error("Ha ocurrido un error al intentar eliminar el asset, para más información consulte los registros de la aplicación.");
                        break;
                }
                console.log(error);
            }
        });
    },
    function() {});
};

function getAssetsTable(client_id)
{
    $.get({
        url: '/clients/table/' + client_id,
        success: function (data) 
        {
            $("div#assets_table").html(data);
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

function shutdownScreenly(client_id) 
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea apagarlo?', 
    function() 
    {         
        $.post({
            url: '/clients/shutdown/' + client_id,
            success: function (data) 
            {
                alertify.success("Operación completada con éxito.");
            },
            error: function (error) 
            {
                switch(error.status)
                {
                    case 401 /*UNAUTHORIZED*/:
                        alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                        break;
                        
                    case 408 /*REQUEST TIMEOUT*/:
                        alertify.error("La pantalla está desconectada.");
                        break;

                    default:
                        alertify.error("Ha ocurrido un error al intentar eliminar el asset, para más información consulte los registros de la aplicación.");
                        break;
                }
            }
        });
    },
    function() {});
};

function rebootScreenly(client_id) 
{
    alertify.confirm('Eliminar', '¿Está seguro de que desea reiniciarlo?', 
    function() 
    {         
        $.post({
            url: '/clients/reboot/' + client_id,
            success: function (data) 
            {
                alertify.success("Operación completada con éxito.");
            },
            error: function (error) 
            {
                switch(error.status)
                {
                    case 401 /*UNAUTHORIZED*/:
                        alertify.error("El nombre de usuario o contraseña del cliente son incorrectos.");
                        break;
                        
                    case 408 /*REQUEST TIMEOUT*/:
                        alertify.error("La pantalla está desconectada.");
                        break;

                    default:
                        alertify.error("Ha ocurrido un error al intentar eliminar el asset, para más información consulte los registros de la aplicación.");
                        break;
                }
            }
        });
    },
    function() {});
};

var cardtimeout;
var check_timer;
var project_id;
var client_id;
var csrf_token;
