import React from 'react';
import {BrowserRouter, Routes, Route} from "react-router-dom";
import {GlobalContextProvider} from './global_context';
import {MainPage} from './pages/main/main';

export const Poison: React.FC = (props) => {
  return (
    <GlobalContextProvider>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<MainPage/>}/>
        </Routes>
      </BrowserRouter>
    </GlobalContextProvider>
  );
}
