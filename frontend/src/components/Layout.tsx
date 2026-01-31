import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Film, TrendingUp, GitCompare, Sparkles } from 'lucide-react';
import clsx from 'clsx';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Home', icon: Film },
    { path: '/compare', label: 'Compare', icon: GitCompare },
    { path: '/trending', label: 'Trending', icon: TrendingUp },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-dark-900 border-b border-dark-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 group">
              <div className="bg-primary-500 p-2 rounded-lg group-hover:bg-primary-400 transition-colors">
                <Sparkles className="w-5 h-5 text-dark-950" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">Movie Argument Engine</h1>
                <p className="text-xs text-gray-500 hidden sm:block">AI-Powered Movie Analysis</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center gap-1">
              {navItems.map(({ path, label, icon: Icon }) => (
                <Link
                  key={path}
                  to={path}
                  className={clsx(
                    'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all',
                    location.pathname === path
                      ? 'bg-primary-500/10 text-primary-500'
                      : 'text-gray-400 hover:text-white hover:bg-dark-800'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-dark-900 border-t border-dark-700 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-gray-500 text-sm">
              Movie Argument Engine - End-to-End Data Science Project
            </p>
            <p className="text-gray-600 text-xs">
              Data powered by TMDB
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
