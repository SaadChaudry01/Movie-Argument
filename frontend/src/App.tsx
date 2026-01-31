import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ComparePage from './pages/ComparePage'
import MoviePage from './pages/MoviePage'
import TrendingPage from './pages/TrendingPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/movie/:id" element={<MoviePage />} />
        <Route path="/trending" element={<TrendingPage />} />
      </Routes>
    </Layout>
  )
}

export default App
