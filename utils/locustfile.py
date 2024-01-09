from locust import HttpLocust, TaskSet, between

def login(l):
    l.client.post("/login", {"username":"ruchella_kock1@email.com", "password":"Hello1"})

def logout(l):
    l.client.post("/logout")

def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/home")

class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
