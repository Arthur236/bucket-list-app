import re

from flask.views import MethodView
from flask import jsonify, make_response, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from . import bucketlists_blueprint
from app.models import Bucketlist
from ..decorators import MyDecorator
my_dec = MyDecorator()


class BucketlistView(MethodView):
    """
      Handles bucketlist creation and retrieval
    """
    @staticmethod
    def post(self):
        """
        Creates bucketlists
        """
        user_id = my_dec.check_token()

        if user_id == 'Missing':
            flash('You cannot access that page without a token')
            return redirect(url_for('auth.login'), 401)
        elif user_id == 'Invalid':
            flash("Your token is either expired or invalid")
            return redirect(url_for('auth.login'), 401)
        else:
            name = str(request.data.get('name', ''))
            description = str(request.data.get('description', ''))

            if name:
                if not re.match("^[a-zA-Z0-9 _]*$", name):
                    flash("The list name cannot contain special characters. Only underscores (_)")
                    return redirect(url_for('bucketlists'), 400)

                b_list = Bucketlist.query. \
                    filter(func.lower(Bucketlist.name) == name.lower(),
                           Bucketlist.user_id == user_id).first()

                if not b_list:
                    # There is no list so we'll try to create it
                    buckelist = Bucketlist(user_id=user_id,
                                               name=name, description=description)
                    buckelist.save()

                    flash("Bucketlist created successfully")
                    return redirect(url_for('bucketlists'), 201)

                flash("That bucketlist already exists")
                return redirect(url_for('bucketlists'), 400)

            flash("Bucketlist name not provided")
            return redirect(url_for('bucketlists'), 400)

        @staticmethod
        def get(self):
            """
            Retrieves bucketlists
            """
            user_id = my_dec.check_token()

            if user_id == 'Missing':
                flash('You cannot access that page without a token')
                return redirect(url_for('auth.login'), 401)
            elif user_id == 'Invalid':
                flash("Your token is either expired or invalid")
                return redirect(url_for('auth.login'), 401)
            else:
                search_query = request.args.get("q")
                try:
                    limit = int(request.args.get('limit', 10))
                    page = int(request.args.get('page', 1))
                except (ValueError, TypeError):
                    # An error occurred, therefore return a string message containing the error
                    flash("The parameters provided should be integers")
                    return redirect(url_for('bucketlists'), 400)

                if search_query:
                    # if parameter q is specified
                    buckelists = Bucketlist.query. \
                        filter(Bucketlist.name.ilike('%' + search_query + '%')). \
                        filter_by(user_id=user_id).all()
                    output = []

                    if not buckelists:
                        flash("You do not have bucketlists matching that criteria")
                        return redirect(url_for('bucketlists'), 404)

                    for b_list in buckelists:
                        obj = {
                            'id': b_list.id,
                            'name': b_list.name,
                            'description': b_list.description,
                            'date_created': b_list.date_created,
                            'date_modified': b_list.date_modified
                        }
                        output.append(obj)
                    response = jsonify(output)
                    return redirect(url_for('bucketlists'), 404, buckelists=response)

                total_lists = Bucketlist.query.filter_by(
                    user_id=user_id).count()
                paginated_lists = Bucketlist.query.filter_by(user_id=user_id). \
                    order_by(Bucketlist.name.asc()).paginate(page, limit)
                results = []

                if not paginated_lists.items:
                    response = 'You have no bucketlists'
                    return redirect(url_for('bucketlists'), 404, buckelists=response)

                for buckelist in paginated_lists.items:
                    obj = {
                        'id': buckelist.id,
                        'name': buckelist.name,
                        'description': buckelist.description,
                        'date_created': buckelist.date_created,
                        'date_modified': buckelist.date_modified
                    }
                    results.append(obj)

                next_page = 'None'
                previous_page = 'None'

                if paginated_lists.has_next:
                    next_page = '/buckelists' + '?page=' + str(page + 1) + \
                                '&limit=' + str(limit)
                if paginated_lists.has_prev:
                    previous_page = '/buckelists' + '?page=' + str(page - 1) + \
                        '&limit=' + str(limit)

                response = {
                    'total': total_lists,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'buckelists': results
                }

                return redirect(url_for('bucketlists'), 200, buckelists=jsonify(response))


