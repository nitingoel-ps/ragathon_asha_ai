import { ThemeProvider } from 'styled-components'
import theme from './styles/theme'
import GlobalStyles from './styles/globalStyles'
import HealthEngagementPage from './components/HealthEngagementPage/HealthEngagementPage'


function App() {

  return (

    <ThemeProvider theme={theme}>
      <GlobalStyles />
      <HealthEngagementPage />
    </ThemeProvider>
  )
}

export default App
