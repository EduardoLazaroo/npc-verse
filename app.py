from flask import Flask
from models.npcverse_model import get_all_npcs
from routes.npcverse_routes import npcverse_bp
from services.qdrant_service import init_qdrant

from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
    app.register_blueprint(npcverse_bp)

    init_qdrant()

    @app.route('/npcs', methods=['GET'])
    def get_npcs():
        npcs = get_all_npcs()
        return npcs  # Se já retorna dict/list, Flask converte para JSON automaticamente

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
