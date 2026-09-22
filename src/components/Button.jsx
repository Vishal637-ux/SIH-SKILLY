import React from 'react';
import { Link } from 'react-router-dom';

export default function Button({
  children,
  to,
  href,
  onClick,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  className = '',
  icon: Icon,
  iconPosition = 'left',
  fullWidth = false,
  loading = false,
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed rounded-xl';
  const widthStyle = fullWidth ? 'w-full' : '';

  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-sm hover:shadow active:scale-[0.98]',
    secondary: 'bg-blue-50 text-blue-700 hover:bg-blue-100 focus:ring-blue-400 border border-blue-200/80',
    outline: 'border border-slate-300 text-slate-700 hover:bg-slate-100 hover:text-slate-900 focus:ring-slate-400 bg-white shadow-sm',
    ghost: 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 focus:ring-slate-400',
    white: 'bg-white text-blue-700 hover:bg-slate-50 focus:ring-white shadow-sm border border-slate-200/80 active:scale-[0.98]',
    dark: 'bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-700 shadow-sm',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-6 py-3 text-base gap-2.5 font-semibold',
  };

  const combinedClasses = `${baseStyles} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${widthStyle} ${className}`;

  const renderIcon = (icon) => {
    if (!icon) return null;
    if (React.isValidElement(icon)) {
      return icon;
    }
    const IconComp = icon;
    return <IconComp className="w-4 h-4 shrink-0" />;
  };

  const content = (
    <>
      {loading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0" />
      ) : (
        iconPosition === 'left' && renderIcon(Icon)
      )}
      {children && <span>{children}</span>}
      {!loading && iconPosition === 'right' && renderIcon(Icon)}
    </>
  );

  if (to) {
    return (
      <Link to={to} className={combinedClasses} {...props}>
        {content}
      </Link>
    );
  }

  if (href) {
    return (
      <a href={href} className={combinedClasses} {...props}>
        {content}
      </a>
    );
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={combinedClasses}
      {...props}
    >
      {content}
    </button>
  );
}
