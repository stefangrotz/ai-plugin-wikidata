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
            self.wfile.write('Error: Missing "query" parameter. Please provide a valid SPARQL query.'.encode('utf-8'))
            return

        # Fetch data from Wikidata
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
        headers = {'Accept': 'application/sparql-results+json'}
        params = {'query': query}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Convert results to a markdown table
            results = data['results']['bindings']
            if results:
                keys = results[0].keys()
                markdown_table = '| ' + ' | '.join(keys) + ' |\n| ' + ' | '.join(['---']*len(keys)) + ' |\n'
                for result in results:
                    markdown_table += '| ' + ' | '.join([result[key]['value'] for key in keys]) + ' |\n'
            else:
                markdown_table = "No results found."

        except requests.exceptions.HTTPError as e:
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
