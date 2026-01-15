import http.server
import socketserver
import json
import os
import shutil
import time

# Configuration
PORT = 8000
ALLOWED_FILES = {
    '/save-requirements': 'data/pay_PizzaStatusRequirements.json',
    '/save-cert-types': 'data/pay_CertTypes.json',
    '/save-status-types': 'data/pay_StatusTypes.json'
}

class LifecycleRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests to save data"""
        if self.path in ALLOWED_FILES:
            try:
                # Get content length
                content_length = int(self.headers['Content-Length'])
                # Read POST data
                post_data = self.rfile.read(content_length)
                
                # Verify JSON
                data = json.loads(post_data)
                
                # Resolve target path
                relative_path = ALLOWED_FILES[self.path]
                
                # Check relative to cwd
                target_path = relative_path
                if not os.path.exists(os.path.dirname(target_path)):
                    # Try one level up (if running from tools/)
                    alt_path = os.path.join('..', relative_path)
                    if os.path.exists(os.path.dirname(alt_path)):
                        target_path = alt_path
                    else:
                        raise FileNotFoundError(f"Could not find data directory for {relative_path}. Checked current and parent directories.")
                
                # Normalize and get absolute path
                target_path = os.path.normpath(target_path)
                abs_path = os.path.abspath(target_path)
                print(f"Writing to: {abs_path}")
                
                # Create backup
                if os.path.exists(target_path):
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    backup_dir = os.path.join(os.path.dirname(target_path), 'backups')
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                    
                    filename = os.path.basename(target_path)
                    backup_filename = f"{os.path.splitext(filename)[0]}.{timestamp}.json"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    shutil.copy2(target_path, backup_path)
                    print(f"Backup created at: {backup_path}")

                # Write file
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4) 

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'success', 
                    'message': f'Changes saved to {os.path.basename(abs_path)}! (Backup created)'
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
print("💾 Writes enabled for:")
for endpoint, filepath in ALLOWED_FILES.items():
    print(f"   - {endpoint} -> {filepath}")

# Reuse address to prevent 'address already in use' errors on quick restarts
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), LifecycleRequestHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopping...")
        httpd.server_close()
