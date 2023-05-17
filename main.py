from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parse query parameters
        path, _, query_string = self.path.partition('?')
        params = urllib.parse.parse_qs(query_string)
        query = params.get('query', [''])[0]  # Use the 'query' parameter value if it exists, or '' if it doesn't

        if not query:
            # Send an error message if the 'query' parameter is missing
            self.send_response(400)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Error: Missing "query" parameter. Please provide a valid SPARQL query.'.encode('utf-8'))
            return

        # Fetch data from Wikidata
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        try:
            data = sparql.query().convert()

            # Convert results to a markdown table
            results = data['results']['bindings']
            if results:
                df = pd.DataFrame(results)
                df = df.applymap(lambda x: x['value'] if isinstance(x, dict) else x)
                markdown_table = df.to_markdown(index=False)
            else:
                markdown_table = "No results found."

        except Exception as e:
            # If the query is invalid or another error occurs, send an error message
            self.send_response(400)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'Error: Invalid query or unable to process the request. Details: {str(e)}'.encode('utf-8'))
            return

        # Send the response
        self.send_response(200)
        self.send_header('Content-type','text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(markdown_table.encode('utf-8'))

        return
