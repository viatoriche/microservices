from unittest import TestCase


class TestUtils(TestCase):

    def test_jinja_utils(self):
        from microservices.utils import get_all_variables_from_template
        from flask import Flask


        app = Flask(__name__)
        vars = get_all_variables_from_template(app.jinja_env, 'test_template.html')
        self.assertEqual('var1' in vars, True)
        self.assertEqual('var2' in vars, True)
