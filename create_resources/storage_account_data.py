import main

# Azure Storage Account connection details
storage_account_url = f"https://{main.storage_account_name}.blob.core.windows.net"
blob_service_client = main.BlobServiceClient(account_url=storage_account_url, credential=main.credential)

# Container where images will be uploaded
container_name = main.storage_account_container_name

# Path to the local folder containing images
local_folder = f"{main.poster_folder}"

# Function to upload an image to Azure Blob Storage
def upload_image_to_blob(file_path, container_name):

    # Extract the file name from the path
    file_name = main.os.path.basename(file_path)

    # Create a blob client using the container and file name
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    # Open the image file and upload its content to the blob
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data)

        print(f"Uploaded {file_name} to blob storage.")

# Iterate through all files in the local folder and upload the images
for file_name in main.os.listdir(local_folder):

    # Construct full file path with the filename (movies/incetion.jpg)
    file_path = main.os.path.join(local_folder, file_name)

    # Only upload files with specific image extensions
    if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
        upload_image_to_blob(file_path, container_name)