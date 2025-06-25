from flask import Flask, render_template
from models.npcverse_model import get_all_npcs
from routes.npcverse_routes import npcverse_bp
from services.qdrant_service import init_qdrant


def create_app():
    app = Flask(__name__)
    app.register_blueprint(npcverse_bp)

    init_qdrant()

    @app.route('/')
    def index():
        npcs = get_all_npcs()
        return render_template('index.html', npcs=npcs)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
