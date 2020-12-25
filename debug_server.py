import uvicorn
import chess.pgn
# Importing app here makes the syntax cleaner as it will be picked up by refactors
from app.main import app

assert isinstance(app, object)
if __name__ == "__main__":
    uvicorn.run("debug_server:app", host="0.0.0.0", port=8000, reload=True)
    # with open("pgn/test.pgn") as file:
    #     game = chess.pgn.read_game(file)
    #     print(game)
