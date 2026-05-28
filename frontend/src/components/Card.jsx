import React from 'react';
import './Card.css';

export const Card = ({ children, className = '', title }) => {
  return (
    <div className={`card-container ${className}`}>
      {title && <div className="card-header"><h3 className="card-title">{title}</h3></div>}
      <div className="card-content">
        {children}
      </div>
    </div>
  );
};
