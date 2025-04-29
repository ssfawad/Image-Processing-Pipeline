import os
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient
from PIL import Image

import io

# Setup
storage_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
servicebus_connection_string = os.getenv('SERVICEBUS_CONNECTION_STRING')
queue_name = 'imgqueue'

def process_image(blob_name):
    container_client = blob_service_client.get_container_client('input')
    blob_client = container_client.get_blob_client(blob_name)
    download_stream = blob_client.download_blob()
    image_data = download_stream.readall()

    # Open, resize, and save
    image = Image.open(io.BytesIO(image_data))

    # 🛠️ Fix: Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    image = image.resize((100, 100))

    output_stream = io.BytesIO()
    image.save(output_stream, format='JPEG')
    output_stream.seek(0)

    output_container_client = blob_service_client.get_container_client('output')
    output_blob_client = output_container_client.get_blob_client(blob_name)
    output_blob_client.upload_blob(output_stream, overwrite=True)


def main():
    servicebus_client = ServiceBusClient.from_connection_string(servicebus_connection_string)
    receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)

    with receiver:
        for msg in receiver:
            raw_blob_path = str(msg)
            print(f"Received raw Service Bus message: {raw_blob_path}")

            # Extract blob name safely
            if '/' in raw_blob_path:
                blob_name = raw_blob_path.split('/')[-1]  # e.g., 'test.jpg'
            else:
                blob_name = raw_blob_path  # fallback if it's just the filename

            print(f"Processing blob: {blob_name}")
            process_image(blob_name)
            receiver.complete_message(msg)

if __name__ == "__main__":
    main()
