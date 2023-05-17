from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
import json

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
            self.wfile.write('Error: Missing "query" parameter. Please provide a SPARQL query.'.encode('utf-8'))
            return

        # Fetch data from Wikidata
        response = requests.get(f"https://query.wikidata.org/bigdata/namespace/wdq/sparql?query={urllib.parse.quote(query)}", headers={"Accept": "application/sparql-results+json"})
        data = response.json()

        # Extract the results
        results = data['results']['bindings']

        if not results:
            self.send_response(404)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Error: The query did not return any results.'.encode('utf-8'))
            return

        # Format the results in markdown as a table
        # Headers
        headers = results[0].keys()
        markdown_results = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]

        # Rows
        for result in results:
            markdown_results.append("| " + " | ".join(result[var]['value'] for var in headers) + " |")

        markdown_results_str = "\n".join(markdown_results)

        # Send the response
        self.send_response(200)
        self.send_header('Content-type','text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(markdown_results_str.encode('utf-8'))

        return
