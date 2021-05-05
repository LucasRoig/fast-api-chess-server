from typing import cast, List, Dict

from chess import pgn, square_name

from app.models.domain.serializable_game import SerializableGame, SerializablePosition, Move
from io import StringIO, BytesIO, TextIOWrapper


def parse_pgn(pgn_content: bytes) -> SerializableGame:
    game: pgn.Game = cast(pgn.Game, pgn.read_game(TextIOWrapper(BytesIO(pgn_content))))
    return pgn_game_to_serializable_game(game)


def pgn_game_to_serializable_game(pgn_game: pgn.Game) -> SerializableGame:
    current_index = 1
    all_positions: List[SerializablePosition] = []

    def parse_position(pgn_position: pgn.ChildNode, is_mainline: bool) -> SerializablePosition:
        nonlocal current_index
        nonlocal all_positions
        index = current_index
        current_index += 1
        next_pos_index = None
        if pgn_position.variations:
            next_pos_index = parse_position(pgn_position.variations[0], True).index
        variations_indexes = []
        if len(pgn_position.variations) > 1:
            variations_indexes = [
                parse_position(p, False).index
                for i, p in enumerate(pgn_position.variations)
                if i > 0
            ]
        position = SerializablePosition(
            index=index,
            next_position_index=next_pos_index,
            variations_indexes=variations_indexes,
            nags=list(pgn_position.nags),
            fen=pgn_position.board().fen(),
            comment=pgn_position.comment,
            commentBefore=pgn_position.starting_comment,
            san=pgn_position.san(),
            is_mainline=is_mainline,
            move=Move(
                from_square=square_name(pgn_position.move.from_square),
                to=square_name(pgn_position.move.to_square),
                promotion=pgn_position.move.promotion
            )
        )
        all_positions.insert(0, position)
        return position
    first_pos = SerializablePosition(
        index=0,
        fen=pgn_game.board().fen(),
        is_mainline=True,
        nags=[],
        san="",
        variations_indexes=[],
        next_position_index=1
    )
    all_positions.append(first_pos)
    for i, position in enumerate(pgn_game.variations):
        if i != 0:
            first_pos.variations_indexes.append(current_index)
        parse_position(position, i == 0)
    headers: Dict[str, str] = {}
    for key in pgn_game.headers.keys():
        headers[key] = pgn_game.headers[key]
    game = SerializableGame(
        headers=headers,
        comment=pgn_game.starting_comment,
        positions=all_positions,
    )
    return game
