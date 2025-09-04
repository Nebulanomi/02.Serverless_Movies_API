import main

# This is a JSON-like Python dictionary containing the movie details you want to insert into Cosmos DB
movies = [
    {
        "id" : "inception-2010",
        "title" : "Inception",
        "releaseYear" : "2010",
        "genre" : "Science Fiction, Action",
        "coverUrl" : f"https://{main.storage_account_name}.blob.core.windows.net/{main.storage_account_container_name}/inception.jpg"
    },
    {
        "id" : "shrek-2001",
        "title" : "Shrek",
        "releaseYear" : "2001",
        "genre" : "Comedy, Fantasy",
        "coverUrl" : f"https://{main.storage_account_name}.blob.core.windows.net/{main.storage_account_container_name}/shrek.jpg"
    },
    {
        "id" : "avengers-2012",
        "title" : "Avengers",
        "releaseYear" : "2012",
        "genre" : "Action,Adventure",
        "coverUrl" : f"https://{main.storage_account_name}.blob.core.windows.net/{main.storage_account_container_name}/avengers.jpg"
    }
]