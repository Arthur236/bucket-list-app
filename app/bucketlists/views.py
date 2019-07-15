import re

from flask.views import MethodView
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import func

from . import bucketlists_blueprint
from app.models import Bucketlist, User
from ..decorators import MyDecorator

my_dec = MyDecorator()


class BucketlistView(MethodView):
    """
      Handles bucketlist creation and retrieval
    """
    @staticmethod
    def post():
        """
        Creates bucketlists
        """
        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        name = str(request.form.get('name', ''))
        description = str(request.form.get('description', ''))

        if name:
            if not re.match("^[a-zA-Z0-9 _]*$", name):
                flash("The list name cannot contain special characters. Only underscores (_)")
                return redirect(url_for('bucketlists.bucketlist_view'))

            b_list = Bucketlist.query. \
                filter(func.lower(Bucketlist.name) == name.lower(),
                        Bucketlist.user_id == user_id).first()

            if not b_list:
                # There is no list so we'll try to create it
                buckelist = Bucketlist(user_id=user_id, name=name, description=description)
                buckelist.save()

                flash("Bucketlist created successfully")
                return redirect(url_for('bucketlists.bucketlist_view'))

            flash("That bucketlist already exists")
            return redirect(url_for('bucketlists.bucketlist_view'))

        flash("Bucketlist name not provided")
        return redirect(url_for('bucketlists.bucketlist_view'))

    @staticmethod
    def get():
        """
        Retrieves bucketlists
        """
        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        page = int(request.args.get('page', 1))
        limit = 10

        total_lists = Bucketlist.query.filter_by(user_id=user_id).count()
        recent_lists = Bucketlist.query.filter_by(user_id=user_id). \
            order_by(Bucketlist.date_modified.desc()).limit(6)
        paginated_lists = Bucketlist.query.filter_by(user_id=user_id). \
            order_by(Bucketlist.name.asc()).paginate(page, limit)
        results = []

        if paginated_lists:
            for bucketlist in paginated_lists.items:
                obj = {
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'description': bucketlist.description,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                }
                results.append(obj)

        return render_template('bucketlists.html', bucketlists=results, recent_lists=recent_lists,
                               total_lists=total_lists)


bucketlist_view = BucketlistView.as_view('bucketlist_view')  # pylint: disable=invalid-name
# bucketist_manipulation = BucketistManipulation.as_view('bucketist_manipulation')  # pylint: disable=invalid-name


# Define rules
bucketlists_blueprint.add_url_rule('/bucketlists',
                                     view_func=bucketlist_view, methods=['POST', 'GET'])
# bucketlists_blueprint.add_url_rule('/bucketlists/<list_id>',
#                                      view_func=bucketist_manipulation, methods=['GET', 'PUT', 'DELETE'])
