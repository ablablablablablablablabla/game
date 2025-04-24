from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
app = Flask(__name__)
DATABASE_URL = "sqlite:///game_data.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    cat_x = Column(Float, nullable=False)
    cat_y = Column(Float, nullable=False)
    time_added = Column(DateTime, default=datetime.utcnow)
    coins_collected = Column(Integer, default=0)

class Coin(Base):
    __tablename__ = 'coins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

@app.route('/api/update_player', methods=['POST'])
def update_player():
    data = request.json
    if not all([data.get(k) is not None for k in ['name', 'cat_x', 'cat_y', 'coins_collected']]):
        return jsonify({"error": "Missing fields"}), 400
    player = session.query(Player).filter_by(name=data['name']).first()
    if player:
        player.cat_x, player.cat_y, player.coins_collected = data['cat_x'], data['cat_y'], data['coins_collected']
    else:
        session.add(Player(**data))
    session.commit()
    return jsonify({"message": "Updated"}), 200

@app.route('/api/get_game_state', methods=['GET'])
def get_game_state():
    players = [{"name": p.name, "cat_x": p.cat_x, "cat_y": p.cat_y, "coins_collected": p.coins_collected} for p in session.query(Player).all()]
    coins = [{"x": c.x, "y": c.y} for c in session.query(Coin).all()]
    return jsonify({"players": players, "coins": coins}), 200

@app.route('/api/update_coins', methods=['POST'])
def update_coins():
    data = request.json
    if not isinstance(data.get("coins"), list) or not all(0 <= c["x"] < 32 and 0 <= c["y"] < 32 for c in data["coins"]):
        return jsonify({"error": "Invalid data"}), 400
    session.query(Coin).delete()
    session.add_all([Coin(x=c["x"], y=c["y"]) for c in data["coins"]])
    session.commit()
    return jsonify({"message": "Coins updated"}), 200

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    players = [{"name": p.name, "time_added": p.time_added.strftime("%Y-%m-%d %H:%M:%S"), "duration": (datetime.utcnow() - p.time_added).total_seconds(), "coins_collected": p.coins_collected} for p in session.query(Player).order_by(Player.coins_collected.desc()).all()]
    return render_template('leaderboard.html', leaderboard=players)

@app.route('/about', methods=['GET'])
def about():
    experience = "Я — эксперт в области ИИ с опытом более 5 лет."
    return render_template('about.html', experience=experience)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True)