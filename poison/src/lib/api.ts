import {Player} from './types';

const sendRequest = async(endpoint: string, body: any): Promise<Response> => {
  return fetch(`/poison/${endpoint}`, {
    method: 'post',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
};

export const getPlayer = (): Player|null => {
  const p = localStorage.getItem('player');
  if (!p) return null;
  return JSON.parse(p) as Player;
};

export const savePlayer = (player: Player) => {
  localStorage.setItem('player', JSON.stringify(player));
};

export const createPlayer = async(name: string): Promise<Player|null> => {
  const r = await sendRequest('create_player', {name: name});
  if (!r.ok) return null;
  const d = await r.json();
  return {
    name: name,
    key: d.id
  };
};
