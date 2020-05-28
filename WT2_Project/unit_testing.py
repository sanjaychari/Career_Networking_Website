import os
import unittest
import requests

class TestCase(unittest.TestCase):
    def setUp(self):
        '''app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()'''

    def tearDown(self):
        '''db.session.remove()
        db.drop_all()'''

    def test_add_user(self):
        '''u = User(nickname='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected'''
        resp_data = {'name':"a",'password':"abcd",'repeat_pass':"abcd",'company_name':"a",'company_headquarters':"a",'category':"a",'ceo':"a",'email':"a@a.com",'skills':"a"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Password in wrong format"
        resp_data = {'name':"a",'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'repeat_pass':"3d725109c7e7c0bfb9d709836735b56d943d263a",'company_name':"a",'company_headquarters':"a",'category':"a",'ceo':"a",'email':"a@a.com",'skills':"a"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Password and repeat password do not match"
        resp_data = {'name':"a",'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'repeat_pass':"3d725109c7e7c0bfb9d709836735b56d943d263f",'company_name':"a",'company_headquarters':"a",'category':"a",'ceo':"a",'email':"sanjaychari2xy2@gmail.com",'skills':"a"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Email already registered"
        resp_data = {'name':"Aditya Nair",'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'repeat_pass':"3d725109c7e7c0bfb9d709836735b56d943d263f",'company_name':"Infosys",'company_headquarters':"Bangalore",'category':"Software",'ceo':"Narayan Murthy",'email':"adityanair@gmail.com",'skills':"Hadoop,Big Data,Spark"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Profile Created Successfully"

    def test_login(self):
        resp_data = {'password':"abcd",'email':"a@a.com"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Password in Wrong Format"
        resp_data = {'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'email':"a@a.com"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Email Not Registered"
        resp_data = {'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'email':"sanjaychari2xy2@gmail.com"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Invalid Password"
        resp_data = {'password':"425af12a0743502b322e93a015bcf868e324d56a",'email':"sanjaychari2xy2@gmail.com"}
        response = requests.post("http://127.0.0.1:5000/api/v1/users",json=resp_data)
        assert response.text == "Login Successful"

    def test_add_job(self):
        resp_data = {'company':"Infosys",'username':"Sanjay Chari",'city':"Bangalore",'country':"India",'specs':"Big Data Consultant",'term':"Part Time",'lowsal':"Rs. 400000",'highsal':"Rs. 700000"}
        response = requests.post("http://127.0.0.1:5000/api/v1/jobs",json=resp_data)
        assert response.text == "Job Created Successfully"

    def test_list_jobs(self):
        response = requests.get("http://127.0.0.1:5000/api/v1/jobs?term=Part%20Time&location=Anywhere&specs=Software")
        assert "<div class=\"row align-items-start job-item border-bottom pb-3 mb-3 pt-3\">" in response.text

    def test_add_connections(self):
        resp_data = {'email':"b@b.com",'user1_name':'Dhakshith RT'}
        response = requests.post("http://127.0.0.1:5000/api/v1/connections",json=resp_data)
        assert response.text == "Invalid Email"
        resp_data = {'email':"sanjaychari2xy2@gmail.com",'user1_name':'Dhakshith RT'}
        response = requests.post("http://127.0.0.1:5000/api/v1/connections",json=resp_data)
        assert response.text == "Connection Request Sent"

    def test_update_connections(self):
        resp_data = {'approve_request_username':"Dhakshith RT",'username':"Sanjay Chari"}
        response = requests.post("http://127.0.0.1:5000/api/v1/connections",json=resp_data)
        assert response.text == "Request Approved"

    def test_list_connections(self):
        response = requests.get("http://127.0.0.1:5000/api/v1/connections?fetchdata=True&username=Sanjay Chari")
        assert "<div class=\"row mb-5 justify-content-center\">" in response.text
        response = requests.get("http://127.0.0.1:5000/api/v1/connections?search_tag=A&username=Sanjay Chari")
        assert "<div class=\"row mb-5 justify-content-center\">" in response.text

    def test_add_messages(self):
        resp_data = {'user1_name':"b",'user2_name':"c",'content':"Hello"}
        response = requests.post("http://127.0.0.1:5000/api/v1/messages",json=resp_data)
        assert response.text == "Invalid Username"
        resp_data = {'user1_name':"Sanjay Chari",'user2_name':"Dhakshith RT",'content':"Hello"}
        response = requests.post("http://127.0.0.1:5000/api/v1/messages",json=resp_data)
        assert response.text == "Message Sent Successfully"

    def test_get_messages(self):
        response = requests.get("http://127.0.0.1:5000/api/v1/messages?is_reload_needed=True")
        assert (response.text == "No new message added") or (response.text == "New Messages Added")
        response = requests.get("http://127.0.0.1:5000/api/v1/messages?search_tag=A&username=Sanjay Chari")
        assert "<div class=\"chat_list\"" in response.text
        response = requests.get("http://127.0.0.1:5000/api/v1/messages?fetchdata=True&username=Sanjay Chari")
        assert "<div class=\"chat_list\"" in response.text

    def test_add_posts(self):
        resp_data = {'username':"Sanjay Chari",'content':"This post is created during unit testing"}
        response = requests.post("http://127.0.0.1:5000/api/v1/posts",json=resp_data)
        assert response.text == "Post Created"

    def test_add_comments(self):
        resp_data = {'username':"Sanjay Chari",'content':"This comment is created during unit testing",'post_id':1}
        response = requests.post("http://127.0.0.1:5000/api/v1/posts",json=resp_data)
        assert response.text == "Comment Posted Successfully"

    def test_get_posts(self):
        response = requests.get("http://127.0.0.1:5000/api/v1/posts?fetchdata=True&username=Sanjay Chari")
        assert "<div class=\"col-md-6 col-lg-4 mb-5\">" in response.text
        response = requests.get("http://127.0.0.1:5000/api/v1/posts?post_id=1")
        assert "<div class=\"pt-5\"><h3 class=\"mb-5\">" in response.text
        

if __name__ == '__main__':
    unittest.main()