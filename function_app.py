import logging  # Import logging module to log information and errors
import json     # Import json module to handle JSON serialization
import os       # Import os module to access environment variables
import openai   # Import OpenAI's GPT for AI summary generation

import azure.functions as func  # Import Azure Functions HTTP request/response classes
from azure.cosmos import CosmosClient, exceptions  # Import Cosmos client and exception handling

# Fetch Cosmos DB credentials from environment variables
# These should be set in the Azure portal under "Application Settings" for security purposes
cosmos_endpoint_uri = os.getenv("COSMOS_DB_ENDPOINT")
key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_NAME")
container_name = os.getenv("COSMOS_CONTAINER_NAME")

# Ensure that all Cosmos DB credentials are provided
# This raises an error if any are missing
if not all([cosmos_endpoint_uri, key, database_name, container_name]):
    raise ValueError("Cosmos DB credentials are missing from environment variables.")

# Initialize the Azure Functions app with anonymous access
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Define the route for this function
# It will be accessed via "/movies" URL
@app.route(route="movies")
def get_movies(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function is triggered by an HTTP request.
    It retrieves all movie records from a Cosmos DB collection and returns them as a JSON response.
    """

    logging.info('Fetching all movies from Cosmos DB.')

    try:
        # Initialize the Cosmos client within the function
        # This ensures the client is only created when needed, improving performance in serverless environments
        client = CosmosClient(cosmos_endpoint_uri, key)
        
        # Get a reference to the specific database and container (collection) where movies are stored
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
    
        # Query the container to read all items (movies) with a maximum item count (100) for better performance
        movies = list(container.read_all_items(max_item_count=100))
        
        # Convert the list of movie objects to JSON format for the HTTP response
        movies_json = json.dumps(movies)
        
        # Return the movies list as a JSON response with a 200 status (success)
        return func.HttpResponse(movies_json, mimetype="application/json", status_code=200)
    
    except exceptions.CosmosHttpResponseError as e:
        # Catch specific Cosmos DB errors and log the error details
        logging.error(f"Error occurred while fetching data from Cosmos DB: {e}")
        
        # Return a 500 (Internal Server Error) response if there's a Cosmos DB issue
        return func.HttpResponse("Error fetching data from Cosmos DB", status_code=500)
    
    except Exception as e:
        # Catch any other unexpected errors and log them for troubleshooting
        logging.error(f"Unexpected error: {e}")
        
        # Return a 500 (Internal Server Error) response if any generic error occurs
        return func.HttpResponse("An unexpected error occurred", status_code=500)

# Define the route for fetching movies by release year
@app.route(route="movies/getmoviesbyyear/{year}")
def get_movies_by_year(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching movies by release year from Cosmos DB.')
    
    try:
        client = CosmosClient(cosmos_endpoint_uri, key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        # Get year from URL parameters
        release_year = req.route_params.get('year')
        
        # Check if a valid year was provided
        if not release_year:
            return func.HttpResponse("Please provide a valid year", status_code=400)

        # Construct a query to fetch movies by the specified release year
        query = f"SELECT * FROM c WHERE c.releaseYear = '{release_year}'"
        movies = list(container.query_items(query=query, enable_cross_partition_query=True))

        # Return the fetched movies as a JSON response with a 200 status (success)
        return func.HttpResponse(json.dumps(movies), mimetype="application/json", status_code=200)
    
    # Log any errors that occur while fetching from Cosmos DB
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error occurred: {e}")
        return func.HttpResponse("Error fetching data from Cosmos DB", status_code=500)
    
    # Log unexpected errors and return a generic error message
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse("An unexpected error occurred", status_code=500)

# Define the route for generating a movie summary based on the title
@app.route(route="movies/getmoviesummary/{title}")
def getmoviesbysummary(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching movie details for summary generation.')

    client = CosmosClient(cosmos_endpoint_uri, key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # OpenAI API Key for accessing the AI model
    openai.api_key = os.getenv("OPENAI_KEY")

    movie_title = req.route_params.get('title')
    
    if not movie_title:
        return func.HttpResponse("Please provide a valid movie title", status_code=400)

    try:
        query = f"SELECT * FROM c WHERE c.title = '{movie_title}'"
        movies = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not movies:
            return func.HttpResponse(f"Movie with title {movie_title} not found", status_code=404)
        
        for movie in movies:
            # Use OpenAI to generate a summary for the movie
            prompt = f"Generate a summary for the movie {movie_title}: {movie['genre']}"
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ])
            
            movie["generatedSummary"] = response['choices'][0]['message']['content'].strip()

            # Return movie data with generated summary
            return func.HttpResponse(json.dumps(movie), mimetype="application/json", status_code=200)
        
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error occurred: {e}")
        return func.HttpResponse("Error fetching data from Cosmos DB", status_code=500)
    
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return func.HttpResponse("Error generating movie summary", status_code=500)