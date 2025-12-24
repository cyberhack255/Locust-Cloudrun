from locust import HttpUser, between, task

import time

class QuickstartUser(HttpUser):
 @task
 def mainPage(self):
  self.client.get("/")