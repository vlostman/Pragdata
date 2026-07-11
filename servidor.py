import http.server
import json
import os
import socketserver
import traceback

PORT = 8000
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pragdata.json')

class PragdataHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        print(f'📨 POST recibido: {self.path}')
        if self.path == '/guardar':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                print(f'📏 Content-Length: {content_length}')
                
                if content_length == 0:
                    print('⚠️ Petición vacía (Content-Length: 0)')
                    self.send_error(400, "Petición vacía")
                    return
                
                post_data = self.rfile.read(content_length)
                print(f'📦 Datos recibidos: {len(post_data)} bytes')
                
                data = json.loads(post_data)
                print(f'📋 Nodos a guardar: {len(data)}')
                
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f'✅ Guardados {len(data)} nodos en {DATA_FILE}')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'count': len(data)}).encode())
                
            except json.JSONDecodeError as e:
                print(f'❌ Error JSON: {e}')
                self.send_error(400, f"JSON inválido: {e}")
            except Exception as e:
                print(f'❌ Error interno: {e}')
                traceback.print_exc()
                self.send_error(500, str(e))
        else:
            print(f'⚠️ Ruta POST no manejada: {self.path}')
            super().do_POST()

    def do_GET(self):
        if self.path == '/cargar':
            try:
                if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            data = json.loads(content)
                        else:
                            data = []
                    print(f'📂 Cargados {len(data)} nodos')
                else:
                    data = []
                    print('📂 Archivo no existe o vacío')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                print(f'❌ Error al cargar: {e}')
                traceback.print_exc()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps([]).encode())
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        # Suprimir logs de archivos estáticos para no saturar
        if '/cargar' in str(args) or '/guardar' in str(args):
            super().log_message(format, *args)

if __name__ == '__main__':
    print(f'🚀 Pragdata Server iniciado en http://localhost:{PORT}')
    print(f'📁 Archivo de datos: {DATA_FILE}')
    
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print(f'📄 Archivo creado: {DATA_FILE}')
    else:
        print(f'📄 Archivo existente: {os.path.getsize(DATA_FILE)} bytes')
    
    with socketserver.TCPServer(("", PORT), PragdataHandler) as httpd:
        try:
            print(f'✅ Servidor listo. Abre http://localhost:{PORT}')
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n👋 Servidor detenido')