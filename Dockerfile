FROM locustio/locust

# Install Authlib for Google Login
RUN pip install authlib requests

# Copy your locustfile
COPY locustfile.py /mnt/locust/locustfile.py

# Cloud Run defaults to port 8080. 
# We set the Locust Web Port to match it.
ENV LOCUST_WEB_PORT=8080

# Command to run locust
CMD ["-f", "/mnt/locust/locustfile.py"]
