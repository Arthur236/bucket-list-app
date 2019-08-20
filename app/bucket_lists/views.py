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
            flash('You need to be logged in to do that', 'error')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        name = str(request.form.get('name', ''))
        description = str(request.form.get('description', ''))

        if name:
            if not re.match("^[a-zA-Z0-9 _]*$", name):
                flash("The list name cannot contain special characters. Only underscores (_)", 'error')
                return redirect(url_for('bucket_lists.bucket_list_view'))

            b_list = BucketList.query. \
                filter(func.lower(BucketList.name) == name.lower(),
                       BucketList.user_id == user_id).first()

            if not b_list:
                # There is no list so we'll try to create it
                bucket_list = BucketList(user_id=user_id, name=name, description=description)
                bucket_list.save()

                flash("Bucket list created successfully", 'success')
                return redirect(url_for('bucket_lists.bucket_list_view'))

            flash("That bucket_list already exists", 'error')
            return redirect(url_for('bucket_lists.bucket_list_view'))

        flash("Bucket list name not provided", 'error')
        return redirect(url_for('bucket_lists.bucket_list_view'))

    @staticmethod
    def get():
        """Retrieves bucket_lists"""

        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that', 'error')
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
                    'name': new_name,
                    'description': new_desc,
                    'slug': bucket_list.slug,
                    'date_created': bucket_list.date_created,
                    'date_modified': bucket_list.date_modified
                }
                recent_results.append(obj)

        if paginated_lists:
            for bucket_list in paginated_lists.items:
                obj = {
                    'name': bucket_list.name,
                    'description': bucket_list.description,
                    'slug': bucket_list.slug,
                    'date_created': bucket_list.date_created,
                    'date_modified': bucket_list.date_modified
                }
                results.append(obj)

        return render_template('bucket-lists.html', bucket_lists=results, recent_lists=recent_results,
                               total_lists=total_lists, page=page, pages=paginated_lists.pages)


class BucketListReadUpdate(MethodView):
    """Handles bucket list read and update"""

    @staticmethod
    def get(slug):
        """Retrieves a specific bucket_list"""

        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that', 'error')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        bucket_list = BucketList.query.filter_by(user_id=user_id, slug=slug).first()

        if not bucket_list:
            flash("That bucket list does not exist", 'error')
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

    @staticmethod
    def post(slug):
        """Handles bucket list edit"""
        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that', 'error')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        bucket_list = BucketList.query.filter_by(user_id=user_id, slug=slug).first()

        if not bucket_list:
            flash("That bucket list does not exist", 'error')
            return redirect(url_for('bucket_lists.bucket_list_view'))

        name = str(request.form.get('name', '')) if str(request.form.get('name', '')) \
            else bucket_list.name
        description = str(request.form.get('description', '')) if \
            str(request.form.get('description', '')) else bucket_list.description

        if name:
            if not re.match("^[a-zA-Z0-9 _]*$", name):
                flash("The list name cannot contain special characters. Only underscores (_)", 'error')
                return redirect(url_for('bucket_lists.bucket_list_rnu', slug=bucket_list.slug))

            b_list = BucketList.query. \
                filter(func.lower(BucketList.name) == name.lower(),
                       BucketList.user_id == user_id).first()

            if b_list and b_list.id != bucket_list.id:
                flash("A list with that name already exists", 'error')
                return redirect(url_for('bucket_lists.bucket_list_rnu', slug=bucket_list.slug))

            if bucket_list.user_id == user_id:
                bucket_list.name = name
                bucket_list.description = description
                bucket_list.save()

                flash("Bucket list updated successfully", 'success')
                return redirect(url_for('bucket_lists.bucket_list_rnu', slug=bucket_list.slug))

            flash("An error occurred while updating the bucket list", 'error')
            return redirect(url_for('bucket_lists.bucket_list_rnu', slug=bucket_list.slug))


class BucketListDelete(MethodView):
    """Handles bucket list delete"""
    @staticmethod
    def post(slug):
        """Handles bucket list delete"""
        is_authenticated = my_dec.is_authenticated()

        if not is_authenticated['status']:
            flash('You need to be logged in to do that', 'error')
            return redirect(url_for('index'))

        user_id = is_authenticated['user_id']
        bucket_list = BucketList.query.filter_by(user_id=user_id, slug=slug).first()

        if not bucket_list:
            flash("That bucket list does not exist", 'error')
            return redirect(url_for('bucket_lists.bucket_list_view'))

        if bucket_list.user_id == user_id:
            bucket_list.delete()

            flash("Bucket list deleted successfully", 'success')
            return redirect(url_for('bucket_lists.bucket_list_view'))

        flash("You do not have permission to delete that bucket list", 'error')
        return redirect(url_for('bucket_lists.bucket_list_view'))


bucket_list_view = BucketListView.as_view('bucket_list_view')  # pylint: disable=invalid-name
bucket_list_rnu = BucketListReadUpdate.as_view('bucket_list_rnu')  # pylint: disable=invalid-name
bucket_list_delete = BucketListDelete.as_view('bucket_list_delete')  # pylint: disable=invalid-name

# Define rules
bucket_lists_blueprint.add_url_rule('/bucket-lists',
                                    view_func=bucket_list_view, methods=['POST', 'GET'])
bucket_lists_blueprint.add_url_rule('/bucket-lists/<slug>',
                                    view_func=bucket_list_rnu, methods=['GET', 'POST'])
bucket_lists_blueprint.add_url_rule('/bucket-lists/<slug>/delete',
                                    view_func=bucket_list_delete, methods=['POST'])
