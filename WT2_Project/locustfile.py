from locust import HttpUser, TaskSet, task, between
import json

class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    @task
    def get_tests(self):
        self.client.get("/api/v1/jobs?term=Part%20Time&location=Anywhere&specs=Software")
        self.client.get("/api/v1/connections?fetchdata=True&username=Sanjay Chari")
        self.client.get("/api/v1/connections?search_tag=A&username=Sanjay Chari")
        self.client.get("/api/v1/messages?search_tag=A&username=Sanjay Chari")
        self.client.get("/api/v1/messages?fetchdata=True&username=Sanjay Chari")
        self.client.get("/api/v1/posts?fetchdata=True&username=Sanjay Chari")

    @task
    def post_tests(self):
        self.client.post("/api/v1/users", json = {'name':"a",'password':"abcd",'repeat_pass':"abcd",'company_name':"a",'company_headquarters':"a",'category':"a",'ceo':"a",'email':"a@a.com",'skills':"a"})
        self.client.post("/api/v1/users", json = {'name':"a",'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'repeat_pass':"3d725109c7e7c0bfb9d709836735b56d943d263a",'company_name':"a",'company_headquarters':"a",'category':"a",'ceo':"a",'email':"a@a.com",'skills':"a"})
        self.client.post("/api/v1/users", json = {'name':"a",'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'repeat_pass':"3d725109c7e7c0bfb9d709836735b56d943d263a",'company_name':"a",'company_headquarters':"a",'category':"a",'ceo':"a",'email':"a@a.com",'skills':"a"})
        self.client.post("/api/v1/users", json = {'name':"a",'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'repeat_pass':"3d725109c7e7c0bfb9d709836735b56d943d263f",'company_name':"a",'company_headquarters':"a",'category':"a",'ceo':"a",'email':"sanjaychari2xy2@gmail.com",'skills':"a"})
        self.client.post("/api/v1/users", json = {'password':"abcd",'email':"a@a.com"})
        self.client.post("/api/v1/users", json = {'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'email':"a@a.com"})
        self.client.post("/api/v1/users", json = {'password':"3d725109c7e7c0bfb9d709836735b56d943d263f",'email':"sanjaychari2xy2@gmail.com"})
        self.client.post("/api/v1/users", json = {'password':"425af12a0743502b322e93a015bcf868e324d56a",'email':"sanjaychari2xy2@gmail.com"})
        self.client.post("/api/v1/jobs", json = {'company':"Infosys",'username':"Sanjay Chari",'city':"Bangalore",'country':"India",'specs':"Big Data Consultant",'term':"Part Time",'lowsal':"Rs. 400000",'highsal':"Rs. 700000"})
        self.client.post("/api/v1/connections", json = {'email':"b@b.com",'user1_name':'Dhakshith RT'})
        self.client.post("/api/v1/connections", json = {'email':"sanjaychari2xy2@gmail.com",'user1_name':'Dhakshith RT'})
        self.client.post("/api/v1/connections", json = {'approve_request_username':"Dhakshith RT",'username':"Sanjay Chari"})
        self.client.post("/api/v1/messages", json = {'user1_name':"b",'user2_name':"c",'content':"Hello"})
        self.client.post("/api/v1/messages", json = {'user1_name':"Sanjay Chari",'user2_name':"Dhakshith RT",'content':"Hello"})
        self.client.post("/api/v1/posts", json = {'username':"Sanjay Chari",'content':"This post is created during unit testing"})
        self.client.post("/api/v1/posts", json = {'username':"Sanjay Chari",'content':"This comment is created during unit testing",'post_id':1})