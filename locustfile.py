import os
from locust import HttpUser, task, events

class MyUser(HttpUser):
    @task
    def my_task(self):
        self.client.get("/")