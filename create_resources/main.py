from azure.identity import DefaultAzureCredential

from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup

from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku, Kind
from azure.storage.blob import BlobServiceClient

from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.cosmosdb.models import DatabaseAccountCreateUpdateParameters, Location
from azure.cosmos import CosmosClient, PartitionKey

from dotenv import load_dotenv
import os

# Take environment variables from .env
load_dotenv("../.env")

# Acquire Azure credentials
credential = DefaultAzureCredential()

# DefaultAzureCredential automatically attempts to authenticate using various methods, such as:
    # - Environment variables (like AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)
    # - Azure Managed Identity if running in an Azure environment
    # - Visual Studio or Azure CLI authentication for local development

# Retrieve the Azure Subscription ID from the environment variable
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")

# The region where we want to create the resources
location = os.environ.get("LOCATION")

# Define the resource names
resource_group_name = os.environ.get("RG_NAME")
storage_account_name = os.environ.get("SA_NAME")
storage_account_container_name = os.environ.get("SA_CONTAINER_NAME")
cosmos_account_name = os.environ.get("COSMOS_ACCOUNT")
cosmos_db_name = os.environ.get("COSMOS_DB_NAME")
cosmos_db_container_name = os.environ.get("COSMOS_CONTAINER_NAME")
poster_folder = os.environ.get("POSTER_LOCATION")