import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  /* CSS Reset */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  html, body {
    font-family: ${(props) => props.theme.typography.fontFamily.primary};
    font-size: ${(props) => props.theme.typography.fontSize.base};
    color: ${(props) => props.theme.colors.text.primary};
    background-color: ${(props) => props.theme.colors.backgroundSecondary};
    line-height: ${(props) => props.theme.typography.lineHeight.base};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    
  }

  #root{
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    max-height: 100vh;
  }
  
  a {
    color: ${(props) => props.theme.colors.primary};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  button, input, textarea, select {
    font-family: inherit;
    font-size: inherit;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-bottom: ${(props) => props.theme.spacing.md};
    font-weight: ${(props) => props.theme.typography.fontWeight.bold};
    line-height: ${(props) => props.theme.typography.lineHeight.tight};
  }
  
  h1 {
    font-size: ${(props) => props.theme.typography.fontSize['3xl']};
  }
  
  h2 {
    font-size: ${(props) => props.theme.typography.fontSize['4xl']};
    font-weight: ${(props) => props.theme.typography.fontWeight.medium};
  }
  
  h3 {
    font-size: ${(props) => props.theme.typography.fontSize.xl};
    font-weight: ${(props) => props.theme.typography.fontWeight.medium};
    
  }
  
  h4 {
    font-size: ${(props) => props.theme.typography.fontSize.lg};
  }
  
  h5 {
    font-size: ${(props) => props.theme.typography.fontSize.base};
  }
  
  h6 {
    font-size: ${(props) => props.theme.typography.fontSize.base};
  }
  
  p {
    font-size: ${(props) => props.theme.typography.fontSize.base};
    margin-bottom: ${(props) => props.theme.spacing.md};
  }
`;

export default GlobalStyles;
