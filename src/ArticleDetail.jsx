import React from 'react';
import { useParams, Link } from 'react-router-dom';

function ArticleDetail({ articles, darkMode, toggleDarkMode }) {
  const { id } = useParams();
  const article = articles[id];

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
      ? 'bg-gray-800/50 backdrop-blur-sm border border-gray-700/50' 
      : 'bg-white/80 backdrop-blur-sm border border-gray-200/50 shadow-sm',
    
    accent: darkMode ? 'text-blue-400' : 'text-blue-600',
    accentHover: darkMode ? 'hover:text-blue-300' : 'hover:text-blue-700',
    
    button: darkMode 
      ? 'bg-blue-600 hover:bg-blue-700 text-white' 
      : 'bg-blue-500 hover:bg-blue-600 text-white'
  };

  if (!article) {
    return (
      <div className={`min-h-screen ${themeClasses.background}`}>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className={`animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 mx-auto mb-4 ${
              darkMode ? 'border-blue-400' : 'border-blue-600'
            }`}></div>
            <p className={`text-lg ${themeClasses.text.secondary}`}>
              Loading article or article not found...
            </p>
            <Link 
              to="/" 
              className={`inline-block mt-4 ${themeClasses.accent} ${themeClasses.accentHover} transition-colors`}
            >
              ← Back to homepage
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${themeClasses.background}`}>
      {/* Header */}
      <header className={`${themeClasses.header} sticky top-0 z-50`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">🗞️</span>
              </div>
              <Link to="/" className={`text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent hover:opacity-80 transition-opacity`}>
                Unbiased Updates
              </Link>
            </div>
            
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
      </header>

      {/* Article Content - Fixed spacing */}
      <main className="max-w-4xl mx-auto px-6 py-8 safe-top">
        {/* Back Button */}
        <div className="mb-8">
          <Link 
            to="/" 
            className={`inline-flex items-center space-x-2 ${themeClasses.accent} ${themeClasses.accentHover} transition-colors font-medium`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back to homepage</span>
          </Link>
        </div>

        {/* Article Header */}
        <article className={`${themeClasses.card} rounded-2xl overflow-hidden`}>
          {/* Article Image */}
          <div className="relative">
            {article.thumbnail && (
              <img
                src={article.thumbnail}
                alt={article.title}
                className="w-full h-64 md:h-80 object-cover"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&h=400&fit=crop&crop=center';
                }}
              />
            )}
            {article.category && (
              <div className={`absolute top-6 left-6 ${getCategoryColor(article.category)} text-white px-4 py-2 rounded-full text-sm font-medium`}>
                {article.category}
              </div>
            )}
          </div>

          {/* Article Content */}
          <div className="p-8">
            {/* Title */}
            <h1 className={`text-3xl md:text-4xl font-bold ${themeClasses.text.primary} mb-6 leading-tight`}>
              {article.title}
            </h1>

            {/* Meta Information */}
            <div className={`flex flex-wrap items-center gap-6 ${themeClasses.text.muted} text-sm mb-8 pb-6 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <time>
                  {new Date(article.publisheddate).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </time>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>5 min read</span>
              </div>
            </div>

            {/* Summary */}
            {article.summary && (
              <div className="mb-8">
                <h2 className={`text-xl font-semibold ${themeClasses.text.primary} mb-4 flex items-center space-x-2`}>
                  <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Summary</span>
                </h2>
                <div className={`text-lg leading-relaxed ${themeClasses.text.secondary} space-y-4`}>
                  {article.summary.split('\n').map((paragraph, idx) => (
                    <p key={idx}>{paragraph}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Insights Section */}
            {article.insights && (
              <div className="mb-8">
                <h2 className={`text-2xl font-bold ${themeClasses.text.primary} mb-6 flex items-center space-x-2`}>
                  <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span>Key Insights</span>
                </h2>
                
                <div className="space-y-4">
                  {article.insights
                    .split(/(?<=[.?!])\s+/)
                    .filter(sentence => sentence.trim() !== "")
                    .map((sentence, idx) => {
                      const formatted = sentence.charAt(0).toUpperCase() + sentence.slice(1).trim();
                      return (
                        <p key={idx} className={`text-lg leading-relaxed ${themeClasses.text.secondary} pl-4 border-l-4 border-blue-500/30`}>
                          {formatted}
                        </p>
                      );
                    })}
                </div>
              </div>
            )}

            {/* Call to Action */}
            <div className={`mt-12 p-6 rounded-xl ${darkMode ? 'bg-gray-700/30' : 'bg-blue-50/50'} border ${darkMode ? 'border-gray-600' : 'border-blue-100'}`}>
              <h3 className={`text-lg font-semibold ${themeClasses.text.primary} mb-3`}>
                Want to read the full story?
              </h3>
              <p className={`${themeClasses.text.secondary} mb-4`}>
                Get the complete details and original reporting from the source.
              </p>
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`inline-flex items-center space-x-2 px-6 py-3 ${themeClasses.button} rounded-lg transition-colors font-medium`}
              >
                <span>Read Original Article</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </article>

        {/* Related Articles Section */}
        <div className="mt-12">
          <Link 
            to="/" 
            className={`inline-flex items-center space-x-2 ${themeClasses.button} px-6 py-3 rounded-lg transition-colors font-medium`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Browse More Articles</span>
          </Link>
        </div>
      </main>
    </div>
  );
}

export default ArticleDetail;