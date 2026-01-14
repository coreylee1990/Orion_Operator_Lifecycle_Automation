import http.server
import socketserver
import json
import os
import shutil
import time

# Configuration
PORT = 8000
DATA_FILE_PATH = 'data/pay_PizzaStatusRequirements.json'

class LifecycleRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests to save data"""
        if self.path == '/save-requirements':
            try:
                # Get content length
                content_length = int(self.headers['Content-Length'])
                # Read POST data
                post_data = self.rfile.read(content_length)
                
                # Verify JSON
                data = json.loads(post_data)
                
                # Check if we are in the right directory
                target_path = DATA_FILE_PATH
                if not os.path.exists('data') and os.path.exists('../data'):
                    target_path = '../' + DATA_FILE_PATH
                
                # Create backup
                if os.path.exists(target_path):
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    backup_dir = os.path.dirname(target_path) + '/backups'
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                    
                    backup_path = f"{backup_dir}/pay_PizzaStatusRequirements.{timestamp}.json"
                    shutil.copy2(target_path, backup_path)
                    print(f"Backup created at: {backup_path}")

                # Write file
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4) # Indent 4 match existing style usually

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'success', 
                    'message': 'Changes saved directly to disk! (Backup created)'
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"Error saving file: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            # Fallback to standard handler for other paths (not allowed for POST usually)
            self.send_error(404)

print(f"🚀 Starting Operator Lifecycle Server on port {PORT}...")
print(f"📂 serving files from: {os.getcwd()}")
print(f"💾 Writes enabled for: {DATA_FILE_PATH}")

# Reuse address to prevent 'address already in use' errors on quick restarts
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), LifecycleRequestHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopping...")
        httpd.server_close()
