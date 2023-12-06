import CONSTANTS from 'constants.js';
import Tile from './tile'; // Assuming the Tile component is in the same directory

export default function Board({ player, board, win, position2path }) {
  const getTiles = () => {
    const tiles = [];
    board.forEach((value, position) => {
      tiles.push(
        <Tile
          key={`tile_${position}`}
          player={player}
          piece={value}
          win={win}
          position2path={position2path}
        />
      );
    });

    return tiles;
  };

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(8, 1fr)',
        gap: '0px',
        width: '250px',
      }}
    >
      {getTiles()}
    </div>
  );
}
