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
    background-color: ${(props) => props.theme.colors.background};
    line-height: ${(props) => props.theme.typography.lineHeight.base};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
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
    font-size: ${(props) => props.theme.typography.fontSize['4xl']};
  }
  
  h2 {
    font-size: ${(props) => props.theme.typography.fontSize['3xl']};
  }
  
  h3 {
    font-size: ${(props) => props.theme.typography.fontSize['2xl']};
  }
  
  h4 {
    font-size: ${(props) => props.theme.typography.fontSize.xl};
  }
  
  h5 {
    font-size: ${(props) => props.theme.typography.fontSize.lg};
  }
  
  h6 {
    font-size: ${(props) => props.theme.typography.fontSize.base};
  }
  
  p {
    margin-bottom: ${(props) => props.theme.spacing.md};
  }
`;

export default GlobalStyles;
