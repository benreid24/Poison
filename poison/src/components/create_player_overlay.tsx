import React from 'react';
import {Player} from '../lib/types';
import {createPlayer} from '../lib/api';
import {Popup} from './popup';

export type CreatePlayerOverlayProps = {
  onCreate: (player: Player) => void;
};

export const CreatePlayerOverlay: React.FC<CreatePlayerOverlayProps> = ({onCreate}) => {
  const [name, setName] = React.useState<string>('');
  const [error, setError] = React.useState<string>('');

  const onSubmit = async () => {
    if (name.length >= 3) {
      const p = await createPlayer(name);
      if (p) {
        onCreate(p);
      }
      else {
        setError('Failed to create user');
      }
    }
    else {
      setError('Name is too short');
    }
  };

  return (
    <Popup>
      <h1 className='modal_header'>What's your name?</h1>
      <input type='text' value={name} onChange={event => setName(event.target.value)}/>
      {error.length > 0 && <p className='error'>{error}</p>}
      <input type='submit' onClick={onSubmit}/>
    </Popup>
  );
};
