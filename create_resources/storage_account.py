import main

if not main.subscription_id or not main.resource_group_name or not main.location or not main.storage_account_name or not main.storage_account_container_name:
    raise ValueError("Missing subscription ID, resource group name, location, storage account name or storage account container name.")

# StorageManagementClient lets you manage Azure Storage accounts (Blob, File, Table, Queue).
storage_client = main.StorageManagementClient(main.credential, main.subscription_id)

# Define Azure Blob Storage account parameters
storage_account_params = main.StorageAccountCreateParameters(
    sku=main.Sku(name="Standard_LRS"),
    kind=main.Kind.STORAGE_V2,
    location=main.location,
    enable_https_traffic_only=True,
    allow_blob_public_access=True
)

# Provision the Azure Blob Storage account
storage_account = storage_client.storage_accounts.begin_create(main.resource_group_name, main.storage_account_name, storage_account_params).result()
print(f"Provisioned Storage Account {main.storage_account_name} in the Resource Group {main.resource_group_name} in the {storage_account.location} region.")

# Create a BlobServiceClient to interact with the Blob service
storage_account_url = f"https://{main.storage_account_name}.blob.core.windows.net"
blob_service_client = main.BlobServiceClient(account_url=storage_account_url, credential=main.credential)

# Create a container in the Blob Storage account
blob_container_client = blob_service_client.create_container(main.storage_account_container_name, public_access='Blob')
print(f"Created Blob container: {main.storage_account_container_name}")