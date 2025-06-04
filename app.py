from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from routes.npc_routes import npc_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

# Registra as rotas
app.register_blueprint(npc_bp)

@app.route('/')
def index():
    from services.db_service import get_all_npcs
    npcs = get_all_npcs()
    return render_template("index.html", npcs=npcs)

if __name__ == '__main__':
    app.run(debug=True)
