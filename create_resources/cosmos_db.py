import main
import movies_data

# Ensure that the necessary environment variables are set
if not main.subscription_id or not main.resource_group_name or not main.cosmos_account_name or not main.cosmos_db_name or not main.cosmos_db_container_name:
    raise ValueError("Missing subscription ID, resource group name, Cosmos DB account name, database name, or container name.")

# CosmosDBManagementClient lets you manage CosmosDB accounts, databases, and collections
cosmos_client = main.CosmosDBManagementClient(main.credential, main.subscription_id)

# Define Cosmos DB account parameters
cosmos_db_params = main.DatabaseAccountCreateUpdateParameters(
    location=main.location, # Specifies the location where the data is stored
    locations=[main.Location(location_name=main.location)], # Specifies the location where the data is replicated
    kind='GlobalDocumentDB', # Database type (GlobalDocumentDB is for the SQL API, Cosmos DB's default)
    database_account_offer_type='Standard' # Offer type (Standard is the default pricing tier)
)

# Provision the Cosmos DB account
cosmos_account = cosmos_client.database_accounts.begin_create_or_update(main.resource_group_name, main.cosmos_account_name, cosmos_db_params).result()
print(f"Provisioned CosmosDB {cosmos_account.name} in the Resource Group {main.resource_group_name} in the {cosmos_account.location} region.")

# Construct the Cosmos DB SQL URI and key
cosmos_db_uri = cosmos_account.document_endpoint
cosmos_db_primary_key = cosmos_client.database_accounts.list_keys(main.resource_group_name, main.cosmos_account_name).primary_master_key

# Ensure the key is available
if not cosmos_db_uri or not cosmos_db_primary_key:
    raise ValueError("Missing Cosmos DB primary key.")

# Connect to the Cosmos DB SQL account using the URI and primary key
cosmos_sql_client = main.CosmosClient(cosmos_db_uri, cosmos_db_primary_key)

# Create the Cosmos DB database
database = cosmos_sql_client.create_database_if_not_exists(id=main.cosmos_db_name)
print(f"Provisioned Cosmos DB SQL database '{main.cosmos_db_name}'.")

# The partition key is used for sharding (for performance/scaling)
partition_key_path = main.PartitionKey(path="/id")  # Define your partition key

# Define the container properties and provision the container
container = database.create_container_if_not_exists(id=main.cosmos_db_container_name, partition_key=partition_key_path, offer_throughput=400)
print(f"Provisioned Cosmos DB container '{main.cosmos_db_container_name}' in the SQL database '{main.cosmos_db_name}' with throughput of 400 RUs.")

# Loop through each movie data and upsert into Cosmos DB
for movie in movies_data.movies:
    container.upsert_item(movie)
    print(f"Inserted movie data for '{movie['title']}' into the Cosmos DB.")