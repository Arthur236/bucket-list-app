import re

from flask.views import MethodView
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import func

from . import bucket_lists_blueprint
from app.models import BucketList
from ..decorators import MyDecorator

my_dec = MyDecorator()


class BucketListView(MethodView):
    """Handles bucket_list creation and retrieval"""

    @staticmethod
    def post():
        """Creates bucket_lists"""

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
                return redirect(url_for('bucket_lists.bucket_list_view'))

            b_list = BucketList.query. \
                filter(func.lower(BucketList.name) == name.lower(),
                       BucketList.user_id == user_id).first()

            if not b_list:
                # There is no list so we'll try to create it
                bucket_list = BucketList(user_id=user_id, name=name, description=description)
                bucket_list.save()

                flash("Bucket list created successfully")
                return redirect(url_for('bucket_lists.bucket_list_view'))

            flash("That bucket_list already exists")
            return redirect(url_for('bucket_lists.bucket_list_view'))

        flash("Bucket list name not provided")
        return redirect(url_for('bucket_lists.bucket_list_view'))

    @staticmethod
    def get():
        """Retrieves bucket_lists"""

        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        page = int(request.args.get('page', 1))
        limit = 10

        total_lists = BucketList.query.filter_by(user_id=user_id).count()
        recent_lists = BucketList.query.filter_by(user_id=user_id). \
            order_by(BucketList.date_modified.desc()).limit(6)
        paginated_lists = BucketList.query.filter_by(user_id=user_id). \
            order_by(BucketList.name.asc()).paginate(page, limit)
        results = []
        recent_results = []

        if recent_lists:
            for bucket_list in recent_lists:
                # Truncate long descriptions
                name_limit = 25
                description_limit = 90
                new_name = bucket_list.name[:name_limit] + '...' * (len(bucket_list.name) > name_limit)
                new_desc = bucket_list.description[:description_limit] + '...' * (
                            len(bucket_list.description) > description_limit)

                obj = {
                    'id': bucket_list.id,
                    'name': new_name,
                    'description': new_desc,
                    'date_created': bucket_list.date_created,
                    'date_modified': bucket_list.date_modified
                }
                recent_results.append(obj)

        if paginated_lists:
            for bucket_list in paginated_lists.items:
                obj = {
                    'id': bucket_list.id,
                    'name': bucket_list.name,
                    'description': bucket_list.description,
                    'date_created': bucket_list.date_created,
                    'date_modified': bucket_list.date_modified
                }
                results.append(obj)

        return render_template('bucket-lists.html', bucket_lists=results, recent_lists=recent_results,
                               total_lists=total_lists)


class BucketListRUD(MethodView):
    """Handles bucket_list read, update and delete"""

    @staticmethod
    def get(slug):
        """Retrieves a specific bucket_list"""

        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        bucket_list = BucketList.query.filter_by(user_id=user_id, slug=slug).first()

        if not bucket_list:
            flash("That bucket list does not exist")
            return redirect(url_for('bucket_lists.bucket_list_view'))

        if bucket_list.user_id == user_id:
            response = {
                'name': bucket_list.name,
                'description': bucket_list.description,
                'slug': bucket_list.slug,
                'date_created': bucket_list.date_created,
                'date_modified': bucket_list.date_modified
            }

            return render_template('bucket_list.html', bucket_list=response)


bucket_list_view = BucketListView.as_view('bucket_list_view')  # pylint: disable=invalid-name
# bucketist_manipulation = BucketistManipulation.as_view('bucketist_manipulation')  # pylint: disable=invalid-name


# Define rules
bucket_lists_blueprint.add_url_rule('/bucket-lists',
                                   view_func=bucket_list_view, methods=['POST', 'GET'])
# bucket_lists_blueprint.add_url_rule('/bucket-lists/<list_id>',
#                                      view_func=bucketist_manipulation, methods=['GET', 'PUT', 'DELETE'])
