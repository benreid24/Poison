import React from 'react';
import {getPlayer, savePlayer} from './lib/api';
import {Player} from './lib/types';

export type GlobalContextValue = {
  player: Player | null;
  setPlayer: (player: Player) => void;
};

export const GlobalContext = React.createContext<GlobalContextValue | null>(null);

export const GlobalContextProvider: React.FC = ({children}) => {
  const [player, setPlayerValue] = React.useState<Player | null>(getPlayer());

  const setPlayer = React.useCallback((player: Player) => {
    savePlayer(player);
    setPlayerValue(player);
  }, [setPlayerValue, savePlayer]);

  const contextValue = React.useMemo<GlobalContextValue>(
    () => ({
      player,
      setPlayer
    }),
    [
      player,
      setPlayer
    ]
  );

  return <GlobalContext.Provider value={contextValue}>{children}</GlobalContext.Provider>;
};

export const useGlobalContext = () => {
  const ctx = React.useContext(GlobalContext);
  if (!ctx) {
    throw new Error('useGlobalContext() must be used within a GlobalContextProvider');
  }
  return ctx;
};
