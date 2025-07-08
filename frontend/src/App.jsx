import React, { useEffect, useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ArticleDetail from './ArticleDetail';

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(true); // Default to dark mode

  useEffect(() => {
    fetch('https://api.unbiasedupdates.com/articles/recent')
      .then(res => res.json())
      .then(data => {
        const sorted = [...data].sort((a, b) =>
          new Date(b.publisheddate) - new Date(a.publisheddate)
        );
        setArticles(sorted);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch articles:', err);
        setLoading(false);
      });
  }, []);

  // Load theme preference from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme !== null) {
      setDarkMode(JSON.parse(savedTheme));
    }
  }, []);

  // Save theme preference to localStorage
  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', JSON.stringify(newDarkMode));
  };

  const getCategoryColor = (category) => {
    const colors = {
      Environment: darkMode ? 'bg-emerald-600' : 'bg-emerald-500',
      Technology: darkMode ? 'bg-blue-600' : 'bg-blue-500',
      Finance: darkMode ? 'bg-amber-600' : 'bg-amber-500',
      Science: darkMode ? 'bg-violet-600' : 'bg-violet-500',
      Health: darkMode ? 'bg-rose-600' : 'bg-rose-500',
      Culture: darkMode ? 'bg-pink-600' : 'bg-pink-500',
      Politics: darkMode ? 'bg-indigo-600' : 'bg-indigo-500',
      Sports: darkMode ? 'bg-orange-600' : 'bg-orange-500',
      World: darkMode ? 'bg-teal-600' : 'bg-teal-500',
      Business: darkMode ? 'bg-cyan-600' : 'bg-cyan-500'
    };
    return colors[category] || (darkMode ? 'bg-gray-600' : 'bg-gray-500');
  };

  const LoadingScreen = () => (
    <div className={`min-h-screen flex items-center justify-center ${
      darkMode 
        ? 'bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900' 
        : 'bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50'
    }`}>
      <div className="text-center">
        <div className={`animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 mx-auto mb-4 ${
          darkMode ? 'border-blue-400' : 'border-blue-600'
        }`}></div>
        <p className={`text-lg ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
          Loading latest news...
        </p>
      </div>
    </div>
  );

  if (loading) {
    return <LoadingScreen />;
  }

  const themeClasses = {
    background: darkMode 
      ? 'bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900' 
      : 'bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50',
    
    header: darkMode 
      ? 'bg-black/20 backdrop-blur-sm border-b border-gray-700/50' 
      : 'bg-white/80 backdrop-blur-sm border-b border-gray-200/50 shadow-sm',
    
    text: {
      primary: darkMode ? 'text-white' : 'text-gray-900',
      secondary: darkMode ? 'text-gray-300' : 'text-gray-600',
      muted: darkMode ? 'text-gray-400' : 'text-gray-500'
    },
    
    card: darkMode 
      ? 'bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 hover:border-blue-500/50' 
      : 'bg-white/80 backdrop-blur-sm border border-gray-200/50 hover:border-blue-300/50 shadow-sm',
    
    accent: darkMode ? 'text-blue-400' : 'text-blue-600',
    accentHover: darkMode ? 'hover:text-blue-300' : 'hover:text-blue-700',
    
    button: darkMode 
      ? 'bg-blue-600 hover:bg-blue-700 text-white' 
      : 'bg-blue-500 hover:bg-blue-600 text-white',
    
    footer: darkMode 
      ? 'bg-black/20 backdrop-blur-sm border-t border-gray-700/50' 
      : 'bg-white/80 backdrop-blur-sm border-t border-gray-200/50'
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <div className={`min-h-screen ${themeClasses.background}`}>
              {/* Header */}
              <header className={`${themeClasses.header} sticky top-0 z-50`}>
                <div className="max-w-7xl mx-auto px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold">🗞️</span>
                      </div>
                      <h1 className={`text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent`}>
                        Unbiased Updates
                      </h1>
                    </div>
                    
                    <div className="flex items-center space-x-8">
                      <nav className="hidden md:flex space-x-8">
                        <a href="#" className={`${themeClasses.text.secondary} ${themeClasses.accentHover} transition-colors`}>Home</a>
                        <a href="#" className={`${themeClasses.text.secondary} ${themeClasses.accentHover} transition-colors`}>Latest</a>
                        <a href="#" className={`${themeClasses.text.secondary} ${themeClasses.accentHover} transition-colors`}>Categories</a>
                        <a href="#" className={`${themeClasses.text.secondary} ${themeClasses.accentHover} transition-colors`}>About</a>
                      </nav>
                      
                      {/* Theme Toggle Button */}
                      <button
                        onClick={toggleDarkMode}
                        className={`p-2 rounded-lg transition-all duration-200 ${
                          darkMode 
                            ? 'bg-gray-700 hover:bg-gray-600 text-yellow-400' 
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                        }`}
                        aria-label="Toggle theme"
                      >
                        {darkMode ? (
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M17.293 13.293A8 8 0 716.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </header>

              {/* Main Content */}
              <main className="max-w-7xl mx-auto px-6 py-8">
                {/* Hero Section */}
                <div className="text-center mb-12">
                  <h2 className={`text-4xl md:text-5xl font-bold ${themeClasses.text.primary} mb-4`}>
                    Stay <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">Informed</span>
                  </h2>
                  <p className={`text-lg max-w-2xl mx-auto ${themeClasses.text.secondary}`}>
                    Your trusted source for unbiased news and updates from around the world
                  </p>
                </div>

                {/* Articles Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {articles.map((article, index) => (
                    <Link
                      key={index}
                      to={`/article/${index}`}
                      className={`group ${themeClasses.card} rounded-2xl overflow-hidden transition-all duration-300 hover:scale-105 ${
                        darkMode 
                          ? 'hover:shadow-2xl hover:shadow-blue-500/20' 
                          : 'hover:shadow-2xl hover:shadow-blue-500/10'
                      } cursor-pointer`}
                      style={{ textDecoration: 'none' }}
                    >
                      <div className="relative overflow-hidden">
                        <img
                          src={article.thumbnail}
                          alt="Article thumbnail"
                          className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-500"
                          onError={(e) => {
                            e.target.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=300&fit=crop&crop=center';
                          }}
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        {article.category && (
                          <div className={`absolute top-4 left-4 ${getCategoryColor(article.category)} text-white px-3 py-1 rounded-full text-sm font-medium`}>
                            {article.category}
                          </div>
                        )}
                      </div>
                      
                      <div className="p-6">
                        <h3 className={`text-xl font-bold ${themeClasses.text.primary} mb-3 ${themeClasses.accentHover} transition-colors line-clamp-2`}>
                          {article.title}
                        </h3>
                        <p className={`${themeClasses.text.secondary} text-sm mb-4 line-clamp-3`}>
                          {article.summary && article.summary.length > 150 
                            ? article.summary.slice(0, 150) + '...' 
                            : article.summary}
                        </p>
                        <div className="flex items-center justify-between">
                          <time className={`${themeClasses.text.muted} text-sm`}>
                            {new Date(article.publisheddate).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            })}
                          </time>
                          <div className={`flex items-center ${themeClasses.accent} text-sm font-medium ${themeClasses.accentHover} transition-colors`}>
                            Read more
                            <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>

                {/* Empty State */}
                {articles.length === 0 && !loading && (
                  <div className="text-center py-12">
                    <div className={`${themeClasses.text.secondary} text-lg mb-4`}>No articles available</div>
                    <p className={themeClasses.text.muted}>Please check back later for updates</p>
                  </div>
                )}
              </main>

              {/* Footer */}
              <footer className={`${themeClasses.footer} mt-16`}>
                <div className="max-w-7xl mx-auto px-6 py-8">
                  <div className="text-center">
                    <p className={themeClasses.text.muted}>© 2024 Unbiased Updates. All rights reserved.</p>
                  </div>
                </div>
              </footer>
            </div>
          }
        />
        <Route
          path="/article/:id"
          element={<ArticleDetail articles={articles} darkMode={darkMode} toggleDarkMode={toggleDarkMode} />}
        />
      </Routes>
    </Router>
  );
}

export default App;