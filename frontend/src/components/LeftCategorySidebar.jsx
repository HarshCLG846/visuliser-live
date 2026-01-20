import React from 'react'
import './LeftCategorySidebar.css'

const categoryData = {
  Trim: ['Ridge Cap', 'J Channel', 'Rake & Corner', 'Corner Trim'],
  Roofing: ['Leakguard Panel', 'Legacy Panel', 'Classic Panel', 'Standing Seam'],
  Siding: ['Board & Batten', 'Traditional Panel', 'Classic Panel', 'Concealed Fastener Board & Batten'],
  Accessories: ['Gutters', 'Downspouts', 'Vents', 'Chimney Caps', 'Skylights']
}

export { categoryData }

function LeftCategorySidebar({ activeCategory, onCategoryChange }) {
  const handleCategoryClick = (category) => {
    onCategoryChange(category)
  }

  return (
    <div className="left-category-sidebar">
      <div className="sidebar-header">
        <h3>Categories</h3>
      </div>
      <div className="sidebar-content">
        <div className="category-list">
          {Object.keys(categoryData).map((category) => {
            const isActive = activeCategory === category
            const icons = {
              Trim: '📐',
              Roofing: '🏠',
              Siding: '🧱',
              Accessories: '🔧'
            }

            return (
              <button
                key={category}
                className={`category-item ${isActive ? 'active' : ''}`}
                onClick={() => handleCategoryClick(category)}
              >
                <span className="category-icon">{icons[category]}</span>
                <div className="category-text-stack">
                  <span className="category-name">{category}</span>
                  <span className="category-subtitle">
                    {{
                      Trim: 'Edges & details',
                      Roofing: 'Panels & colors',
                      Siding: 'Walls & texture',
                      Accessories: 'Gutters & vents'
                    }[category]}
                  </span>
                </div>

                {/* Optional Arrow if needed, but icon is cleaner */}
              </button>
            )
          })}
        </div>
      </div>
    </div >
  )
}

export default LeftCategorySidebar

