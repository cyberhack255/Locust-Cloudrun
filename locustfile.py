from locust import HttpUser, between, task

import time

class QuickstartUser(HttpUser):
 @task
 def mainPage(self):
  self.client.get("/")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    min_wait = 5000
    max_wait = 9000