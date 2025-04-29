import logging
import os
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

STORAGE_CONNECTION_STRING = os.getenv("AzureWebJobsStorage")
SERVICE_BUS_CONNECTION_STRING = os.getenv("ServiceBusConnectionString")
QUEUE_NAME = os.getenv("QueueName")

def main(blob: func.InputStream):
    logging.info(f"Blob trigger function processed blob \nName: {blob.name}\nBlob Size: {blob.length} bytes")

    servicebus_client = ServiceBusClient.from_connection_string(conn_str=SERVICE_BUS_CONNECTION_STRING)
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    
    with sender:
        message = ServiceBusMessage(blob.name)
        sender.send_messages(message)

    logging.info(f"Sent message for blob {blob.name} to Service Bus queue")
