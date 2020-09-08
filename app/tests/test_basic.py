from app import create_app
from app.models import db
import unittest

 
class BasicTests(unittest.TestCase):
 
    # executed prior to each test
    def setUp(self):
        app = create_app(testing=True)
        self.app = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
 
 
if __name__ == "__main__":
    unittest.main()
