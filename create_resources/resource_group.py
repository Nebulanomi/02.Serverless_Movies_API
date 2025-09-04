import main

# Ensure that the necessary environment variables are set
if not main.subscription_id or not main.resource_group_name or not main.location:
    raise ValueError("Missing subscription ID, resource group name or location.")

# ResourceManagementClient allows us to interact with Azure Resource Groups
resource_client = main.ResourceManagementClient(main.credential, main.subscription_id)

# Add some tags to the resource group for better management
resource_group_params = main.ResourceGroup(
    location=main.location,
    tags={
        "Budget": "---",
        "End date": "---",
        "Owner": "---",
        "Secondary Owner": "---",
        "Team name": "---",
        "Data_Classification":"---",
        "Project_Chargeability":"---",
        "Project_End_User":"---",
        "Project_Name":"---",
        "Deployed_By":"---",
        "Ticket_IdW":"---"
    }
)

# Create the Resource Group
resource_group = resource_client.resource_groups.create_or_update(main.resource_group_name, resource_group_params) # type: ignore
print(f"Provisioned Resource Group {resource_group.name} in the {resource_group.location} region.")