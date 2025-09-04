from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
from openai import OpenAI

import azure.functions as func
import logging
import json
import os
import html

# Take environment variables from .env
load_dotenv()

# Fetch Cosmos DB credentials from environment variables
cosmos_endpoint_uri = os.getenv("COSMOS_DB_ENDPOINT")
key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_NAME")
container_name = os.getenv("COSMOS_CONTAINER_NAME")

# Initialize the Azure Functions app with anonymous access
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Validate that all necessary Cosmos DB credentials are present
if not cosmos_endpoint_uri or not key or not database_name or not container_name:
    raise ValueError("Cosmos DB credentials are missing.")

# Initialize the Cosmos client within the function
client = CosmosClient(cosmos_endpoint_uri, key)

# Get a reference to the specific database and container (collection) where movies are stored
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# Helper function to build HTML header
def build_html_header():
    return """
    <html>
    <head>
        <style>
            .movie-gallery { display:flex; flex-wrap:wrap; gap:20px; }
            .movie-card { border:1px solid #ccc; padding:10px; width:200px; text-align:center; box-shadow:2px 2px 5px rgba(0,0,0,0.1); }
            .movie-card img { max-width:100%; height:auto; }
        </style>
    </head>
    <body><div class="movie-gallery">
    """

# Helper function to build HTML footer
def build_html_footer():
    return "</div></body></html>"

# Define the route for this function
@app.route(route="movies")
def get_movies(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function is triggered by an HTTP request.
    It retrieves all movie records from a Cosmos DB collection and returns them as an HTML response.
    """

    logging.info('Fetching all movies from Cosmos DB.')

    try:
        
        # Query the container to read all items (movies) with a maximum item count (100) for better performance
        movies = list(container.read_all_items(max_item_count=100))

        # Build HTML content
        html_content = build_html_header()
        
        # Iterate through the movies and create HTML cards for each movie
        for movie in movies:
            html_content += f"""
                <div class="movie-card">
                    <h3>{html.escape(movie['title'])} ({html.escape(movie['releaseYear'])})</h3>
                    <p>{html.escape(movie['genre'])}</p>
                    <img src="{html.escape(movie['coverUrl'])}" />
                </div>
            """

        # Close the HTML tags
        html_content += build_html_footer()

        # Return the movies list as a HTML response with a 200 status (success)
        return func.HttpResponse(html_content, mimetype="text/html")
    
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
@app.route(route="movies/year/{year}")
def get_year(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching movies by release year from Cosmos DB.')
    
    try:
        
        # Get year from URL parameters
        release_year = req.route_params.get('year')
        
        # Check if a valid year was provided
        if not release_year:
            return func.HttpResponse("Please provide a valid year", status_code=400)

        # Construct a query to fetch movies by the specified release year
        document_query = f"SELECT * FROM documents WHERE documents.releaseYear = '{release_year}'"
        movies = list(container.query_items(query=document_query, enable_cross_partition_query=True))

        html_content = build_html_header()
        
        for movie in movies:
            html_content += f"""
                <div class="movie-card">
                    <h3>{html.escape(movie['title'])} ({html.escape(movie['releaseYear'])})</h3>
                    <p>{html.escape(movie['genre'])}</p>
                    <img src="{html.escape(movie['coverUrl'])}" />
                </div>
            """

        html_content += build_html_footer()

        return func.HttpResponse(html_content, mimetype="text/html")
    
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error occurred: {e}")
        return func.HttpResponse("Error fetching data from Cosmos DB", status_code=500)
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse("An unexpected error occurred", status_code=500)

# Define the route for generating a movie summary based on the title
@app.route(route="movies/summary/{title}")
def get_summary(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching movie details for summary generation.')

    try:
        title = req.route_params.get('title')
        
        if not title:
            return func.HttpResponse("Please provide a valid movie title", status_code=400)

        document_query = "SELECT * FROM documents WHERE documents.title = @title"
        movies = list(container.query_items(query=document_query, parameters=[{"name": "@title", "value": title}], enable_cross_partition_query=True))
        
        if not movies:
            return func.HttpResponse(f"Movie with title {title} not found", status_code=404)
        
        # Use OpenAI to generate a summary for the movie
        for movie in movies:
            prompt = f"Generate a summary for the movie {title}"
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Capture and clean up the generated summary
            movie["generatedSummary"] = response.choices[0].message.content

        html_content = build_html_header()
        
        for movie in movies:
            html_content += f"""
                <div class="movie-card">
                    <h3>{html.escape(movie['title'])} ({html.escape(movie['releaseYear'])})</h3>
                    <p>{html.escape(movie['genre'])}</p>
                    <img src="{html.escape(movie['coverUrl'])}" />
                    <p>{html.escape(movie.get('generatedSummary', ''))}</p>
                </div>
            """

        html_content += build_html_footer()

        return func.HttpResponse(html_content, mimetype="text/html")
    
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error occurred: {e}")
        return func.HttpResponse("Error fetching data from Cosmos DB", status_code=500)
    
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return func.HttpResponse("Error generating movie summary", status_code=500)