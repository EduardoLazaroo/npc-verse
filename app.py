from flask import Flask, render_template
from models.npcverse_model import get_all_npcs
from routes.npcverse_routes import npcverse_bp
from services.qdrant_service import init_qdrant

from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    # Usar CORS aberto para o frontend local ou nenhum CORS se tudo for servido do mesmo domínio
    CORS(app)
    app.register_blueprint(npcverse_bp)

    # init_qdrant() is opcional em startup; será tentado sob demanda nas funções Qdrant

    @app.route('/')
    def index():
        npcs = get_all_npcs()
        return render_template('index.html', npcs=npcs)

    @app.route('/npcs', methods=['GET'])
    def get_npcs():
        npcs = get_all_npcs()
        return npcs  # dict/list vira JSON automaticamente

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
