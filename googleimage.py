from google_images_search import GoogleImagesSearch

# you can provide API key and CX using arguments,
# or you can set environment variables: GCS_DEVELOPER_KEY, GCS_CX
gis = GoogleImagesSearch('AIzaSyBRlama1N7tiW0yVq45CrqCx9hyFrESmIs', '144af1a5b59944a2b')
_search_params = {
    'q': 'iphone15',
}
gis.search(search_params=_search_params)