class BucketistManipulation(MethodView):
    """
    Handles bucketlist manipulation operations
    """
    @staticmethod
    def get(list_id):
        """
        Retrieves a specific bucketlist
        """
        user_id = my_dec.check_token()

        if user_id == 'Missing':
            return jsonify({'message': 'You cannot access that page without a token.'}), 401
        elif user_id == 'Invalid':
            return jsonify({'message': 'Your token is either expired or invalid.'}), 401
        else:
            try:
                int(list_id)
            except (ValueError, TypeError):
                # An error occurred, therefore return a string message containing the error
                response = {
                    'message': 'The parameter provided should be an integer'}
                return make_response(jsonify(response)), 401

            # retrieve a bucketlist using it's id
            buckelist = Bucketlist.query.filter_by(
                id=list_id, user_id=user_id).first()

            if not buckelist:
                response = {
                    "message": "That bucketlist is not yours or does not exist"}
                return make_response(jsonify(response)), 404

            if buckelist.user_id == user_id:
                response = jsonify({
                    'id': buckelist.id,
                    'name': buckelist.name,
                    'description': buckelist.description,
                    'date_created': buckelist.date_created,
                    'date_modified': buckelist.date_modified
                })
                response.status_code = 200
                return response

    @staticmethod
    def put(list_id):
        """
        Updates a specific bucketlist
        """
        user_id = my_dec.check_token()

        if user_id == 'Missing':
            return jsonify({'message': 'You cannot access that page without a token.'}), 401
        elif user_id == 'Invalid':
            return jsonify({'message': 'Your token is either expired or invalid.'}), 401
        else:
            try:
                int(list_id)
            except (ValueError, TypeError):
                # An error occurred, therefore return a string message containing the error
                response = {
                    'message': 'The parameter provided should be an integer'}
                return make_response(jsonify(response)), 401

            # retrieve a bucketlist using it's id
            buckelist = Bucketlist.query.filter_by(
                id=list_id, user_id=user_id).first()

            if not buckelist:
                response = {
                    "message": "That bucketlist is not yours or does not exist"}
                return make_response(jsonify(response)), 404

            name = str(request.data.get('name', '')) if str(request.data.get('name', '')) \
                else buckelist.name
            description = str(request.data.get('description', '')) if \
                str(request.data.get('description', '')) else buckelist.description

            if name:
                if not re.match("^[a-zA-Z0-9 _]*$", name):
                    response = {
                        'message': 'The list name cannot contain special characters. '
                                   'Only underscores'
                    }
                    return make_response(jsonify(response)), 400

                b_lists = Bucketlist.query.filter_by(user_id=user_id).all()

                for b_list in b_lists:
                    # Check if name exists
                    if str(list_id) != str(b_list.id) and name.lower() == b_list.name.lower():
                        response = {"message": "bucketlist already exists"}
                        return make_response(jsonify(response)), 401

                # Check if user is owner
                if buckelist.user_id == user_id:
                    buckelist.name = name
                    buckelist.description = description
                    buckelist.save()

                    response = jsonify({
                        'id': buckelist.id,
                        'name': buckelist.name,
                        'description': buckelist.description,
                        'date_created': buckelist.date_created,
                        'date_modified': buckelist.date_modified
                    })
                    response.status_code = 200
                    return response

    @staticmethod
    def delete(list_id):
        """
        Deletes a specific bucketlist
        """
        user_id = my_dec.check_token()

        if user_id == 'Missing':
            return jsonify({'message': 'You cannot access that page without a token.'}), 401
        elif user_id == 'Invalid':
            return jsonify({'message': 'Your token is either expired or invalid.'}), 401
        else:
            try:
                int(list_id)
            except (ValueError, TypeError):
                # An error occurred, therefore return a string message containing the error
                response = {
                    'message': 'The parameter provided should be an integer'}
                return make_response(jsonify(response)), 401

            # retrieve a bucketlist using it's id
            buckelist = Bucketlist.query.filter_by(
                id=list_id, user_id=user_id).first()

            if not buckelist:
                response = {
                    "message": "That bucketlist is not yours or does not exist"
                }
                return make_response(jsonify(response)), 404

            if buckelist.user_id == user_id:
                buckelist.delete()
                response = {
                    "message": "bucketlist {} deleted successfully".format(buckelist.id)
                }
                return make_response(jsonify(response)), 200


bucketlist_view = BucketlistView.as_view('bucketlist_view')  # pylint: disable=invalid-name
bucketist_manipulation = BucketistManipulation.as_view('bucketist_manipulation')  # pylint: disable=invalid-name


# Define rules
bucketlists_blueprint.add_url_rule('/bucketlists',
                                     view_func=bucketlist_view, methods=['POST', 'GET'])
bucketlists_blueprint.add_url_rule('/bucketlists/<list_id>',
                                     view_func=bucketist_manipulation, methods=['GET', 'PUT', 'DELETE'])
