from flask import Blueprint, render_template, redirect, Response, g, flash
from flask_login import login_required
from flask_api import status
from app import screenly_api
from app.mqtt import mqtt_client
from app.models import Project, Action, Subscription, Asset, db
from app.forms import SubscriptionForm, UpdateSubscriptionForm

# Define the blueprint: 'subs', set its url prefix: app.url /subscriptions
bp = Blueprint('subs', __name__, url_prefix='/subscriptions')


@bp.route('/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_subscription(project_id):
    """
    Allows user to creates a new subscriptions.
    """
    project = Project.query.get_or_404(project_id)
    g.project = project
    form = SubscriptionForm()
    if form.validate_on_submit():
        action = Action(name=form.name.data)
        if form.operator.data:
            action.operator = form.operator.data
        if form.value.data:
            action.value = form.value.data
        if form.extra_param_1.data:
            action.extra_param_1 = str(form.extra_param_1.data)
        if form.extra_param_2.data:
            action.extra_param_2 = str(form.extra_param_2.data)
        if form.extra_param_3.data:
            action.extra_param_3 = str(form.extra_param_3.data)
        if form.clients.data:
            for client in form.clients.data:
                action.clients.append(client)

        if action.name == "Reproducir Asset":
            asset = Asset.query.get_or_404(action.extra_param_2)
            for client in action.clients:
                if asset not in client.assets:
                    r = screenly_api.upload_asset(client.id, asset.id)
                    if r.status_code != status.HTTP_200_OK:
                        flash(
                        """
                        El cliente {} con IP {} no tiene el Asset que desea
                        reproducir y no es posible agregarlo en estos momentos.
                        """.format(client.name, client.address), 'error')
                        return render_template('subscriptions/new_subscription.html', project=project, form=form)

        subscription = Subscription.query.filter_by(topic=form.topic.data).first()
        if subscription is None:
            subscription = Subscription(project=project, topic=form.topic.data, status = 1)          

        subscription.actions.append(action)
        db.session.add(action)
        db.session.add(subscription)
        db.session.commit()
        return redirect('/projects/{}/subscriptions'.format(project.name))

    if form.errors:
        for error in form.errors:
            print(error)
        render_template('subscriptions/new_subscription.html', project=project, form=form), status.HTTP_303_SEE_OTHER

    return render_template('subscriptions/new_subscription.html', project=project, form=form)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subscription(id):
    """
    Allows user to edit an existing subscription.
    """
    subscription = Subscription.query.get_or_404(id)
    project = subscription.project
    g.project = project
    form = UpdateSubscriptionForm()
    if form.validate_on_submit():
        if form.status.data:
            subscription_status = form.status.data
            if subscription_status < 0:
                if subscription.status == 0:
                    subscription_status = 1
                else:
                    subscription_status = 0
            subscription.status = subscription_status
        db.session.commit()
        return Response(status=status.HTTP_200_OK)
    
    return render_template('subscriptions/edit_subscription.html', project=project, subscription=subscription, form=form)


@bp.route('/<int:id>/<int:action_id>', methods=['DELETE'])
@login_required
def delete_subscription(id, action_id):
    """
    Allows user to delete an existing subscription.
    """
    subscription = Subscription.query.get_or_404(id)
    action = Action.query.get_or_404(action_id)
    
    if action in subscription.actions:
        subscription.actions.remove(action)
    
    if len(subscription.actions) == 0:
        try:
            mqtt_client.remove_subscription(subscription)    
            db.session.delete(subscription)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        try:
            mqtt_client.update_subscription(subscription)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    db.session.commit()
    return Response(status=status.HTTP_200_OK)


@bp.route('/<int:id>', methods=['GET'])
@login_required
def subscription(id):
    """
    Retrieve information about an existing subscription.
    """
    subscription = Subscription.query.get(id)
    return render_template('subscriptions/subscription.html', subscription=subscription)
