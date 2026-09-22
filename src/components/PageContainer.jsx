import React from 'react';

export default function PageContainer({
  children,
  title,
  subtitle,
  badge,
  action,
  className = '',
  containerClassName = 'max-w-7xl',
}) {
  return (
    <div className={`min-h-[calc(100vh-4rem)] py-8 sm:py-12 ${className}`}>
      <div className={`${containerClassName} mx-auto px-4 sm:px-6 lg:px-8`}>
        {(title || subtitle || badge || action) && (
          <div className="mb-8 sm:mb-12 pb-6 border-b border-slate-200/80 flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div className="max-w-3xl">
              {badge && (
                <div className="mb-3">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                    {badge}
                  </span>
                </div>
              )}
              {title && (
                <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                  {title}
                </h1>
              )}
              {subtitle && (
                <p className="mt-3 text-base sm:text-lg text-slate-600 leading-relaxed">
                  {subtitle}
                </p>
              )}
            </div>
            {action && <div className="shrink-0">{action}</div>}
          </div>
        )}
        {children}
      </div>
    </div>
  );
}
