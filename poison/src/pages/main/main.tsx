import React from 'react';
import {useGlobalContext} from '../../global_context';
import styled from 'styled-components';
import {CreatePlayerOverlay} from '../../components/create_player_overlay';
import {Link} from 'react-router-dom';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  vertical-align: middle;
`;

const Centered = styled.div`
  margin-left: auto;
  margin-right: auto;
  margin-top: 30vh;
`;

const ButtonBox = styled.div`
  display: flex;
  flex-direction: row;
  margin-left: auto;
  margin-right: auto;
`;

const ButtonContainer = styled.div`
  border-radius: 5px;
  background-color: ${(props: {color: string}) => props.color};
  border: 1px solid black;
  display: flex;
  justify-content: center;
  vertical-align: middle;
  margin: 16px;
`;

const ButtonText = styled.h2`
  color: white;
  font-weight: bold;
  margin: 12px;
  font-size: 32pt;
`;

const Header = styled.h1`
  color: #ededed;
  text-style: italic;
  text-align: center;
  font-size: 46pt;
`;

const Name = styled.span`
  color: #12ddcd;
`;

type ButtonProps = {
  color: string;
  text: string;
  url: string;
};

const Button: React.FC<ButtonProps> = ({color, text, url}) => {
  return (
    <Link to={url} style={{textDecoration: 'none'}}>
      <ButtonContainer color={color}>
        <ButtonText>{text}</ButtonText>
      </ButtonContainer>
    </Link>
  );
};

export const MainPage: React.FC = (props) => {
  const {player, setPlayer} = useGlobalContext();

  return (
    <Container>
      <Centered>
        <Header>Playing as <Name>{player ? player.name : '...'}</Name></Header>
        {player && (
          <ButtonBox>
            <Button text='Create Game' color='#12cd12' url='/'/>
            <Button text='Join Game' color='#cd1212' url='/'/>
          </ButtonBox>
        )}
        {!player && <CreatePlayerOverlay onCreate={setPlayer}/>}
      </Centered>
    </Container>
  );
};
