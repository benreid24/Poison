import React from 'react';
import styled from 'styled-components';

const Cover = styled.div`
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 10000;
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  vertical-align: middle;
`;

const Modal = styled.div`
  background-color: lightskyblue;
  border-radius: 5px;
  border: 1px solid blue;
  display: flex;
  justify-content: center;
  vertical-align: middle;
  flex-direction: column;
  margin-top: auto;
  margin-bottom: auto;
  padding: 16px;
`;

export const Popup: React.FC = ({children}) => {
  return (
    <Cover>
      <Modal>
        {children}
      </Modal>
    </Cover>
  );
};
