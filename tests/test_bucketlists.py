import unittest
import os
import json
from app import create_app, db


class BucketListTestCase(unittest.TestCase):
    """This class represents the bucket_list test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucket_list = {'name': 'Go to Borabora for vacay'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_bucket_list_creation(self):
        """Test API can create a bucket_list (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucket_list by making a POST request
        res = self.client().post(
            '/bucket-lists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucket_list)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_all_bucket_lists(self):
        """Test API can get a bucket_list (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucket_list by making a POST request
        res = self.client().post(
            '/bucket_lists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucket_list)
        self.assertEqual(res.status_code, 201)

        # get all the bucket_lists that belong to the test user by making a GET request
        res = self.client().get(
            '/bucket_lists/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_bucket_list_by_id(self):
        """Test API can get a single bucket_list by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/bucket_lists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucket_list)

        # assert that the bucket_list is created
        self.assertEqual(rv.status_code, 201)
        # get the response data in json format
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/bucket_lists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the bucket_list is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Borabora', str(result.data))

    def test_bucket_list_can_be_edited(self):
        """Test API can edit an existing bucket_list. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a bucket_list by making a POST request
        rv = self.client().post(
            '/bucket_lists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat, pray and love'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the bucket_list
        results = json.loads(rv.data.decode())

        # then, we edit the created bucket_list by making a PUT request
        rv = self.client().put(
            '/bucket_lists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Dont just eat, but also pray and love :-)"
            })
        self.assertEqual(rv.status_code, 200)

        # finally, we get the edited bucket_list to see if it is actually edited.
        results = self.client().get(
            '/bucket-lists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Dont just eat', str(results.data))

    def test_bucket_list_deletion(self):
        """Test API can delete an existing bucket_list. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/bucket-lists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat, pray and love'})
        self.assertEqual(rv.status_code, 201)
        # get the bucket_list in json
        results = json.loads(rv.data.decode())

        # delete the bucket_list we just created
        res = self.client().delete(
            '/bucket-lists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/bucket-lists/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
